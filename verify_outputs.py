"""Kiểm tra sản phẩm thực: notebook, PDF, biểu đồ và số liệu xuất ra."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
if (ROOT / '.packages').exists():
    sys.path.insert(0, str(ROOT / '.packages'))
import nbformat
import pymupdf as fitz
import numpy as np
import pandas as pd


def main():
    out = ROOT / 'outputs'
    s = json.loads((out / 'tables/metrics.json').read_text(encoding='utf-8'))
    nb = nbformat.read(ROOT / 'visual_analytics.ipynb', as_version=4)
    nbformat.validate(nb)
    code = [c for c in nb.cells if c.cell_type == 'code']
    assert all(c.execution_count is not None for c in code), 'Notebook chưa chạy hết.'
    assert not any(o.output_type == 'error' for c in code for o in c.outputs)
    assert sum(o.output_type == 'display_data' and 'image/png' in o.get('data', {})
               for c in code for o in c.outputs) >= 6
    pdf = fitz.open(out / 'bao_cao_visual_analytics.pdf')
    assert len(pdf) == 10, f'PDF có {len(pdf)} trang, dự kiến 10.'
    text = '\n'.join(p.get_text() for p in pdf)
    assert 'Doanh thu tập trung ở đâu?' in text
    assert 'Hành động' in text and '\ufffd' not in text
    assert all(len(pdf[i].get_images()) >= 1 for i in range(3, 9))
    assert f'{s["sales"]:,.2f}' in text
    assert f'{s["cancellation"]:,.2f}' in text
    # Không có text chạy ra ngoài mép trang.
    for page in pdf:
        for block in page.get_text('dict')['blocks']:
            if block['type'] == 0:
                x0, y0, x1, y1 = block['bbox']
                assert x0 >= 0 and y0 >= 0 and x1 <= page.rect.width + 1 and y1 <= page.rect.height + 1
    orders = pd.read_csv(out / 'tables/orders.csv')
    assert orders.InvoiceNo.is_unique
    assert np.isclose(orders.OrderValue.sum(), s['sales'])
    assert s['sale_rows'] + s['cancel_rows'] + s['other_rows'] == s['raw_rows']
    preview = out / 'preview'
    preview.mkdir(exist_ok=True)
    for n in [0, 2, 3, 5, 8, 9]:
        pdf[n].get_pixmap(matrix=fitz.Matrix(1.1, 1.1)).save(preview / f'page_{n+1:02}.png')
    report = {'status': 'PASS', 'pdf_pages': len(pdf), 'executed_code_cells': len(code),
              'figures': 6, 'raw_rows': s['raw_rows'], 'sales': s['sales'],
              'checks': ['notebook executed without errors', '6 embedded notebook figures',
                         '10 PDF pages with Vietnamese text', 'figures on pages 4–9',
                         'PDF metrics match exported tables', 'no text outside page bounds',
                         'unique orders and sales reconciliation', 'row partition reconciliation']}
    (out / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()

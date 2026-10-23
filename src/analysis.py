"""Đọc dữ liệu gốc, kiểm tra chất lượng, tổng hợp và vẽ sáu loại biểu đồ.

Mỗi hàm được gọi độc lập trong notebook để người mới có thể học từng bước.
"""
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

SOURCE = 'https://archive.ics.uci.edu/dataset/352/online-retail'
DOWNLOAD = 'https://archive.ics.uci.edu/static/public/352/online+retail.zip'
BLUE, RED, GRAY = '#176B87', '#C65543', '#A8B4BE'


def load_data(root):
    """Chỉ tải nếu chưa có Excel. Các lần chạy sau không cần mạng."""
    root = Path(root)
    raw_dir = root / 'data/raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / 'Online Retail.xlsx'
    if not path.exists():
        archive = raw_dir / 'online_retail.zip'
        if not archive.exists():
            urllib.request.urlretrieve(DOWNLOAD, archive)
        with zipfile.ZipFile(archive) as z:
            # Chỉ lấy đúng tệp Excel đã biết, tránh giải nén đường dẫn tùy ý.
            path.write_bytes(z.read('Online Retail.xlsx'))
    raw = pd.read_excel(path, engine='openpyxl')
    expected = ['InvoiceNo', 'StockCode', 'Description', 'Quantity',
                'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country']
    assert list(raw.columns) == expected, 'Cấu trúc dữ liệu không đúng dự kiến.'
    assert len(raw) >= 10000 and len(raw.columns) >= 7
    metadata = {
        'source': SOURCE, 'download': DOWNLOAD,
        'citation': 'Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33',
        'license': 'CC BY 4.0', 'download_date_local': '2026-10-23',
        'sha256_excel': hashlib.sha256(path.read_bytes()).hexdigest(),
        'rows': len(raw), 'columns': list(raw.columns),
        'note': '541909 dòng hàng, không phải 541909 đơn hàng. UCI ghi 6 features và 2 ID; tệp có 8 cột.'
    }
    (raw_dir / 'source.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    return raw


def clean_data(raw):
    """Giữ dòng trùng; gắn cờ và lượng hóa độ nhạy thay vì mặc định xóa."""
    df = raw.copy()
    df['InvoiceNo'] = df.InvoiceNo.astype('string').str.strip()
    df['StockCode'] = df.StockCode.astype('string').str.strip()
    df['InvoiceDate'] = pd.to_datetime(df.InvoiceDate, errors='coerce')
    for col in ['Quantity', 'UnitPrice']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['IsCancellation'] = df.InvoiceNo.str.upper().str.startswith('C').fillna(False)
    df['LineValue'] = df.Quantity * df.UnitPrice
    df['ExactDuplicate'] = raw.duplicated(keep='first').to_numpy()
    valid = (df.InvoiceNo.notna() & df.StockCode.notna() & df.InvoiceDate.notna()
             & df.Country.notna() & np.isfinite(df.Quantity)
             & np.isfinite(df.UnitPrice) & (df.UnitPrice > 0))
    sale_mask = valid & ~df.IsCancellation & (df.Quantity > 0)
    cancel_mask = valid & df.IsCancellation & (df.Quantity < 0)
    df['Status'] = np.select([sale_mask, cancel_mask], ['sale', 'cancellation'], default='other')
    sales = df.loc[sale_mask].copy()
    cancellations = df.loc[cancel_mask].copy()
    cancellations['CancellationValue'] = -cancellations.LineValue
    other = df.loc[df.Status.eq('other')].copy()
    audit = pd.DataFrame([
        ('Dữ liệu thô', len(df), 'Giữ nguyên 8 cột nguồn; 1 dòng là 1 dòng hàng'),
        ('Giao dịch bán hợp lệ', len(sales), 'Không mã C, Quantity > 0, UnitPrice > 0; đủ khóa và ngày'),
        ('Giao dịch hủy hợp lệ', len(cancellations), 'Mã C, Quantity < 0, UnitPrice > 0; đủ khóa và ngày'),
        ('Dòng bất thường / không hợp lệ', len(other), 'Phần còn lại; lưu riêng để kiểm tra'),
        ('Bán có mã khách hàng', int(sales.CustomerID.notna().sum()), 'Chỉ tập này được dùng phân tích khách hàng'),
        ('Bán thiếu mã khách hàng', int(sales.CustomerID.isna().sum()), 'Vẫn giữ trong doanh số'),
        ('Dòng trùng hoàn toàn (sau dòng đầu)', int(df.ExactDuplicate.sum()), 'Giữ lại: chưa có bằng chứng là lỗi nhập lặp'),
    ], columns=['Buoc', 'So_dong', 'Quy_tac'])
    quality = pd.DataFrame({
        'Kieu_du_lieu': raw.dtypes.astype(str),
        'So_thieu': raw.isna().sum(),
        'Ty_le_thieu_pct': raw.isna().mean() * 100,
        'So_gia_tri_khac_nhau': raw.nunique(),
    }).rename_axis('Cot').reset_index()
    issues = {
        'quantity_negative': int((df.Quantity < 0).sum()),
        'price_zero': int((df.UnitPrice == 0).sum()),
        'price_negative': int((df.UnitPrice < 0).sum()),
        'negative_quantity_without_C': int(((df.Quantity < 0) & ~df.IsCancellation).sum()),
        'C_without_negative_quantity': int((df.IsCancellation & ~(df.Quantity < 0)).sum()),
        'duplicate_sale_value': float(sales.loc[sales.ExactDuplicate, 'LineValue'].sum()),
        'duplicate_cancel_value': float(cancellations.loc[cancellations.ExactDuplicate, 'CancellationValue'].sum()),
    }
    assert len(sales) + len(cancellations) + len(other) == len(raw)
    return dict(all=df, sales=sales, cancellations=cancellations, other=other,
                audit=audit, quality=quality, issues=issues)


def summarize(data):
    sales, cancel = data['sales'], data['cancellations']
    orders = sales.groupby('InvoiceNo').agg(
        OrderValue=('LineValue', 'sum'), Country=('Country', 'first'),
        InvoiceDate=('InvoiceDate', 'min'), CustomerID=('CustomerID', 'first'),
        Lines=('StockCode', 'size')).reset_index()
    # Mã hóa đơn cần cùng một quốc gia và tối đa một khách hàng xác định.
    assert sales.groupby('InvoiceNo').Country.nunique().max() == 1
    assert sales.groupby('InvoiceNo').CustomerID.nunique().max() <= 1
    monthly = sales.groupby(sales.InvoiceDate.dt.to_period('M')).LineValue.sum().to_frame('Sales')
    monthly['Cancellation'] = cancel.groupby(cancel.InvoiceDate.dt.to_period('M')).CancellationValue.sum()
    monthly = monthly.fillna(0)
    observed_end = data['all'].InvoiceDate.max()
    observed_start = data['all'].InvoiceDate.min()
    monthly['Partial'] = [(p.start_time.date() < observed_start.date()
                           or p.end_time.date() > observed_end.date()) for p in monthly.index]
    markets = sales.groupby('Country').LineValue.sum().to_frame('Sales')
    markets['Cancellation'] = cancel.groupby('Country').CancellationValue.sum()
    markets = markets.fillna(0).sort_values('Sales', ascending=False)
    markets['CancellationToSalesPct'] = markets.Cancellation / markets.Sales * 100
    # Các mã không bắt đầu bằng 5 chữ số (POST, DOT, M, ...) được xem là mã điều chỉnh/phí.
    product_rows = sales[sales.StockCode.str.match(r'^\d{5}', na=False)]
    products = product_rows.groupby('StockCode').LineValue.sum().sort_values(ascending=False).to_frame('Sales')
    names = product_rows.dropna(subset=['Description']).groupby('StockCode').Description.agg(lambda x: x.value_counts().index[0])
    products['Description'] = names
    customers = sales.dropna(subset=['CustomerID']).groupby('CustomerID').agg(
        Orders=('InvoiceNo', 'nunique'), Spending=('LineValue', 'sum')).sort_values('Spending', ascending=False)
    cancellation_invoices = cancel.groupby('InvoiceNo').agg(
        CancellationValue=('CancellationValue', 'sum'), Country=('Country', 'first'),
        InvoiceDate=('InvoiceDate', 'min')).sort_values('CancellationValue', ascending=False)
    large_cancellation_lines = cancel.nlargest(10, 'CancellationValue')[[
        'InvoiceNo', 'StockCode', 'Description', 'Quantity', 'UnitPrice', 'CancellationValue']]
    count_top = max(1, int(np.ceil(len(customers) * .1)))
    full = monthly[~monthly.Partial]
    peak = full.Sales.idxmax()
    s = {
        'raw_rows': len(data['all']), 'sale_rows': len(sales), 'cancel_rows': len(cancel),
        'other_rows': len(data['other']), 'orders': len(orders), 'customers': len(customers),
        'sales': float(sales.LineValue.sum()), 'cancellation': float(cancel.CancellationValue.sum()),
        'period_balance': float(sales.LineValue.sum() - cancel.CancellationValue.sum()),
        'cancel_to_sales_pct': float(cancel.CancellationValue.sum() / sales.LineValue.sum() * 100),
        'uk_share_pct': float(markets.loc['United Kingdom', 'Sales'] / sales.LineValue.sum() * 100),
        'identified_sales': float(customers.Spending.sum()),
        'identified_share_pct': float(customers.Spending.sum() / sales.LineValue.sum() * 100),
        'top10_customer_n': count_top,
        'top10_customer_share_pct': float(customers.head(count_top).Spending.sum() / customers.Spending.sum() * 100),
        'mean_order': float(orders.OrderValue.mean()), 'median_order': float(orders.OrderValue.median()),
        'p99_order': float(orders.OrderValue.quantile(.99)), 'max_order': float(orders.OrderValue.max()),
        'peak_month': str(peak), 'peak_sales': float(full.loc[peak, 'Sales']),
        'top_product': str(products.iloc[0].Description), 'top_product_code': str(products.index[0]),
        'top_product_sales': float(products.iloc[0].Sales),
        'top10_product_share_pct': float(products.head(10).Sales.sum() / sales.LineValue.sum() * 100),
        'nonproduct_sales': float(sales.LineValue.sum() - product_rows.LineValue.sum()),
        'spearman_orders_spending': float(customers.Orders.rank().corr(customers.Spending.rank())),
        'top2_cancellation_share_pct': float(cancellation_invoices.head(2).CancellationValue.sum() / cancel.CancellationValue.sum() * 100),
        'top2_cancellation_value': float(cancellation_invoices.head(2).CancellationValue.sum()),
        'largest_cancellation_invoice': str(cancellation_invoices.index[0]),
        'largest_cancellation_value': float(cancellation_invoices.iloc[0].CancellationValue),
        'start': str(observed_start), 'end': str(observed_end),
        'duplicates': int(data['all'].ExactDuplicate.sum()), **data['issues'],
    }
    # Không cần SciPy: tương quan Pearson trên thứ hạng là Spearman.
    return dict(orders=orders, monthly=monthly, markets=markets,
                products=products, customers=customers, cancellation_invoices=cancellation_invoices,
                large_cancellation_lines=large_cancellation_lines, stats=s)


def save_tables(root, data, tables):
    dest = Path(root) / 'outputs/tables'
    dest.mkdir(parents=True, exist_ok=True)
    processed = Path(root) / 'data/processed'
    processed.mkdir(parents=True, exist_ok=True)
    for name in ['audit', 'quality']:
        data[name].to_csv(dest / f'{name}.csv', index=False, encoding='utf-8-sig')
    for name in ['orders', 'monthly', 'markets', 'products', 'customers', 'cancellation_invoices', 'large_cancellation_lines']:
        tables[name].to_csv(dest / f'{name}.csv', index=True, encoding='utf-8-sig')
    for name in ['sales', 'cancellations', 'other']:
        data[name].to_csv(processed / f'{name}.csv', index=False, encoding='utf-8-sig')
    (dest / 'metrics.json').write_text(json.dumps(tables['stats'], ensure_ascii=False, indent=2), encoding='utf-8')


def make_charts(root, data, tables):
    out = Path(root) / 'outputs/figures'
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'Arial', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.spines.left': False, 'axes.titleweight': 'bold',
                         'axes.labelcolor': '#334155', 'text.color': '#172B3A',
                         'axes.edgecolor': '#CBD5E1', 'figure.facecolor': 'white'})
    paths = []

    def finish(fig, ax, filename, title, note):
        ax.set_title(title, loc='left', fontsize=15, pad=20)
        ax.grid(axis='y', alpha=.14)
        ax.set_axisbelow(True)
        fig.text(.025, .025, note + '\nNguồn: UCI Online Retail | Đơn vị tiền: GBP', fontsize=9, color='#526779')
        fig.tight_layout(rect=(.015, .12, .99, .98))
        path = out / filename
        fig.savefig(path, dpi=220, facecolor='white')
        plt.close(fig)
        paths.append(path)

    monthly = tables['monthly']
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    x = np.arange(len(monthly))
    full = ~monthly.Partial.to_numpy()
    ax.plot(x[full], monthly.Sales.to_numpy()[full] / 1e6, '-o', color=BLUE, linewidth=2)
    partial_idx = x[~full]
    ax.scatter(partial_idx, monthly.Sales.to_numpy()[~full] / 1e6, color=RED, marker='D', s=70, label='Tháng chưa đầy đủ')
    ax.set_xticks(x, [str(p)[2:] for p in monthly.index], rotation=35)
    ax.set_ylabel('Doanh số bán (triệu GBP)')
    ax.set_xlabel('Tháng (YY-MM)')
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False)
    finish(fig, ax, '01_line_monthly.png', 'Doanh số theo tháng: tách riêng kỳ chưa đầy đủ',
           'Bán hợp lệ, chưa trừ hủy. Tháng 12/2011 chỉ có dữ liệu đến ngày 09; không so tăng trưởng với tháng đủ.')

    p = tables['products'].head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10.8, 6.3))
    labels = [f'{code} | {str(row.Description)[:33]}' for code, row in p.iterrows()]
    ax.barh(labels, p.Sales / 1000, color=[BLUE] * 9 + [RED])
    ax.set_xlabel('Doanh số bán (nghìn GBP)')
    ax.grid(False)
    finish(fig, ax, '02_bar_products.png', 'Top 10 sản phẩm theo doanh số bán',
           'Gộp theo StockCode; tên phổ biến nhất. Chỉ mã bắt đầu bằng 5 chữ số; loại mã phí/điều chỉnh khỏi xếp hạng.')

    m = tables['markets'].head(6)
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    # Stacked bar 100%: mẫu số là bán + trị tuyệt đối hủy, không phải doanh thu thuần.
    denom = m.Sales + m.Cancellation
    sell_pct, cancel_pct = m.Sales / denom * 100, m.Cancellation / denom * 100
    ax.bar(m.index, sell_pct, color=BLUE, label='Giá trị bán')
    ax.bar(m.index, cancel_pct, bottom=sell_pct, color=RED, label='Giá trị hủy (trị tuyệt đối)')
    for i, v in enumerate(cancel_pct):
        ax.text(i, 102, f'{v:.1f}%', ha='center', color=RED, fontsize=10)
    ax.set_ylim(0, 113)
    ax.set_ylabel('Tỷ trọng trong (bán + |hủy|), %')
    ax.tick_params(axis='x', rotation=15)
    ax.legend(frameon=True, facecolor='white', edgecolor='white', framealpha=.95, loc='lower right')
    finish(fig, ax, '03_stacked_markets.png', 'Cơ cấu giá trị bán và hủy ở sáu thị trường lớn',
           'Nhãn đỏ = |hủy| / (bán + |hủy|). Không phải tỷ lệ đơn hủy; không ghép hủy về đơn bán gốc.')

    orders = tables['orders']
    p99 = orders.OrderValue.quantile(.99)
    shown = orders.loc[orders.OrderValue <= p99, 'OrderValue']
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    ax.hist(shown, bins=45, color=BLUE, edgecolor='white', linewidth=.4)
    median = orders.OrderValue.median()
    ax.axvline(median, color=RED, linewidth=2, label=f'Trung vị toàn bộ: {median:,.2f} GBP')
    ax.set_xlabel('Giá trị đơn bán (GBP)')
    ax.set_ylabel('Số đơn hàng')
    ax.legend(frameon=False)
    finish(fig, ax, '04_hist_orders.png', 'Phần lớn đơn hàng nằm ở vùng giá trị nào?',
           f'Gộp theo InvoiceNo. Hiển thị ≤ P99 = {p99:,.2f} GBP; {len(orders)-len(shown):,} đơn ngoài hình vẫn được giữ trong KPI.')

    countries = tables['markets'].head(5).index.tolist()
    groups = [orders.loc[orders.Country.eq(c), 'OrderValue'] for c in countries]
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    bp = ax.boxplot(groups, tick_labels=countries, showfliers=False, patch_artist=True,
                    medianprops=dict(color=RED, linewidth=2))
    for patch in bp['boxes']:
        patch.set_facecolor('#D6E8EF')
        patch.set_edgecolor(BLUE)
    ax.set_ylabel('Giá trị đơn bán (GBP)')
    ax.tick_params(axis='x', rotation=12)
    finish(fig, ax, '05_box_markets.png', 'Giá trị đơn hàng khác nhau giữa các thị trường',
           'Hộp: Q1–Q3; vạch đỏ: trung vị; râu: tối đa 1,5 IQR. Ẩn điểm ngoài râu, không xóa khỏi tính toán.')

    c = tables['customers']
    threshold = c.Spending.quantile(.9)
    colors = np.where(c.Spending >= threshold, RED, BLUE)
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    ax.scatter(c.Orders, c.Spending, c=colors, s=16, alpha=.45, edgecolors='none')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.set_xlabel('Số đơn bán / khách hàng (thang log)')
    ax.set_ylabel('Tổng chi tiêu bán (GBP, thang log)')
    finish(fig, ax, '06_scatter_customers.png', 'Khách mua thường xuyên có chi tiêu cao hơn đến mức nào?',
           'Chỉ khách có CustomerID; chưa trừ hủy. Màu đỏ: chi tiêu ≥ P90. Giữ mọi khách; thang log để đọc đuôi dài.')
    return paths


def validate(data, t, figures):
    """Kiểm tra các bất biến kinh doanh, không chỉ kiểm tra file tồn tại."""
    s = t['stats']
    assert s['raw_rows'] == 541909
    assert len(figures) == 6 and all(p.exists() and p.stat().st_size > 10000 for p in figures)
    assert np.isclose(t['orders'].OrderValue.sum(), s['sales'])
    assert np.isclose(t['monthly'].Sales.sum(), s['sales'])
    assert np.isclose(t['markets'].Sales.sum(), s['sales'])
    assert np.isclose(t['monthly'].Cancellation.sum(), s['cancellation'])
    assert np.isclose(t['markets'].Cancellation.sum(), s['cancellation'])
    assert np.isclose(t['cancellation_invoices'].CancellationValue.sum(), s['cancellation'])
    assert np.isclose(t['customers'].Spending.sum(), data['sales'].loc[data['sales'].CustomerID.notna(), 'LineValue'].sum())
    assert t['orders'].InvoiceNo.is_unique
    assert data['sales'].LineValue.gt(0).all()
    assert data['cancellations'].CancellationValue.gt(0).all()
    assert not set(data['sales'].index) & set(data['cancellations'].index)
    assert t['monthly'].loc[pd.Period('2011-12'), 'Partial']
    return 'PASS: dữ liệu, phân nhóm, 6 biểu đồ, đối soát đơn/tháng/thị trường/khách hàng.'


def main(root):
    from src.deliverables import build_report, build_notebook, build_presentation
    raw = load_data(root)
    data = clean_data(raw)
    tables = summarize(data)
    save_tables(root, data, tables)
    figures = make_charts(root, data, tables)
    result = validate(data, tables, figures)
    build_report(root, data, tables, figures)
    build_notebook(root)
    build_presentation(root, tables)
    (Path(root) / 'outputs/validation.txt').write_text(result + '\n', encoding='utf-8')
    print(json.dumps(tables['stats'], ensure_ascii=True, indent=2))
    print(result)


"""Đóng gói bài nộp đã kiểm tra, gồm nguồn dữ liệu để tái tạo offline."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent


def main():
    verification = json.loads((ROOT / 'outputs/verification.json').read_text(encoding='utf-8'))
    assert verification['status'] == 'PASS'
    dest = ROOT / 'submission'
    files = [ROOT / name for name in [
        'README.md', 'requirements.txt', 'context.md', 'run.py', 'execute_notebook.py',
        'verify_outputs.py', 'package_submission.py', 'visual_analytics.ipynb',
        'data/raw/Online Retail.xlsx', 'data/raw/source.json',
        'outputs/bao_cao_visual_analytics.pdf', 'outputs/bao_cao_visual_analytics.md',
        'outputs/thuyet_trinh.md', 'outputs/validation.txt', 'outputs/verification.json',
    ]]
    for folder, pattern in [('src', '*.py'), ('docs', '*.md'),
                            ('outputs/figures', '*.png'), ('outputs/tables', '*')]:
        files.extend(sorted((ROOT / folder).glob(pattern)))
    manifest = {}
    for source in files:
        assert source.is_file(), str(source)
        rel = source.relative_to(ROOT)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        manifest[rel.as_posix()] = hashlib.sha256(target.read_bytes()).hexdigest()
    (dest / 'manifest_sha256.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    archive = ROOT / 'bai_nop_visual_analytics.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for rel in [*manifest, 'manifest_sha256.json']:
            z.write(dest / rel, rel)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(manifest) + 1
    print('ZIP verified:', archive.name, '| files:', len(manifest) + 1,
          '| MB:', round(archive.stat().st_size / 1024**2, 2))


if __name__ == '__main__':
    main()

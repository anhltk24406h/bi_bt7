"""Chạy: python run.py. Thư viện cục bộ được tìm trong .packages nếu có."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if (ROOT / '.packages').exists():
    sys.path.insert(0, str(ROOT / '.packages'))
from src.analysis import main

if __name__ == '__main__':
    main(ROOT)

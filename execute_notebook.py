"""Thực thi notebook bằng kernel Python hiện tại, không cần đăng ký kernel toàn máy."""
from pathlib import Path
import os
import sys
import json

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / '.packages'
if LOCAL.exists():
    sys.path.insert(0, str(LOCAL))
import nbformat
from nbclient import NotebookClient


def main():
    # Jupyter chỉ ghi cache và kernel spec trong workspace.
    cache = ROOT / '.jupyter_runtime'
    spec_dir = cache / 'kernels/python3'
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / 'kernel.json').write_text(json.dumps({
        'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        'display_name': 'Python dự án', 'language': 'python'
    }), encoding='utf-8')
    os.environ['JUPYTER_PATH'] = str(cache)
    os.environ['JUPYTER_RUNTIME_DIR'] = str(cache / 'runtime')
    os.environ['IPYTHONDIR'] = str(cache / 'ipython')
    os.environ['PYTHONPATH'] = os.pathsep.join([str(LOCAL), str(ROOT), os.environ.get('PYTHONPATH', '')])
    nb_path = ROOT / 'visual_analytics.ipynb'
    notebook = nbformat.read(nb_path, as_version=4)
    client = NotebookClient(notebook, timeout=600, kernel_name='python3',
                            resources={'metadata': {'path': str(ROOT)}})
    client.execute()
    nbformat.write(notebook, nb_path)
    print('Notebook executed:', sum(c.cell_type == 'code' for c in notebook.cells), 'code cells; no errors.')


if __name__ == '__main__':
    main()

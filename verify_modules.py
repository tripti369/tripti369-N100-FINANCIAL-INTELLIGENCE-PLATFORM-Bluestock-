import importlib.util
from pathlib import Path

for filename in ['pages/04_Peers.py', 'pages/05_Trends.py', 'pages/06_Sectors.py']:
    path = Path(filename)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print(filename, 'has app:', hasattr(module, 'app'))

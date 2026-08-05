import importlib.util
from pathlib import Path

for filename in ['pages/05_Trends.py', 'pages/06_Sectors.py']:
    path = Path(filename)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        print(filename, 'imported ok')
        if hasattr(module, 'app'):
            try:
                module.app(set_page_config=False)
                print(filename, 'app() ran ok')
            except Exception as e:
                import traceback
                print(filename, 'app() error:')
                traceback.print_exc()
        else:
            print(filename, 'missing app()')
    except Exception as e:
        import traceback
        print(filename, 'import error:')
        traceback.print_exc()

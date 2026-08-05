import sys
from pathlib import Path
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))

print('sys.path[0]=', sys.path[0])

try:
    import utils
    print('utils module file:', getattr(utils, '__file__', None))
    print('utils path:', getattr(utils, '__path__', None))
except Exception as exc:
    print('failed to import utils:', exc)

try:
    import utils.db as db
    print('utils.db file:', db.__file__)
    print('load_cash_flow exists:', hasattr(db, 'load_cash_flow'))
except Exception as exc:
    print('failed to import utils.db:', exc)

try:
    from utils.db import load_cash_flow
    print('from utils.db import load_cash_flow ok:', load_cash_flow)
except Exception as exc:
    print('failed from import load_cash_flow:', exc)

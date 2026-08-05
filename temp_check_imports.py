import sys
from pathlib import Path
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))
print('root', root)
try:
    import utils
    print('utils', getattr(utils, '__file__', None), getattr(utils, '__path__', None))
    import utils.db as db
    print('utils.db', db.__file__)
    for name in ['load_master','load_balance_sheet','load_cash_flow','load_market_cap','load_analysis','load_documents','load_pros_cons','load_profit_loss']:
        print(name, hasattr(db, name))
except Exception as exc:
    import traceback
    traceback.print_exc()

from importlib.util import spec_from_file_location, module_from_spec
for f in ['pages/09_CashFlow.py','pages/10_Valuation.py','pages/11_NLP.py','src/nlp/parser.py','src/nlp/pros_cons_generator.py','src/analytics/cashflow_kpis.py','src/reports/portfolio_generator.py']:
    path = root / f
    print('===', f, path.exists())
    if not path.exists():
        continue
    try:
        spec = spec_from_file_location(f.replace('/', '_').replace('.py', ''), path)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        print('loaded', f)
    except Exception as exc:
        import traceback
        print('failed to load', f)
        traceback.print_exc()
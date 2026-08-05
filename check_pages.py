import sys
import importlib.util

sys.path.insert(0, ".")

pages = [
    "pages/02_Profile.py",
    "pages/03_Screener.py",
    "pages/04_Peers.py",
    "pages/05_Trends.py",
    "pages/06_Sectors.py",
    "pages/07_Capital.py",
    "pages/08_Reports.py",
    "pages/09_CashFlow.py",
    "pages/10_Valuation.py",
    "pages/11_NLP.py",
    "pages/12_Portfolio.py",
]

for p in pages:
    for key in list(sys.modules.keys()):
        if key.startswith("utils.") or key.startswith("src."):
            del sys.modules[key]
    spec = importlib.util.spec_from_file_location("test_mod", p)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        print(f"OK  {p}")
    except Exception as e:
        print(f"ERR {p} -> {e}")

import sys
from pathlib import Path
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))

import streamlit as st

# Monkeypatch set_page_config to avoid Streamlit startup behavior.
st.set_page_config = lambda *args, **kwargs: None

page_files = [
    'pages/09_CashFlow.py',
    'pages/10_Valuation.py',
    'pages/11_NLP.py',
    'pages/12_Portfolio.py',
]

from importlib.util import spec_from_file_location, module_from_spec

for page in page_files:
    path = root / page
    print('===', page)
    spec = spec_from_file_location(page.replace('/', '_').replace('.py', ''), path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, 'app'):
        print('NO app() in', page)
        continue
    try:
        module.app(set_page_config=False)
        print('app() ok for', page)
    except Exception as exc:
        import traceback
        traceback.print_exc()

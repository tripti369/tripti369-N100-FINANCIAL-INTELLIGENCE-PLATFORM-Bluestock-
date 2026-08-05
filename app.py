import importlib
import importlib.util
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st
from utils.db import load_master

st.set_page_config(
    page_title="Nifty100 Analytics",
    page_icon="📈",
    layout="wide"
)

PAGES_DIR = Path(__file__).resolve().parent / "pages"
PAGE_MODULES = [
    ("Company Profile", "02_Profile.py"),
    ("Stock Screener", "03_Screener.py"),
    ("Peer Comparison", "04_Peers.py"),
    ("Financial Trends", "05_Trends.py"),
    ("Sector Analysis", "06_Sectors.py"),
    ("Capital Structure", "07_Capital.py"),
    ("Company Reports", "08_Reports.py"),
    ("Cash Flow Intelligence", "09_CashFlow.py"),
    ("Valuation & Health", "10_Valuation.py"),
    ("NLP Insights", "11_NLP.py"),
    ("Portfolio Summary", "12_Portfolio.py"),
]


def load_page_module(page_filename):
    page_path = PAGES_DIR / page_filename
    module_name = f"nifty100_page_{page_filename.replace('.', '_')}"

    # Clear stale cached modules so re-imports resolve fresh
    for key in list(sys.modules.keys()):
        if key == module_name or key.startswith("utils.") or key.startswith("src."):
            del sys.modules[key]

    spec = importlib.util.spec_from_file_location(module_name, page_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


master = load_master()

selected_page = st.sidebar.radio(
    "Select a page",
    ["Home"] + [title for title, _ in PAGE_MODULES],
    index=0,
)

if selected_page == "Home":
    st.title("📈 Nifty100 Financial Intelligence Platform")

    st.markdown(
        """
        Welcome to the **Nifty100 Analytics Dashboard**.

        Use the sidebar to explore companies, screen stocks, compare peers and analyze financial performance.
        """
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Companies", len(master))

    with c2:
        st.metric("ROE Available", master["roe_percentage"].notna().sum())

    with c3:
        st.metric("ROCE Available", master["roce_percentage"].notna().sum())

    with c4:
        st.metric("Book Value", "Available")

    st.divider()

    st.subheader("🚀 Available Modules")

    for title, filename in PAGE_MODULES:
        st.markdown(f"- **{title}**")

    st.divider()

    st.caption("Built with Streamlit • SQLite • Plotly • Pandas")

else:
    page_filename = next(filename for title, filename in PAGE_MODULES if title == selected_page)
    try:
        page_module = load_page_module(page_filename)
        if hasattr(page_module, "app"):
            page_module.app(set_page_config=False)
        else:
            st.error("Selected module does not expose an app() function.")
    except Exception as exc:
        st.error("Could not load selected page.")
        st.exception(exc)

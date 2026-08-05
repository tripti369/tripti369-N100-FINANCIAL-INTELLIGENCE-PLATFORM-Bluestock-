import streamlit as st
import pandas as pd
from utils.db import load_master


def app(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    master = load_master().copy()

    st.title("🔍 Stock Screener")

    # -----------------------------
    # Data Cleaning
    # -----------------------------
    numeric_cols = [
        "roe_percentage",
        "roce_percentage",
        "book_value",
        "face_value"
    ]

    for col in numeric_cols:
        master[col] = pd.to_numeric(master[col], errors="coerce")

    # -----------------------------
    # Sidebar Filters
    # -----------------------------
    st.sidebar.header("Filters")

    company_search = st.sidebar.text_input("Search Company")

    roe_min = st.sidebar.slider(
        "Minimum ROE (%)",
        0,
        100,
        10
    )

    roce_min = st.sidebar.slider(
        "Minimum ROCE (%)",
        0,
        100,
        10
    )

    book_value = st.sidebar.slider(
        "Minimum Book Value",
        0.0,
        float(master["book_value"].max()),
        0.0
    )

    # -----------------------------
    # Apply Filters
    # -----------------------------
    filtered = master.copy()

    if company_search:
        filtered = filtered[
            filtered["company_name"].str.contains(
                company_search,
                case=False,
                na=False
            )
        ]

    filtered = filtered[
        (filtered["roe_percentage"] >= roe_min) &
        (filtered["roce_percentage"] >= roce_min) &
        (filtered["book_value"] >= book_value)
    ]

    # -----------------------------
    # KPI Cards
    # -----------------------------
    c1, c2, c3 = st.columns(3)

    c1.metric("Companies Found", len(filtered))

    c2.metric(
        "Average ROE",
        round(filtered["roe_percentage"].mean(), 2)
        if len(filtered) else 0
    )

    c3.metric(
        "Average ROCE",
        round(filtered["roce_percentage"].mean(), 2)
        if len(filtered) else 0
    )

    st.divider()

    # -----------------------------
    # Results Table
    # -----------------------------
    display_cols = [
        "company_name",
        "roe_percentage",
        "roce_percentage",
        "book_value",
        "face_value"
    ]

    st.dataframe(
        filtered[display_cols].sort_values(
            "roe_percentage",
            ascending=False
        ),
        use_container_width=True
    )

    # -----------------------------
    # Download CSV
    # -----------------------------
    csv = filtered[display_cols].to_csv(index=False)

    st.download_button(
        "📥 Download Filtered Companies",
        csv,
        "screened_companies.csv",
        "text/csv"
    )

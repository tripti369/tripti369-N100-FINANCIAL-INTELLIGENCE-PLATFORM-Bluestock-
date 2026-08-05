import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import load_master, load_table


def app(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    st.title("📈 Financial Trends")

    master = load_master()
    profit = load_table("profit_loss")

    company = st.selectbox(
        "Select Company",
        sorted(master["company_name"].dropna().unique())
    )

    row = master[master["company_name"] == company].iloc[0]
    company_id = str(row["id"]).strip().upper()

    profit["company_id"] = profit["company_id"].astype(str).str.strip().str.upper()
    profit = profit[profit["company_id"] == company_id].copy()

    if profit.empty:
        st.warning("No financial data available for the selected company.")
        st.info("Please choose a company with profit & loss data in the dataset.")
        st.stop()

    profit["year"] = profit["year"].astype(str)

    numeric_cols = [
        "sales",
        "net_profit",
        "eps",
        "operating_profit"
    ]

    for col in numeric_cols:
        profit[col] = pd.to_numeric(profit[col], errors="coerce")

    metric = st.selectbox(
        "Select Metric",
        {
            "Revenue": "sales",
            "Net Profit": "net_profit",
            "Operating Profit": "operating_profit",
            "EPS": "eps"
        }
    )

    column = {
        "Revenue": "sales",
        "Net Profit": "net_profit",
        "Operating Profit": "operating_profit",
        "EPS": "eps"
    }[metric]

    fig = px.line(
        profit,
        x="year",
        y=column,
        markers=True,
        title=f"{metric} Trend"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(profit, use_container_width=True)
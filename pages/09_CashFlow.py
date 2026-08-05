import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import load_master, load_cash_flow, load_balance_sheet
from src.analytics.cashflow_kpis import generate_cashflow_intelligence


def resolve_company_id(row):
    return str(
        row.get("company_id") or row.get("company_id_pl") or row.get("id") or ""
    ).strip().upper()


def app(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    st.title("💧 Cash Flow Intelligence")

    master = load_master()
    cash = load_cash_flow()
    balance = load_balance_sheet()

    company = st.selectbox(
        "Select Company",
        sorted(master["company_name"].dropna().unique())
    )

    row = master[master["company_name"] == company].iloc[0]
    company_id = resolve_company_id(row)
    if not company_id:
        st.warning("Selected company does not have a valid company identifier.")
        return

    company_cash = cash[cash["company_id"].astype(str).str.strip().str.upper() == company_id].copy()
    company_balance = balance[balance["company_id"].astype(str).str.strip().str.upper() == company_id].copy()

    if company_cash.empty or company_balance.empty:
        st.warning("No cash flow or balance sheet data available for the selected company.")
        return

    company_cash["year"] = pd.to_numeric(company_cash["year"], errors="coerce")
    company_cash = company_cash.sort_values("year")

    company_cash["operating_activity"] = pd.to_numeric(company_cash["operating_activity"], errors="coerce")
    company_cash["investing_activity"] = pd.to_numeric(company_cash["investing_activity"], errors="coerce")
    company_cash["financing_activity"] = pd.to_numeric(company_cash["financing_activity"], errors="coerce")

    cfo_chart = px.bar(
        company_cash,
        x="year",
        y="operating_activity",
        title="Operating Cash Flow Trend",
        labels={"operating_activity": "Operating Activity"}
    )
    st.plotly_chart(cfo_chart, use_container_width=True)

    capex_chart = px.bar(
        company_cash,
        x="year",
        y="investing_activity",
        title="Investing Activity (CapEx) Trend",
        labels={"investing_activity": "Investing Activity"}
    )
    st.plotly_chart(capex_chart, use_container_width=True)

    financing_chart = px.bar(
        company_cash,
        x="year",
        y="financing_activity",
        title="Financing Activity Trend",
        labels={"financing_activity": "Financing Activity"}
    )
    st.plotly_chart(financing_chart, use_container_width=True)

    st.markdown("### Latest Cash Flow Summary")
    latest = company_cash.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("CFO", f"{latest['operating_activity']:,}")
    c2.metric("CFI", f"{latest['investing_activity']:,}")
    c3.metric("CFF", f"{latest['financing_activity']:,}")

    if st.button("Generate Full Cash Flow Intelligence Report"):
        df = generate_cashflow_intelligence()
        st.success("Cash flow intelligence output generated.")
        company_report = df[df["company_id"] == company_id]
        if not company_report.empty:
            st.dataframe(company_report, use_container_width=True)
        else:
            st.warning("This company was not included in the generated cash flow intelligence output.")

    st.markdown("### Raw Cash Flow Data")
    st.dataframe(company_cash, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import load_master, load_market_cap, load_profit_loss


def resolve_company_id(row):
    return str(
        row.get("company_id") or row.get("company_id_pl") or row.get("id") or ""
    ).strip().upper()


def normalize_market_cap(df: pd.DataFrame) -> pd.DataFrame:
    if "abb" in df.columns:
        df = df.rename(columns={"abb": "company_id"})
    if "company_id" not in df.columns and "id" in df.columns:
        df = df.rename(columns={"id": "company_id"})

    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].astype(str).str.strip().str.upper()

    if "market_cap" not in df.columns:
        numeric_cols = [
            c for c in df.columns
            if c not in {"company_id", "id", "year"} and pd.api.types.is_numeric_dtype(df[c])
        ]
        if numeric_cols:
            largest = sorted(
                numeric_cols,
                key=lambda c: df[c].abs().mean() if len(df[c]) else 0,
                reverse=True,
            )
            df = df.rename(columns={largest[0]: "market_cap"})

    if "market_cap" not in df.columns:
        df["market_cap"] = 0

    return df


def app(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    st.title("💰 Valuation & Financial Health")

    master = load_master()
    market_cap = normalize_market_cap(load_market_cap())
    profit = load_profit_loss()

    master["company_id"] = master["company_id"].fillna("").astype(str).str.strip().str.upper()
    master["company_id_pl"] = master["company_id_pl"].fillna("").astype(str).str.strip().str.upper()
    master["id"] = master["id"].fillna("").astype(str).str.strip().str.upper()
    master["company_id_resolved"] = master["company_id"]
    missing = master["company_id_resolved"] == ""
    master.loc[missing, "company_id_resolved"] = master.loc[missing, "company_id_pl"]
    missing = master["company_id_resolved"] == ""
    master.loc[missing, "company_id_resolved"] = master.loc[missing, "id"]

    merged = master.merge(
        market_cap,
        left_on="company_id_resolved",
        right_on="company_id",
        how="left"
    )

    merged["roe_percentage"] = pd.to_numeric(merged["roe_percentage"], errors="coerce")
    merged["roce_percentage"] = pd.to_numeric(merged["roce_percentage"], errors="coerce")

    # Ensure a sector column exists for coloring. Create a literal 'sector' column if missing.
    if "sector" not in merged.columns:
        merged["sector"] = "Unknown"
    else:
        merged["sector"] = merged["sector"].fillna("Unknown")

    st.markdown("### Valuation Overview")
    fig = px.scatter(
        merged,
        x="roce_percentage",
        y="roe_percentage",
        size="market_cap",
        color="sector",
        hover_name="company_name",
        title="ROE vs ROCE vs Market Cap"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Top Financial Health Leaders")
    leaders = merged.sort_values(["roe_percentage", "roce_percentage"], ascending=False).head(10)
    st.dataframe(leaders[["company_name", "roe_percentage", "roce_percentage", "market_cap"]], use_container_width=True)

    st.markdown("### Net Profit Trend")
    profit["year"] = pd.to_numeric(profit["year"], errors="coerce")
    profit = profit.sort_values(["company_id", "year"])
    company = st.selectbox("Select Company for Profit Trend", sorted(master["company_name"].dropna().unique()))
    selected_id = master[master["company_name"] == company]["company_id"].iloc[0]
    company_profit = profit[profit["company_id"].astype(str).str.strip().str.upper() == str(selected_id).strip().upper()]
    if not company_profit.empty:
        fig2 = px.line(company_profit, x="year", y="net_profit", title=f"Net Profit Trend for {company}")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No profit loss data available for the selected company.")

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import load_master, load_table


def app(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    st.title("🏭 Sector Analysis")

    master = load_master()
    companies = load_table("companies")
    sectors = load_table("sectors")

    # Clean column names
    companies.columns = [c.lower() for c in companies.columns]
    sectors.columns = [c.lower() for c in sectors.columns]

    # Fix malformed sector headers if needed
    if list(sectors.columns) == ["1", "abb", "industrials", "capital_goods", "081", "large_cap"]:
        sectors.columns = ["id", "company_id", "broad_sector", "sub_sector", "index_weight_pct", "market_cap_category"]

    # Merge
    companies["id"] = companies["id"].astype(str).str.upper()
    sectors["company_id"] = sectors["company_id"].astype(str).str.upper()

    sector_df = companies.merge(
        sectors[["company_id", "broad_sector"]],
        left_on="id",
        right_on="company_id",
        how="left"
    )

    sector_df["roe_percentage"] = pd.to_numeric(
        sector_df["roe_percentage"],
        errors="coerce"
    )

    sector_df["roce_percentage"] = pd.to_numeric(
        sector_df["roce_percentage"],
        errors="coerce"
    )

    if sector_df["broad_sector"].isna().all():
        st.warning("No sector data found. Please verify the sectors dataset.")
        st.stop()

    summary = (
        sector_df
        .groupby("broad_sector")
        .agg(
            Companies=("company_name", "count"),
            Avg_ROE=("roe_percentage", "mean"),
            Avg_ROCE=("roce_percentage", "mean")
        )
        .reset_index()
    )

    st.dataframe(summary, use_container_width=True)

    fig = px.bar(
        summary,
        x="broad_sector",
        y="Companies",
        title="Companies per Sector"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(
        summary,
        x="broad_sector",
        y="Avg_ROE",
        title="Average ROE by Sector"
    )

    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.bar(
        summary,
        x="broad_sector",
        y="Avg_ROCE",
        title="Average ROCE by Sector"
    )

    st.plotly_chart(fig3, use_container_width=True)
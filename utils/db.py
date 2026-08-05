import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "nifty100.db"


def normalize_table_columns(table, df):
    if table == "peer_groups" and list(df.columns) == ["2", "private_banks", "icicibank", "false"]:
        df.columns = ["id", "peer_group", "company_id", "is_leader"]
    elif table == "sectors" and list(df.columns) == ["1", "abb", "industrials", "capital_goods", "081", "large_cap"]:
        df.columns = ["id", "company_id", "broad_sector", "sub_sector", "index_weight_pct", "market_cap_category"]
    elif table == "market_cap":
        if "abb" in df.columns:
            df = df.rename(columns={"abb": "company_id"})
        if "company_id" not in df.columns and "id" in df.columns:
            df = df.rename(columns={"id": "company_id"})
    elif table == "master_company_data":
        if "company_id" not in df.columns and "company_id_pl" in df.columns:
            df["company_id"] = df["company_id_pl"]
        elif "company_id" in df.columns and "company_id_pl" in df.columns:
            df["company_id"] = df["company_id"].fillna(df["company_id_pl"])
    return df


@st.cache_data(ttl=600)
def load_table(table):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()
    return normalize_table_columns(table, df)


@st.cache_data(ttl=600)
def load_master():
    return load_table("master_company_data")


@st.cache_data(ttl=600)
def load_profit_loss():
    return load_table("profit_loss")


@st.cache_data(ttl=600)
def load_balance_sheet():
    return load_table("balance_sheet")


@st.cache_data(ttl=600)
def load_cash_flow():
    return load_table("cash_flow")


@st.cache_data(ttl=600)
def load_market_cap():
    return load_table("market_cap")


@st.cache_data(ttl=600)
def load_stock_prices():
    return load_table("stock_prices")


@st.cache_data(ttl=600)
def load_peer_groups():
    return load_table("peer_groups")


@st.cache_data(ttl=600)
def load_analysis():
    return load_table("analysis")


@st.cache_data(ttl=600)
def load_documents():
    return load_table("documents")


@st.cache_data(ttl=600)
def load_pros_cons():
    return load_table("pros_cons")
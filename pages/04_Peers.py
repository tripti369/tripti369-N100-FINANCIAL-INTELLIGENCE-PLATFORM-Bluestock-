import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import load_master, load_table


def app(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    st.title("📊 Peer Comparison")

    master = load_master()
    peer = load_table("peer_groups")

    # Normalize peer group table if headers were malformed
    if list(peer.columns) == ["2", "private_banks", "icicibank", "false"]:
        peer.columns = ["id", "peer_group", "company_id", "is_leader"]

    # Company IDs uppercase for matching
    master["id"] = master["id"].astype(str).str.upper()
    peer["company_id"] = peer["company_id"].astype(str).str.strip().str.upper()

    master = master.merge(
        peer[["company_id", "peer_group", "is_leader"]],
        left_on="id",
        right_on="company_id",
        how="left"
    )

    company = st.selectbox(
        "Select Company",
        sorted(master["company_name"].dropna().unique())
    )

    row = master[master["company_name"] == company].iloc[0]

    peer_group = row.get("peer_group")

    if pd.isna(peer_group) or peer_group is None:
        st.warning("Peer Group not available for the selected company.")
        st.info("Please choose a different company or update the peer_groups dataset.")
        st.stop()

    peers = master[
        master["peer_group"] == peer_group
    ].copy()

    if peers.empty:
        st.warning("No peer companies were found for this peer group.")
        st.stop()

    for col in [
        "roe_percentage",
        "roce_percentage",
        "book_value"
    ]:
        peers[col] = pd.to_numeric(
            peers[col],
            errors="coerce"
        )

    st.subheader(f"Peer Group : {peer_group}")

    st.dataframe(
        peers[
            [
                "company_name",
                "roe_percentage",
                "roce_percentage",
                "book_value",
                "is_leader"
            ]
        ],
        use_container_width=True
    )

    fig = px.bar(
        peers,
        x="company_name",
        y="roe_percentage",
        color="is_leader",
        title="ROE Comparison"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(
        peers,
        x="company_name",
        y="roce_percentage",
        color="is_leader",
        title="ROCE Comparison"
    )

    st.plotly_chart(fig2, use_container_width=True)
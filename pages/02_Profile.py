import streamlit as st
import pandas as pd
from utils.db import load_master


def app(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    master = load_master()

    st.title("🏢 Company Profile")

    company = st.selectbox(
        "Select Company",
        sorted(master["company_name"].dropna().unique())
    )

    row = master[master["company_name"] == company].iloc[0]

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("ROE (%)", row["roe_percentage"])
    col2.metric("ROCE (%)", row["roce_percentage"])
    col3.metric("Book Value", row["book_value"])
    col4.metric("Face Value", row["face_value"])

    st.markdown("---")

    left, right = st.columns([2, 1])

    with left:
        st.subheader("About Company")
        st.write(row["about_company"])

    with right:
        st.subheader("Links")

        if pd.notna(row["website"]):
            st.markdown(f"🌐 {row['website']}")

        if pd.notna(row["nse_profile"]):
            st.markdown(f"📈 NSE : {row['nse_profile']}")

        if pd.notna(row["bse_profile"]):
            st.markdown(f"📊 BSE : {row['bse_profile']}")

    st.markdown("---")

    st.subheader("Company Logo")

    if pd.notna(row["company_logo"]):
        st.image(row["company_logo"], width=180)
    else:
        st.info("Logo not available.")
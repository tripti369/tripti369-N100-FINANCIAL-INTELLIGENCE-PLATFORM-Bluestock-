import streamlit as st

from utils.db import load_master


def app(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    st.title("📄 Company Reports")

    master = load_master()

    company = st.selectbox(
        "Select Company",
        sorted(master["company_name"].dropna().unique())
    )

    row = master[
        master["company_name"] == company
    ].iloc[0]

    st.subheader(company)

    st.markdown("### Company Overview")
    st.write(row["about_company"])

    st.markdown("### Financial Snapshot")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("ROE", row["roe_percentage"])
    c2.metric("ROCE", row["roce_percentage"])
    c3.metric("Book Value", row["book_value"])
    c4.metric("Face Value", row["face_value"])

    st.divider()

    st.markdown("### Official Website")
    st.write(row["website"])

    st.download_button(
        "⬇ Download Summary",
        data=f"""
Company: {company}

ROE: {row['roe_percentage']}
ROCE: {row['roce_percentage']}
Book Value: {row['book_value']}
Face Value: {row['face_value']}

Website:
{row['website']}
""",
        file_name=f"{company}_summary.txt",
        mime="text/plain"
    )
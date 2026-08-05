import streamlit as st

from src.reports.portfolio_generator import create_portfolio_summary


def app(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    st.title("📊 Portfolio Summary")

    if st.button("Generate Portfolio Summary PDF"):
        output_path = create_portfolio_summary()
        st.success(f"Portfolio summary generated: {output_path}")
        st.markdown("### Output files")
        st.write(output_path)

    st.markdown(
        "This module generates an alphabetical portfolio summary PDF with trend arrows for each company."
    )

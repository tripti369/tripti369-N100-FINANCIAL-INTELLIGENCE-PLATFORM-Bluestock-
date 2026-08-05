import streamlit as st
import pandas as pd

from src.nlp.parser import parse_analysis_excel
from src.nlp.pros_cons_generator import generate_pros_cons
from utils.db import load_master


def app(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    st.title("🤖 NLP Insights")

    master = load_master()
    st.markdown("### NLP Processing")

    if st.button("Parse Analysis Text"):
        parsed = parse_analysis_excel(
            source_path="analysis.xlsx",
            output_path="output/analysis_parsed.csv",
            failures_path="output/parse_failures.csv",
            divergence_path="output/analysis_divergences.csv",
        )
        st.success("Analysis parsing complete.")
        st.dataframe(parsed.head(20), use_container_width=True)

    if st.button("Generate Pros/Cons"):
        generated = generate_pros_cons()
        st.success("Pros and cons generated.")
        st.dataframe(generated.head(20), use_container_width=True)

    st.markdown("### NLP Coverage")
    st.write(f"Total companies in master dataset: {len(master)}")

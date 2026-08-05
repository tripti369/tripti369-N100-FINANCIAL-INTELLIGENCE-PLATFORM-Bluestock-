import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import load_master


def app(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    st.title("🏦 Capital Structure")

    master = load_master()

    company = st.selectbox(
        "Select Company",
        sorted(master["company_name"].dropna().unique())
    )

    row = master[
        master["company_name"] == company
    ].iloc[0]

    book = pd.to_numeric(row["book_value"], errors="coerce")
    face = pd.to_numeric(row["face_value"], errors="coerce")

    capital = pd.DataFrame({
        "Metric": [
            "Face Value",
            "Book Value"
        ],
        "Value": [
            face,
            book
        ]
    })

    st.dataframe(capital, use_container_width=True)

    fig = px.bar(
        capital,
        x="Metric",
        y="Value",
        title=f"{company} Capital Structure"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.metric("Face Value", face)
    st.metric("Book Value", book)
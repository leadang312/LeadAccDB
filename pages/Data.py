import streamlit as st
import pandas as pd
import numpy as nps


# Page settings and headings
st.set_page_config(
    page_title='Database',
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# Page headers
st.title("📊 Analysis")
st.caption("Here you can view the data")

# Database
lead_db = pd.read_csv("./lead_db.csv", index_col='lead_id')
st.experimental_data_editor(lead_db)
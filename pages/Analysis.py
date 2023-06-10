import streamlit as st
import pandas as pd
import numpy as nps


# Page settings and headings
st.set_page_config(
    page_title='Analysis',
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# Page headers
st.title("📊 Analysis")
st.caption("Here we have some analysis of the data")

# Dbt users
lead_db = pd.read_csv("./lead_db.csv", index_col='lead_id')
st.write(f"**Dbt users:** {lead_db['note'].str.contains('dbt|Dbt', case=False).sum()}")
#st.experimental_data_editor(lead_db[lead_db['note'].str.contains('dbt|Dbt', case=False)])
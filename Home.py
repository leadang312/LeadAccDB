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
st.title("📊 Databases")
st.caption("Here you can view the data from all accounts and all leads")

# Download
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

# Leads
lead_db = pd.read_csv("./lead_db.csv", index_col='lead_id')
st.data_editor(lead_db)

csv = convert_df(lead_db)  
st.download_button(label="Download Leads",  data=csv, file_name='LeadList.csv', mime='text/csv')

# Accounts
st.write("")
acc_db = pd.read_csv("./acc_db.csv", index_col='acc_id')
st.data_editor(acc_db)

csv = convert_df(acc_db)  
st.download_button(label="Download Accounts",  data=csv, file_name='AccountList.csv', mime='text/csv')



import pandas as pd
import streamlit as st

# Page settings and headings
st.set_page_config(
    page_title='Campaigns',
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# Page headers
st.title("📊 Campaigns")
st.caption("Here you can see the campaigns with thei filters and results")

# Campaign data analysts
st.header("#1 Data Analysts that use dbt")

# Fpr Download
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

# Read Lead Database
df = pd.read_csv('lead_db.csv')

# First search
title_criteria = ['Data Analyst', 'Data Analytics']
skill_criteria = 'dbt'

filtered_df1 = df[
    (df['title'].str.contains('|'.join(title_criteria), case=False, na=False)) &
    (df['note'].str.contains(skill_criteria, case=False, na=False)) &
    ((df['sf_linkedin_url'].notnull()) | (df['linkedin_url'].notnull()))
]

st.experimental_data_editor(filtered_df1)

f"**Title:** {title_criteria}   **Skills:** {skill_criteria}   **Linkedin:** not null"
csv1 = convert_df(filtered_df1)  
st.download_button(label="Download Leads",  data=csv1, file_name='LeadList.csv', mime='text/csv')

# Second search
title_criteria = ['Data Analyst', 'Data Analytics']

filtered_df2 = df[
    (df['title'].str.contains('|'.join(title_criteria), case=False, na=False)) &
    ((df['sf_linkedin_url'].notnull()) | (df['linkedin_url'].notnull()))
]

st.experimental_data_editor(filtered_df2)

f"**Title:** {title_criteria}   **Linkedin** not null"
csv2 = convert_df(filtered_df2)  
st.download_button(label="Download Leads",  data=csv2, file_name='LeadList.csv', mime='text/csv')

# Third search
skill_criteria = 'dbt'

filtered_df3 = df[
    (df['note'].str.contains(skill_criteria, case=False, na=False)) &
    ((df['sf_linkedin_url'].notnull()) | (df['linkedin_url'].notnull()))
]

st.experimental_data_editor(filtered_df3)

f"**Skills:** {skill_criteria}   **Linkedin** not null"
csv3 = convert_df(filtered_df3)  
st.download_button(label="Download Leads",  data=csv3, file_name='LeadList.csv', mime='text/csv')
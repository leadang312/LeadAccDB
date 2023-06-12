import streamlit as st
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed
import pandas as pd
import numpy as np

# Page settings and headings
st.set_page_config(
    page_title='Salesforce Upload',
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# Page headers
st.title("📊 Salesforce Upload")
st.caption("Here you can add new leads to salesforce")

# Columns
required_cols = ["LastName", "FirstName", "Title", "Email", "Company", "OwnerId", "LinkedIn_profile__c", "Campaign_ID_Array__c", "Existing_Account__c", "Phone"]

### FIRST STEP: Lead List Upload
st.write("")
st.markdown(f"**1️⃣ FIRST STEP:** Log into Salesforce.")

col1, col2, col3, col4 = st.columns(4)   

with col1: desired_lead_owner_id = st.text_input("Owner ID", value="", key="Owner ID")
with col2: my_username = st.text_input("User Name", value="", key="User Name")
with col3: my_password = st.text_input("Password", value="", type="password", key="Password")
with col4: my_security_token = st.text_input("Security token", value="", key="Security token")

connect = st.button("Connect to Salesforce")

if desired_lead_owner_id != "" and my_username != "" and my_password != "" and my_security_token != "" and connect:
    sf = Salesforce(username=my_username, password=my_password, security_token=my_security_token)
    st.write("Connection successfull!")

#if st.button("Upload"):


if 'mapped' not in st.session_state:
    st.session_state.mapped = False

### SECOND STEP: Lead List Upload
st.write("")
st.markdown(f"**2️⃣ SECOND STEP:** Upload the lead list.")

lead_list = st.file_uploader("Upload the lead list.", key = "lead_list_uploader", label_visibility="collapsed")


if lead_list is not None:

    lead_df = pd.read_csv(lead_list)
    lead_df = st.experimental_data_editor(lead_df, key = "init_df")
    lead_list_cols = list(lead_df.columns)

    #### SECOND STEP: Mapping columns
    st.write("")
    st.markdown(f"**2️⃣ SECOND STEP:** Type in the column names of your lead list. By clicking map you rename them. You need to map firstname and lastname!")      
        
    cols = st.columns(5)   

    for idx, col in enumerate(required_cols):
        with cols[idx%5]:
            input = st.selectbox(col, ["No match"]+lead_list_cols)

        if input:
            if input != "No match":
                lead_df = lead_df.rename(columns={input:col})
    
    # Introducing state and setting it with map button
    if st.button('Map', key="map_button"):

        lead_list_cols = list(lead_df.columns)

        if ("firstname" in lead_list_cols and "lastname" in lead_list_cols) or "linkedin_url" in lead_list_cols:
            st.session_state.mapped = True
            
        else: 
            st.error("You need to set the firstname, lastname column or the linkedin_url column!", icon="🚨")
            
    
    ### THIRD STEP: Checking mapping
    if st.session_state.mapped:
        
        st.write("")
        st.markdown(f"**3️⃣ THIRD STEP:** Check if every column is renamed correctly.")

        # Preprocess lead_df
        for col in required_cols:

            if col not in list(lead_df.columns):
                lead_df[col] = np.nan

        lead_df = lead_df[required_cols].dropna(how='all', axis=1)
        lead_df = lead_df.reindex(columns=required_cols)

        lead_df['company_id'] = lead_df['company_id'].fillna("")
        lead_df['company_id'] = lead_df['company_id'].str.replace('www.', '').str.split('/').str[0]

        lead_df = lead_df.replace([""], np.nan)
        lead_df = st.experimental_data_editor(lead_df, key = "mapped_df")

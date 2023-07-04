import streamlit as st
import pandas as pd
import numpy as np

# Page settings and headings
st.set_page_config(
    page_title='Lead Database',
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# Page headers
st.title("📊 Lead Database")
st.caption("Here you can add new leads to the lead database")

# Macros
lead_db = pd.read_csv("./lead_db.csv", index_col='lead_id')
required_cols = ["lead_id", "company_id", "campaign_id", "firstname", "lastname", "title", "company", "country", "region", "email", "mobilephone", "officephone","phone", "sf_linkedin_url", "linkedin_url", "rating", "leadsource", "website", "note", "existing_acc"]

if 'mapped' not in st.session_state:
    st.session_state.mapped = False

if 'added' not in st.session_state:
    st.session_state.added = False

if 'name_idxer' not in st.session_state:
    st.session_state.name_idxer = True

        

### FIRST STEP: Lead List Upload
st.write("")
st.markdown(f"**1️⃣ FIRST STEP:** Upload the lead list.")

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
            options = ["No match"] + lead_list_cols
            input = st.selectbox(col, options)

        if input != "No match":
            lead_df = lead_df.rename(columns={input:col})
    
    # Introducing state and setting it with map button
    if st.button('Map', key="map_button"):

        lead_list_cols = list(lead_df.columns)

        if ("firstname" in lead_list_cols and "lastname" in lead_list_cols):
            st.session_state.name_idxer = True
            st.session_state.mapped = True
            
        elif "linkedin_url" in lead_list_cols:
            st.session_state.name_idxer = False
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
        lead_df = st.data_editor(lead_df, key = "mapped_df")

        ### FOURTH STEP: Adding leads to the database
        st.write("")
        st.markdown(f"**4️⃣ FOURTH STEP:** Add leads to the database.")

        # Introducig state and setting it with add button
        if st.button('Add to Lead Database', key="add_button"):
            st.session_state.added = True


    if st.session_state.added and st.session_state.mapped:

        # Adding lead_df to lead_db with progress bar
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        numb_leads = len(lead_df)

        # Iterating over new leads
        for idx, row in lead_df.iterrows():

            mask = None
            match = None

            if idx == 3:
                break
            
            lead_list_cols = list(lead_df.columns)


            if st.session_state.name_idxer:

                st.write("Fullname")
                firstname = row["firstname"]
                lastname = row["lastname"]
            
                mask = (lead_db['firstname'] == firstname) & (lead_db['lastname'] == lastname)
                match = lead_db[(lead_db['firstname'] == firstname) & (lead_db['lastname'] == lastname)]

            else:
                
                st.write("LinkedIn")
                linkedin_url = row["linkedin_url"]

                mask = lead_db['linkedin_url'] == linkedin_url
                match = lead_db[lead_db['linkedin_url'] == linkedin_url]

            if len(match) == 0:
                lead_db.loc[len(lead_db)] = row 

            else:
                for col in required_cols[1:]:   
                    if pd.isna(match.iloc[0][col]):
                        lead_db.loc[mask, col] = row[col]

            my_bar.progress(idx/numb_leads, text=progress_text)

        st.data_editor(lead_db)
        my_bar.empty()

        ### FIFTH STEP: Save the leads
        st.write("")
        st.markdown(f"**5️⃣ FIFTH STEP:** Check out the added leads and save them to the database.")

        if st.button('Save to Lead Database', key="save_button"):
                    
            st.session_state.mapped = False
            st.session_state.added = False

            del lead_list

            lead_db.to_csv("lead_db.csv")
            st.write("Leads Saved!")
import streamlit as st
import pandas as pd
import numpy as np


# Page settings and headings
st.set_page_config(
    page_title='Account Database',
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# Page headers
st.title("📊 Account Database")
st.caption("Here you can add new accounts to the acc database")

# Macros
acc_db = pd.read_csv("./acc_db.csv", index_col='acc_id')
required_cols = ["acc_id","sf_acc_id","company_id","linkedin_url","sf_linkedin_url","name","description","themes","city","country","website","founded","data_employees","totel_employees","stage_raised","stage_date","raised","owner","owner_email"]

if 'mapped' not in st.session_state:
    st.session_state.mapped = False

if 'added' not in st.session_state:
    st.session_state.added = False

### FIRST STEP: acc List Upload
st.write("")
st.markdown(f"**1️⃣ FIRST STEP:** Upload the account list.")

acc_list = st.file_uploader("Upload the acc list.", key = "acc_list_uploader", label_visibility="collapsed")


if acc_list is not None:

    acc_df = pd.read_csv(acc_list)
    acc_df = st.data_editor(acc_df, key = "init_df")
    acc_list_cols = list(acc_df.columns)

    #### SECOND STEP: Mapping columns
    st.write("")
    st.markdown(f"**2️⃣ SECOND STEP:** Type in the column names of your account list. By clicking map you rename them. You need to map firstname and lastname!")      
        
    cols = st.columns(5)   

    for idx, col in enumerate(required_cols):
        with cols[idx%5]:
            input = st.selectbox(col, ["No match"]+acc_list_cols)

        if input:
            if input != "No match":
                acc_df = acc_df.rename(columns={input:col})
    
    # Introducing state and setting it with map button
    if st.button('Map', key="map_button"):

        if "company_id" not in list(acc_df.columns):
            st.error("You need to set the domain column!", icon="🚨")
            
        else: 
            st.session_state.mapped = True
    
    ### THIRD STEP: Checking mapping
    if st.session_state.mapped:
        
        st.write("")
        st.markdown(f"**3️⃣ THIRD STEP:** Check if every column is renamed correctly.")

        # Preprocess acc_df
        for col in required_cols:

            if col not in list(acc_df.columns):
                acc_df[col] = np.nan

        acc_df = acc_df[required_cols].dropna(how='all', axis=1)
        acc_df = acc_df.reindex(columns=required_cols)

        acc_df['company_id'] = acc_df['company_id'].fillna("")
        acc_df['company_id'] = acc_df['company_id'].str.replace('www.', '').str.split('/').str[0]

        acc_df = acc_df.replace([""], np.nan)
        acc_df = st.data_editor(acc_df, key = "mapped_df")

        ### FOURTH STEP: Adding accs to the database
        st.write("")
        st.markdown(f"**4️⃣ FOURTH STEP:** Add accounts to the database.")

        # Introducig state and setting it with add button
        if st.button('Add to acc Database', key="add_button"):
            st.session_state.added = True


    if st.session_state.added and st.session_state.mapped:

        # Adding acc_df to acc_db with progress bar
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        numb_accs = len(acc_df)

        # Iterating over new accs
        for idx, row in acc_df.iterrows():

            domain = row["company_id"]

            mask = acc_db["company_id"] == domain
            match = acc_db[acc_db["company_id"] == domain]

            if len(match) == 0:
                acc_db.loc[len(acc_db)] = row 

            else:
                for col in required_cols[1:]:   
                    if pd.isna(match.iloc[0][col]):
                        acc_db.loc[mask, col] = row[col]

            my_bar.progress(idx/numb_accs, text=progress_text)

        st.data_editor(acc_db)
        my_bar.empty()

        ### FIFTH STEP: Save the accs
        st.write("")
        st.markdown(f"**5️⃣ FIFTH STEP:** Check out the added accounts and save them to the database.")

        if st.button('Save to acc Database', key="save_button"):
                    
            st.session_state.mapped = False
            st.session_state.added = False

            del acc_list

            acc_db.to_csv("acc_db.csv")
            st.write("Accountss Saved!")
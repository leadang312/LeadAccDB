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

st.title("📊 Lead Database")
st.caption("Here you can add new leads to the lead database")
st.write("")

# Macros
required_cols = ["lead_id", "company_id", "campaign_id", "firstname", "lastname", "title", "company", "country", "region", "email", "df_linkedin_url", "linkedin_url", "rating", "leadsource", "website", "note", "existing_acc"]
lead_db = pd.read_csv("./data/lead_db.csv", index_col='lead_id')

# Introducing states to create pop ups that stay
if 'mapped' not in st.session_state:
    st.session_state.mapped = 0

if 'added' not in st.session_state:
    st.session_state.added = 0

# Upload, map and save leads to db
def lead_list_upload():
    
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
        st.markdown(f"**2️⃣ SECOND STEP:** Type in the column names of your lead list. By clicking map you rename them.")      
        
        cols = st.columns(5)    

        for idx, col in enumerate(required_cols):
            with cols[idx%5]:
                text_input = st.selectbox(col, ["No match"]+lead_list_cols)

                #st.write('You selected:', option)
                #text_input = st.text_input(col, key = col)

            if text_input:
                if text_input != "No match":
                    lead_df = lead_df.rename(columns={text_input:col})

        if st.button('Map', key="map_button"):
            st.session_state.mapped += 1

        if st.session_state.mapped > 0:
            
            ### THIRD STEP: Checking mapping
            st.write("")
            st.markdown(f"**3️⃣ THIRD STEP:** Check if every column is renamed correctly.")
            lead_df = st.experimental_data_editor(lead_df, key = "mapped_df")

            ### FOURTH STEP: Adding leads to the database
            st.write("")
            st.markdown(f"**4️⃣ FOURTH STEP:** Add leads to the database.")

            if st.button('Add to Lead Database', key="add_button"):
                st.session_state.added += 1

            if st.session_state.added > 0:

                # Preprocess lead_df
                for col in required_cols:
                    if col not in list(lead_df.columns):
                        lead_df[col] = np.nan

                lead_df = lead_df[required_cols].dropna(how='all', axis=1)
                lead_df = lead_df.replace("", np.nan)
                lead_df = lead_df.reindex(columns=required_cols)

                # Adding lead_df to lead_db with progress bar
                progress_text = "Operation in progress. Please wait."
                my_bar = st.progress(0, text=progress_text)
                numb_leads = len(lead_df)

                # Iterating over new leads
                for idx, row in lead_df.iterrows():

                    firstname = row["firstname"]
                    lastname = row["lastname"]

                    mask = (lead_db['firstname'] == firstname) & (lead_db['lastname'] == lastname)
                    match = lead_db[(lead_db['firstname'] == firstname) & (lead_db['lastname'] == lastname)]

                    if len(match) == 0:
                        # Append for new leads
                        lead_db.loc[len(lead_db)] = row 

                    else:
                        # Fill in for old leads
                        for col in required_cols[1:]:   
                            if pd.isna(match.iloc[0][col]):
                                lead_db.loc[mask, col] = row[col]

                    my_bar.progress(idx/numb_leads, text=progress_text)

                st.experimental_data_editor(lead_db)
                my_bar.empty()

                ### FIFTH STEP: Save the leads
                st.write("")
                st.markdown(f"**5️⃣ FIFTH STEP:** Check out the added leads and save them to the database.")

                if st.button('Save to Lead Database', key="save_button"):
                    lead_db.to_csv("./data/lead_db.csv")
                    st.write("Leads Saved!")


def main():
    lead_list_upload()

if __name__ == '__main__':
    main()

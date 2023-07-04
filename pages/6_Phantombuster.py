import streamlit
import requests
import json
import pandas as pd
import numpy as np

headers = {
    'Content-Type': 'application/json',
    'x-phantombuster-key': '4nyJGsMxPo18HHM1TgZaOmr8B4IRIyUYRtmqcXzjQxk',
}

folder = "./dbt_analytics_engineer_phase_2"

def launch(data):
    """
    Launches an agent.

    Args:
        data (str): Post request information including the id and arguments for the launch.

    Returns:
        int: The ID of the container where the new results are stored
    """
    # VORHER
    # data = '{"id":"' + str(id) + '","argument":{"numberOfProfiles":2500,"extractDefaultUrl":false,"removeDuplicateProfiles":true,"sessionCookie":"AQEDAULM85MCOfA-AAABiACMrRAAAAGIJJkxEFYAmDLBQTfzXToA9uuWQnkKN0RA-jrRXPOfg8e0a7DUifmcho1WVgfiK7OoQinT9_w-7EIe3wwnQhVlOHjqxb5gCvVMd-FIdJTdliKMi2HOUOJVfZ30","searches":"' + search + '","numberOfResultsPerSearch":2500,"csvName":"SalesNavigatorList"}}'
    response = requests.post('https://api.phantombuster.com/api/v2/agents/launch', headers=headers, data=data)
    
    containerId = json.loads(response.text)['containerId']
    print("Launch successfull with containerId: ", containerId)

    return containerId


def extract(id, contid, path):
    """
    Extracts agent launch results and stores them in a csv file at path.

    Args:
        id (int): Agent id that launched the results
        contid (int): Container id where the results are stored.
        path (str): Location where csv should be stored.

    Returns:
        pandas.core.frame.DataFrame: Dataframe of the results
    """

    url = "https://api.phantombuster.com/api/v1/agent/{id}/output?mode=track&containerId=" + str(contid)
    output = json.loads(requests.get(url, headers=headers).text)['data']
    csv_url = json.loads(output['resultObject'])['csvURL']
    csv = requests.get(csv_url, headers=headers).text

    with open(path, "w") as file:
        file.write(csv)

    return pd.read_csv(f"{folder}/SalesNavigatorListDbt.csv")


def linkedIn_profiles(df):
    """
    Stores all the LinkedIn profiles in a csv file without an header.

    Args:
        df (pandas.core.frame.DataFrame): Dataframe with an exisiting column called 'linkedInProfileUrl'.
    """

    profiles = pd.DataFrame({ 'linkedInProfileUrl': df['linkedInProfileUrl'] })
    profiles.to_csv(f'{folder}/LinkedInProfiles.csv', header=False, index=False)


def sales_nav_profiles(df):
    """
    Stores all the LinkedIn Sales Navigator profiles in a csv file without an header.

    Args:
        df (pandas.core.frame.DataFrame): Dataframe with an exisiting column called 'profileUrl'.
    """

    profiles = pd.DataFrame({ 'profileUrl': df['profileUrl'] })
    profiles.to_csv(f'{folder}/SalesNavProfiles.csv', header=False, index=False)


def missing_leads(path_complete, path_part):
    """
    Compares the first column of two csv files

    Args: 
        path_complete(str): Path to csv file with all the leads with required column 'LINKEDIN_PROFILE__C'.
        path_part(str): Path to scv file where only part of the leads where processed with required column 'LINKEDIN_PROFILE__C'.
    """
    complete = pd.read_csv(path_complete)
    part = pd.read_csv(path_part)

    missing = pd.DataFrame(columns=['LINKEDIN_PROFILE__C'])

    for idx, row in complete.iterrows():
        if row['LINKEDIN_PROFILE__C'] not in list(part['query'].values):
            missing.loc[len(missing)] = row['LINKEDIN_PROFILE__C']

    missing.to_csv("/Users/leadang/Downloads/missing.csv", index=False)
    print("Missing Leads: ", len(missing))
    print("Leads: ", len(part))


def formit(zoominfo_path, cognism_path, phantombuster_path):
    """
    Modifies two dataframes so that they are ready for the LinkedIn Sales Navigator Upload.

    Args:
        zoominfo (pandas.core.frame.DataFrame): Dataframe with the required columns 'profileUrl', 'firstName', 'lastName', 'title', 'Email Address', 'Mobile phone', 
            'Contact Accuracy Score', 'Country', 'Website', 'Company Name', 'Within EU'
        cognism (pandas.core.frame.DataFrame): Dataframe with the required columns 'profileUrl','First Name', 'Last Name', 'Matched Job Title', 'Cognism Email', 
            'Direct', 'Mobile', 'Office', 'Person Country', 'Matched Web Site', 'Company Name Input'

    Returns:
        (pandas.core.frame.DataFrame, pandas.core.frame.DataFrame): The cognism and zoominfo file in the right LinekdIn Navigator Upload form.
    """
    zoominfo = pd.read_csv(zoominfo_path)
    cognism = pd.read_csv(cognism_path)
    phantombuster = pd.read_csv(phantombuster_path)

    # Define the required column names
    required_cols_zoominfo = ['profileUrl', 'firstName', 'lastName', 'title', 'Email Address', 'Mobile phone', 
                            'Contact Accuracy Score', 'Country', 'Website', 'Company Name', 'Within EU']
    required_cols_cognism = ['profileUrl','First Name', 'Last Name', 'Matched Job Title', 'Cognism Email', 
                            'Direct', 'Mobile', 'Office', 'Person Country', 'Matched Web Site', 'Company Name Input']  
    required_cols_phantombuster = ['query', 'firstName', 'lastName', 'currentJobTitle', 'emailAddress', 'currentCompanyName', 
                                   'location', 'phoneNumber', 'allSkills']


    # Remove columns that are not in the required columns list
    zoominfo = zoominfo[required_cols_zoominfo].dropna(how='all', axis=1)
    cognism = cognism[required_cols_cognism].dropna(how='all', axis=1)
    phantombuster = phantombuster[required_cols_phantombuster].dropna(how='all', axis=1)


    # Renaming 
    zoominfo = zoominfo.rename(columns={'profileUrl':'LINKEDIN_PROFILE__C', 'firstName':'FIRSTNAME', 'lastName':'LASTNAME', 
                                        'title':'TITLE', 'Email Address':'EMAIL','Mobile phone':'MOBILEPHONE', 
                                        'Contact Accuracy Score':'RATING', 'Country':'COUNTRY__C', 
                                        'Website':'WEBSITE', 'Company Name':'COMPANY','Within EU':'REGION__C'})

    cognism = cognism.rename(columns={'profileUrl':'LINKEDIN_PROFILE__C', 'First Name':'FIRSTNAME', 
                                      'Last Name':'LASTNAME','Matched Job Title':'TITLE', 'Cognism Email':'EMAIL',
                                      'Direct':'PHONE', 'Mobile':'MOBILEPHONE', 'Office':'OFFICE_PHONE__C',
                                      'Person Country':'COUNTRY__C', 'Matched Web Site':'WEBSITE', 
                                      'Company Name Input':'COMPANY'})
    
    phantombuster = phantombuster.rename(columns={'query':'LINKEDIN_PROFILE__C', 'firstName':'FIRSTNAME', 'lastName': 'LASTNAME', 
                                                  'currentJobTitle':'TITLE', 'emailAddress':'EMAIL', 'phoneNumber':'PHONE', 
                                                  'currentCompanyName':'COMPANY', 'website':'WEBSITE', 'location':'CITY', 'allSkills':'MESSAGE'})

    # Adding missing columns 
    zoominfo['CAMPAIGN_ID_ARRAY__C'] = 'dbt_analytics_engineer_phase_2'
    zoominfo['CITY'] = np.nan
    zoominfo['PHONE'] = np.nan
    zoominfo['OFFICE_PHONE__C'] = np.nan
    zoominfo['EXISTING_ACCOUNT__C'] = np.nan
    zoominfo['LEADSOURCE'] = 'demand_gen'
    zoominfo['NOTE'] = np.nan
    zoominfo['MESSAGE'] = np.nan

    cognism['CAMPAIGN_ID_ARRAY__C'] = 'dbt_analytics_engineer_phase_2'
    cognism['CITY'] = np.nan
    cognism['REGION__C'] = np.nan
    cognism['RATING'] = np.nan
    cognism['EXISTING_ACCOUNT__C'] = np.nan
    cognism['LEADSOURCE'] = 'demand_gen'
    cognism['NOTE'] = np.nan
    cognism['MESSAGE'] = np.nan

    phantombuster['CAMPAIGN_ID_ARRAY__C'] = 'dbt_analytics_engineer_phase_2'
    phantombuster['COUNTRY__C'] = np.nan
    phantombuster['LEADSOURCE'] = 'demand_gen'
    phantombuster['MOBILEPHONE'] = np.nan
    phantombuster['OFFICE_PHONE__C'] = np.nan
    phantombuster['RATING'] = np.nan
    phantombuster['REGION__C'] = np.nan
    phantombuster['NOTE'] = np.nan
    phantombuster['EXISTING_ACCOUNT__C'] = np.nan

    # Reordering the columns
    columns = ['CAMPAIGN_ID_ARRAY__C', 'COMPANY', 'CITY', 'COUNTRY__C', 'EMAIL', 'FIRSTNAME', 'LASTNAME', 'LEADSOURCE', 
               'LINKEDIN_PROFILE__C', 'MOBILEPHONE', 'OFFICE_PHONE__C', 'PHONE', 'RATING', 'REGION__C', 'TITLE', 
               'WEBSITE', 'NOTE', 'MESSAGE', 'EXISTING_ACCOUNT__C']

    zoominfo = zoominfo.reindex(columns=columns)
    cognism = cognism.reindex(columns=columns)
    phantombuster = phantombuster.reindex(columns=columns)

    # Improving quality of the cognism data
    cognism['PHONE'] = cognism['PHONE'].str.replace('\t', '')
    cognism['MOBILEPHONE'] = cognism['MOBILEPHONE'].str.replace('\t', '')
    cognism['OFFICE_PHONE__C'] = cognism['OFFICE_PHONE__C'].str.replace('\t', '')

    cognism = cognism.replace('DNC', np.nan)
    cognism = cognism.replace('TPS', np.nan)
    cognism = cognism.replace('CTPS', np.nan)
    cognism = cognism.replace('', np.nan)

    # Improving quality of the cognism data
    zoominfo = zoominfo.replace('', np.nan)
    cognism = cognism.replace('', np.nan)
    phantombuster = phantombuster.replace('', np.nan)

    zoominfo['NOTE'] = ''
    cognism['NOTE'] = ''
    phantombuster['NOTE'] = ''

    # Saving 
    zoominfo.to_csv(f"{folder}/ZoominfoMod.csv", index=False)
    cognism.to_csv(f"{folder}/CognismMod.csv", index=False)
    phantombuster.to_csv(f"{folder}/PhantombusterMod.csv", index=False)

    return zoominfo,cognism,phantombuster

def merge(zoominfo_path, cognism_path, phantombuster_path, evaluate):
    """
    Created a new csv file, that is ready for upload to LinkedIn Sales Navigator.

    Args:
        zoominfo_path (str): CSV file with the required columns 'profileUrl', 'firstName', 'lastName', 'title', 'Email Address', 'Mobile phone', 
            'Contact Accuracy Score', 'Country', 'Website', 'Company Name', 'Within EU'
        cognism_path (str): CSV file with the required columns 'profileUrl','First Name', 'Last Name', 'Matched Job Title', 'Cognism Email', 
            'Direct', 'Mobile', 'Office', 'Person Country', 'Matched Web Site', 'Company Name Input'

    Returns:
        (pandas.core.frame.DataFrame, pandas.core.frame.DataFrame): The merged dataframe with duplications stored in additional dataframe.
    """
    
    # Modifying the two dataframes
    zoominfo, cognism, phantombuster = formit(zoominfo_path, cognism_path, phantombuster_path)
    
    # merged is cognism in the beginning
    merged = cognism.copy() 
    duplic = pd.DataFrame(columns=['LINKEDIN_PROFILE__C', 'EMAIL', 'MOBILEPHONE'])
    
    # iterating through zoominfo to put into merged
    for z_idx, z_row in zoominfo.iterrows():
        
        # Extracting important information from zoominfo row
        linkedIn = z_row["LINKEDIN_PROFILE__C"]
        withInEU = z_row["REGION__C"]
        
        # Searching for same linkedIn profile in cognism/merged
        mask = (merged['LINKEDIN_PROFILE__C'] == linkedIn)
        c_df = merged[mask]
        
        # Has no match and need to be added to merged
        if len(c_df) == 0:
            merged.loc[len(merged)] = z_row.values

            
        # Has one match and information need to be added to row
        elif len(c_df) == 1:
            c_row = c_df.iloc[0]
            
            if withInEU == True: 
                
                # Checking for duplications that might still be useful
                if (c_row['EMAIL'] != z_row['EMAIL']) and not pd.isna(c_row['EMAIL']) and not pd.isna(z_row['EMAIL']):
                    duplic.loc[len(duplic)] = [z_row['LINKEDIN_PROFILE__C'], z_row['EMAIL'], np.nan]
                    
                cognism_numbers = [c_row['MOBILEPHONE'], c_row['OFFICE_PHONE__C'], c_row['PHONE']]
                unique_number = (z_row['MOBILEPHONE'] not in cognism_numbers) and not pd.isna(z_row['MOBILEPHONE'])
                
                if unique_number:
                    if pd.isna(c_row['OFFICE_PHONE__C']): 
                        merged.loc[mask, 'OFFICE_PHONE__C'] = z_row['MOBILEPHONE']
                        
                    elif pd.isna(c_row['PHONE']): 
                        merged.loc[mask, 'PHONE'] = z_row['MOBILEPHONE']
                        
                    elif not pd.isna(c_row['MOBILEPHONE']): 
                        duplic.loc[len(duplic)] = [z_row['LINKEDIN_PROFILE__C'], np.nan, z_row['MOBILEPHONE']]

                # Take cognism value except they are nan
                for col in list(merged.columns):
                    if pd.isna(c_row[col]):
                        merged.loc[mask, col] = z_row[col]
            
            else: 
                # Checking for duplications that might still be useful
                if (c_row['EMAIL'] != z_row['EMAIL']) and not pd.isna(c_row['EMAIL']) and not pd.isna(z_row['EMAIL']):
                    duplic.loc[len(duplic)] = [c_row['LINKEDIN_PROFILE__C'], c_row['EMAIL'], np.nan]
                
                cognism_numbers = [c_row['MOBILEPHONE'], c_row['OFFICE_PHONE__C'], c_row['PHONE']]
                unique_number = (z_row['MOBILEPHONE'] not in cognism_numbers) and not pd.isna(z_row['MOBILEPHONE'])
                
                if unique_number:
                    if pd.isna(c_row['OFFICE_PHONE__C']): 
                        merged.loc[mask, 'OFFICE_PHONE__C'] = z_row['MOBILEPHONE']
                        
                    elif pd.isna(c_row['PHONE']): 
                        merged.loc[mask, 'PHONE'] = z_row['MOBILEPHONE']
                        
                    elif not pd.isna(c_row['MOBILEPHONE']): 
                        duplic.loc[len(duplic)] = [c_row['LINKEDIN_PROFILE__C'], np.nan, c_row['MOBILEPHONE']]
                
                # Take zoominfo value except they are nan
                for col in list(merged.columns):
                    if not pd.isna(z_row[col]):
                        merged.loc[mask, col] = z_row[col]
                        
        # Has more than one match so zoominfo has duplicates    
        else: print("Error: Cognism or Zoominfo has duplicates!!!")


    # Iterate through whole merged dataframe and fill in missing values from phantombuster
    # NOT IDEAL: COMPARING IN MERGED CREATION DIRECTLY
    for idx, row in merged.iterrows():
        linkedIn = row["LINKEDIN_PROFILE__C"]
        mask = (phantombuster['LINKEDIN_PROFILE__C'] == linkedIn)
        match = phantombuster[mask]

        # Insert missing values from phantombuster
        for col in merged.columns:
            if pd.isna(row[col]):
                merged.at[idx, col] = match[col].values[0]

        # Handling duplicate EMAILS
        if (row['EMAIL'] != match['EMAIL'].values[0]) and not pd.isna(match['EMAIL'].values[0]):
            duplic.loc[len(duplic)] = [linkedIn, match['EMAIL'].values[0], np.nan]

        # Handling duplicate NUMBERS
        merged_numbers = [row['MOBILEPHONE'], row['OFFICE_PHONE__C'], row['PHONE']]
        unique_number = (match['PHONE'].values[0] not in merged_numbers) and not pd.isna(match[col].values[0])
                
        if unique_number:
            if pd.isna(row['OFFICE_PHONE__C']): 
                merged.at[idx, 'OFFICE_PHONE__C'] = match['PHONE'].values[0]
                        
            elif pd.isna(row['PHONE']): 
                merged.at[idx, 'PHONE'] = match['PHONE'].values[0]
                        
            elif not pd.isna(c_row['MOBILEPHONE']): 
                duplic.loc[len(duplic)] = [linkedIn, np.nan, match['PHONE'].values[0]]


    # Filling the duplicates in notes 
    # NOT IDEAL: BEST TO NOT EVEN CREATE DF BUT DIRECLTY INSERT IN NOTES
    for idx, row in duplic.iterrows():
        linkedIn = row["LINKEDIN_PROFILE__C"]
        mask = (merged['LINKEDIN_PROFILE__C'] == linkedIn)
        
        if not pd.isna(duplic.at[idx,'EMAIL']): merged.loc[mask, 'NOTE'] += f"Alternative Email: {duplic.at[idx,'EMAIL']} "
        if not pd.isna(duplic.at[idx,'MOBILEPHONE']): merged.loc[mask, 'NOTE'] += f"Alternative Number: {duplic.at[idx,'MOBILEPHONE']} "

    # Clean the merged csv file
    merged = merged.replace('', np.nan)
    merged.to_csv(f"{folder}/Merged.csv", index=False)
    duplic.to_csv(f"{folder}/Duplicates.csv", index=False)
    

    # Evaluate if necessary
    # NOT CORRECT NOT: ADDED PHANTOMBUSTER
    if evaluate:
        print("\n\n______________________________", "\nEVALUATION",  "\n------------------------------")
        print("Zoominfo length: ", len(zoominfo))
        print("Cognism length: ", len(cognism), '\n______________________________')
        print("Zoominfo non nan emails: ", zoominfo['EMAIL'].count())
        print("Cognism non nan emails: ", cognism['EMAIL'].count())

        unique_cognism = 0
        for idx, row in cognism.iterrows():
            if (not pd.isna(row["EMAIL"])) and (row["EMAIL"] not in list(zoominfo["EMAIL"].values)):
                unique_cognism += 1

        print("Unique Cognism Emails: ", unique_cognism)

        unique_zoominfo = 0
        for idx, row in zoominfo.iterrows():
            if (not pd.isna(row["EMAIL"])) and (row["EMAIL"] not in list(cognism["EMAIL"].values)):
                unique_zoominfo += 1

        print("Unique Zoominfo Emails: ", unique_zoominfo)

        cognism_and_zoominfo = 0
        for idx, row in cognism.iterrows():
            if (not pd.isna(row["EMAIL"])) and (row["EMAIL"] in list(zoominfo["EMAIL"].values)):
                cognism_and_zoominfo += 1

        print("Zoominfo Cognism Emails: ", cognism_and_zoominfo, '\n______________________________')

        print("Merged length: ", len(merged))
        print("Merged non nan emails: ", merged['EMAIL'].count())
        print("Merged non nan notes: ", merged['NOTE'].count())
        print("Duplic length: ", len(duplic))
        print("Duplic non nan emails: ", duplic['EMAIL'].count(), '\n______________________________')

        email_eval = (merged['EMAIL'].count() == unique_zoominfo + unique_cognism + (cognism_and_zoominfo - duplic['EMAIL'].count()))
        print("Emails Extraction: ", "Success" if email_eval else "Failed", "\n______________________________\n\n")

    return merged, duplic



def main():
    ### Launching LinkedIn Salves Nav search list extraction ###       
    argument_dict = {
        "numberOfProfiles":2500,
        "extractDefaultUrl":False,
        "removeDuplicateProfiles":True,
        "sessionCookie":"AQEDAULM85MCOfA-AAABiACMrRAAAAGIJJkxEFYAmDLBQTfzXToA9uuWQnkKN0RA-jrRXPOfg8e0a7DUifmcho1WVgfiK7OoQinT9_w-7EIe3wwnQhVlOHjqxb5gCvVMd-FIdJTdliKMi2HOUOJVfZ30",
        "searches":"https://www.linkedin.com/sales/search/people?query=(spellCorrectionEnabled%3Atrue%2CrecentSearchParam%3A(id%3A2732368940%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3ACURRENT_COMPANY%2Cvalues%3AList((id%3A10893210%2Ctext%3Adbt%2520Labs%2CselectionType%3AEXCLUDED)))%2C(type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList((id%3AC%2Ctext%3A11-50%2CselectionType%3AINCLUDED)%2C(id%3AD%2Ctext%3A51-200%2CselectionType%3AINCLUDED)%2C(id%3AE%2Ctext%3A201-500%2CselectionType%3AINCLUDED)%2C(id%3AF%2Ctext%3A501-1000%2CselectionType%3AINCLUDED)))%2C(type%3AREGION%2Cvalues%3AList((id%3A102221843%2Ctext%3ANorth%2520America%2CselectionType%3AINCLUDED)%2C(id%3A103644278%2Ctext%3AUnited%2520States%2CselectionType%3AINCLUDED)%2C(id%3A91000007%2Ctext%3AEMEA%2CselectionType%3AINCLUDED)%2C(id%3A100506914%2Ctext%3AEurope%2CselectionType%3AINCLUDED)%2C(id%3A101165590%2Ctext%3AUnited%2520Kingdom%2CselectionType%3AINCLUDED)%2C(id%3A91000006%2Ctext%3ADACH%2CselectionType%3AINCLUDED)))%2C(type%3ACOMPANY_HEADQUARTERS%2Cvalues%3AList((id%3A102221843%2Ctext%3ANorth%2520America%2CselectionType%3AINCLUDED)%2C(id%3A91000007%2Ctext%3AEMEA%2CselectionType%3AINCLUDED)))%2C(type%3AYEARS_AT_CURRENT_COMPANY%2Cvalues%3AList((id%3A1%2Ctext%3ALess%2520than%25201%2520year%2CselectionType%3AINCLUDED)%2C(id%3A2%2Ctext%3A1%2520to%25202%2520years%2CselectionType%3AINCLUDED)%2C(id%3A3%2Ctext%3A3%2520to%25205%2520years%2CselectionType%3AINCLUDED)%2C(id%3A4%2Ctext%3A6%2520to%252010%2520years%2CselectionType%3AINCLUDED)))%2C(type%3ATITLE%2Cvalues%3AList((text%3A%2522analytics%2520engineer%2522%2CselectionType%3AINCLUDED))%2CselectedSubFilter%3ACURRENT))%2Ckeywords%3A%2522dbt%2522)&sessionId=AuI7isNtSXmBu5jymgmYuA%3D%3D&viewAllFilters=true",
        "numberOfResultsPerSearch":2500,
        "csvName":"SalesNavigatorList"
    }

    data_dict = {
        "id":1292263820451514,
        "argument":argument_dict
    }

    data = json.dumps(data_dict)
    # ----> containerId = launch(id, data)
   

    ### Extracting LinkedIn Sales Nav search list ###                 
    id = 1292263820451514
    contid = 8189542453129171
    path = f"{folder}/SalesNavigatorListDbt.csv"
    # ----> df = extract(id, contid, path)


    ### Merging cognism and zoominfo dataframes
    zoominfo_path = f"{folder}/Zoominfo.csv"
    cognism_path = f"{folder}/Cognism.csv"
    phantombuster_path = f"{folder}/Phantombuster.csv"
    #formit(zoominfo_path, cognism_path, phantombuster_path)
    merge(zoominfo_path, cognism_path, phantombuster_path, True)

    
if __name__ == '__main__':
    main()

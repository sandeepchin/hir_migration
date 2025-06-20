#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Code to map provider data into provider tables
import pandas as pd
import numpy as np

#from project_main.provider_mapper_standalone import webiz_provider


class Provider:

    def __init__(self):
        self.df_sp = pd.DataFrame()
        self.df_db = pd.DataFrame()
        self.parent_child=pd.DataFrame()
        self.webiz_provider=pd.DataFrame()

        self.combine_data()

        print('Sharepoint file has',len(self.df_sp),'entries')
        print('Database has',len(self.df_db), 'entries')
        self.prepare_data()

    def combine_data(self):
        sharepoint1 = '../providers/parent_child_orgs_list_with_addresses_sharepoint.xlsx'
        sharepoint2 = '../providers/stand_alone_orgs_with_addresses_sharepoint.xlsx'
        db1 = 'input/parent_child_orgs_list_with_addresses.csv'
        db2 = 'input/stand_alone_orgs_with_addresses.csv'
        df_sp1 = pd.DataFrame(pd.read_excel(sharepoint1,dtype={'WebIZ Provider Zip':str,'WebIZ Clinic Zip':str},na_filter=False))
        df_sp2 = pd.DataFrame(pd.read_excel(sharepoint2,dtype={'WebIZ Provider Zip':str,'WebIZ Clinic Zip':str},na_filter=False))
        #print(df_sp1.columns)
        #print(df_sp2.columns)
        self.df_sp = pd.concat([df_sp1,df_sp2])
        self.df_sp.reset_index(drop=True,inplace=True)
        #print(self.df_sp.info())
        df_db1 = pd.read_csv(db1,dtype={'LEGACY_CLINIC_ID':int},na_filter=False)
        df_db2 = pd.read_csv(db2,dtype={'LEGACY_CLINIC_ID':int},na_filter=False)
        #print(df_db1.columns)
        #print(df_db2.columns)
        self.df_db = pd.concat([df_db1,df_db2])
        self.df_db.reset_index(drop=True,inplace=True)
        #print(self.df_db.info())

    def is_contained(self,df_set1,df_set2,key):
        # Check orgs in db that are not in sharepoint
        codes = list(df_set1.loc[:, key])
        somelist = []
        for code in df_set2.loc[:, key]:
            if code not in codes:
                somelist.append(code)
        return somelist

    def prepare_data(self):

        # Keep the webiz provider category code from DB and drop it from share point since db is more accurate 6/3/2025
        self.df_db = self.df_db.drop(
            ['LEGACY_PARENT_ORG_ID', 'HL7_SENDER','WebIZ_Provider', 'WebIZ_Provider_Street_Address', 'WebIZ_Provider_City', 'WebIZ_Provider_County',
             'WebIZ_Provider_Zip',  'WebIZ_Provider_Type_of_Practice'], axis=1)

        self.df_sp = self.df_sp.drop(
            ['LEGACY_PARENT_ORG_ID', 'HL7_SENDER', 'WebIZ_Provider_Category_Code','WebIZ_Clinic', 'ACTIVE', 'WebIZ_Clinic_Street_Address',
             'WebIZ_Clinic_City', 'WebIZ_Clinic_County', 'WebIZ_Clinic_Zip', 'WebIZ_Clinic_Category_Code',
             'WebIZ_Clinic_State'], axis=1)

        # Replace underscore with spaces to be consistent with share point file
        for col in self.df_db.columns:
            self.df_db.rename(columns={col:col.replace('_',' ')},inplace=True)

        for col in self.df_sp.columns:
            self.df_sp.rename(columns={col:col.replace('_',' ')},inplace=True)

        somelist = self.is_contained(self.df_sp,self.df_db,'LEGACY CLINIC ID')
        # codes
        print('Orgs in DB but not in SP')
        print(somelist)
        somelist = self.is_contained(self.df_db, self.df_sp,'LEGACY CLINIC ID')
        print('Orgs in SP but not in DB')
        print(somelist)

        # Merge the two dataframes
        df_merge = self.df_db.merge(self.df_sp, on='LEGACY CLINIC ID')
        # replace any nan values
        df_merge = df_merge.replace(np.nan,'')

        #print(df_merge.columns)

        # This is useful later for parent-child relationship
        self.parent_child = df_merge[['WebIZ Provider', 'LEGACY CLINIC ID', 'WebIZ Clinic']]
        # Clean up
        self.parent_child.loc[:, 'WebIZ Provider'] = [provider.replace(",", "").strip() for provider in self.parent_child.loc[:, 'WebIZ Provider']]
        self.parent_child.loc[:, 'WebIZ Clinic'] = [clinic.replace(",", "").strip() for clinic in self.parent_child.loc[:, 'WebIZ Clinic']]

        # Standardize city, county, and all columns before removing duplicates
        self.webiz_provider = df_merge[['WebIZ Provider', 'WebIZ Provider Street Address', 'WebIZ Provider City', 'WebIZ Provider County',
                                        'WebIZ Provider State', 'WebIZ Provider Zip', 'WebIZ Provider Category Code']]

        self.webiz_provider.loc[:, 'WebIZ Provider City'] = [city.replace(",", "").title().strip() for city in self.webiz_provider.loc[:, 'WebIZ Provider City']]
        self.webiz_provider.loc[:, 'WebIZ Provider County'] = [county.replace(",", "").title().strip() for county in self.webiz_provider.loc[:, 'WebIZ Provider County']]
        self.webiz_provider.loc[:, 'WebIZ Provider Street Address'] = [address.replace(",", "").strip() for address in self.webiz_provider.loc[:, 'WebIZ Provider Street Address']]
        self.webiz_provider.loc[:, 'WebIZ Provider'] = [provider.replace(",", "").strip() for provider in self.webiz_provider.loc[:, 'WebIZ Provider']]
        #self.webiz_provider.loc[:, 'WebIZ Provider Zip'] = [zip.strip() for zip in self.webiz_provider.loc[:, 'WebIZ Provider Zip']]

        print('Length of provider list',len(self.webiz_provider))
        # Drop duplicates (considering all columns)
        self.webiz_provider=self.webiz_provider.drop_duplicates(ignore_index=True)
        print('Length of provider list after dropping duplicates', len(self.webiz_provider))

    def get_provider_type_of_practice(self):
        # Get provider type of practice data from manually created file
        df_prov_type_of_practice1 = pd.read_csv('../providers/webiz_provider_remove_duplicates.csv', na_filter=False)
        # Get provider type of practice data for standalone providers
        df_prov_type_of_practice2 = pd.read_csv('../providers/stand_alone_providers_duplicates_removed.csv', na_filter=False)

        # combine
        df_prov_type_of_practice = pd.concat([df_prov_type_of_practice1,df_prov_type_of_practice2])
        # reset index
        df_prov_type_of_practice.reset_index(drop=True,inplace=True)

        # Collect rows of interest
        df_prov_type_of_practice = df_prov_type_of_practice[['WebIZ Provider', 'WebIZ Provider Type of Practice']]

        df_prov_type_of_practice.loc[:, 'WebIZ Provider'] = [provider.replace(",", "").strip() for provider in
                                                df_prov_type_of_practice.loc[:, 'WebIZ Provider']]

        # Check if this list is contained in webiz provider list
        somelist = self.is_contained(df_prov_type_of_practice, self.webiz_provider,'WebIZ Provider')
        print("Orgs in webiz provider but not in prov type of practice file")
        print(somelist)
        # Check if webiz provider list is contained within prov type of practive file
        somelist = self.is_contained(self.webiz_provider,df_prov_type_of_practice,'WebIZ Provider')
        print("Orgs in prov type of practice file but not in webiz provider")
        print(somelist)

        # Merge prov type of practice with webiz_provider data
        self.webiz_provider = self.webiz_provider.merge(df_prov_type_of_practice, on='WebIZ Provider')
        print('Num of entries after merge',len(self.webiz_provider))
        self.webiz_provider = self.webiz_provider.replace(np.nan,'')

        # Drop duplicates (considering all columns)
        self.webiz_provider.drop_duplicates(inplace=True, ignore_index=True)
        print('Length of provider list after dropping duplicates', len(self.webiz_provider))

        # Check if any entries are null
        results = self.webiz_provider[self.webiz_provider['WebIZ Provider Type of Practice'].isna()]
        print('Any null entries for provider type of practice')
        if len(results)==0:
            print('No')
        else:
            print('Yes',results)

    # Map provider category to an id
    def get_category_code(self):

        # Mapping of categories to an id
        category_mapping = [
            (1, 'Public Health'),
            (2, 'Public Provider'),
            (3, 'Private Provider'),
            (4, 'Pharmacy'),
            (5, 'Federal Partners'),
            (6, 'Immunization Registry'),
            (7, 'Provider Office/Clinic'),
            (8, 'School'),
            (9, 'Pre-School/DC Day Care/Head Start'),
            (10, 'Post-secondary School'),
            (11, 'EMR'),
            (12, 'Health Insurer'),
            (13, 'Corrections'),
            (14, 'Nursing Home/Long Term Care'),
            (15, 'Birthing Hospital'),
            (16, 'Hospital'),
            (17, 'DOH'),
            (18, 'ER/Urgent Care'),
            (19, 'External'),
            (20, 'Other')
        ]
        category_dict = {}
        for t in category_mapping:
            category_dict[t[1]] = t[0]
        # Map Inactive to Other
        self.webiz_provider.loc[:, 'WebIZ Provider Category Code'] = [category_dict[category.strip()] if category.strip()!='Inactive' else 20 for category in
                                                               self.webiz_provider.loc[:, 'WebIZ Provider Category Code']]

        # Hard coding some providers because database category codes associated with clinics are being assigned to providers
        hard_code_list = [{'name':'Adventist Health Castle','category_code':16},
                          {'name':'BYU Hawaii Health Services','category_code':10},
                          {'name':'Boyuan Cao','category_code':7},
                          {'name':'DOH IMB Hepatitis B HHC Vaccination Clinic','category_code':17},
                          {'name':'HHSC East Hawaii Region','category_code':16},
                          {'name':'HHSC Kauai Region','category_code':16},
                          {'name':'HICHC West','category_code':7},
                          {'name':'Hawaii HOME Project','category_code':7},
                          {'name':'Hawaii Keiki','category_code':7},
                          {'name':'Hawaii State Hospital','category_code':17},
                          {'name':'Iao Intermediate 404','category_code':8},
                          {'name':'Joel Kobayashi','category_code':7},
                          {'name':'Kahala Pediatrics','category_code':7},
                          {'name':'Kahuku Medical Center','category_code':16},
                          {'name':'Kaiser Maui','category_code':16},
                          {'name':'Kaiser Oahu','category_code':16},
                          {'name':'Kapiolani','category_code':16},
                          {'name':'Kauai District Health Office','category_code':17},
                          {'name':'Kona Community Hospital','category_code':16},
                          {'name':'Liberty Dialysis Hawaii','category_code':7},
                          {'name':'Liberty Dialysis Oahu','category_code':7},
                          {'name':'Life Care Center','category_code':14},
                          {'name':'Maui Health','category_code':16},
                          {'name':'Maui Medical Group','category_code':7},
                          {'name':'Molokai General Hospital','category_code':16},
                          {'name':'Pali Momi','category_code':16},
                          {'name':'Pharmacare','category_code':4},
                          {'name':"Queen's Medical Center",'category_code':16},
                          {'name':"Queen's Medical Center West Oahu",'category_code':16},
                          {'name':"Queen's North Hawaii Community Hospital",'category_code':16},
                          {'name':'Rehabilitation Hospital of the Pacific','category_code':16},
                          {'name':'Safeway Pharmacy','category_code':4},
                          {'name':"Shriners Children's Hawaii",'category_code':16},
                          {'name':'St Joseph School 1105','category_code':8},
                          {'name':'Straub Oahu','category_code':16},
                          {'name':'Times Pharmacy Oahu West Region','category_code':4},
                          {'name':'UCERA Oahu','category_code':7},
                          {'name':'US Renal Care','category_code':7},
                          {'name':"University Women's Health Specialists",'category_code':7},
                          {'name':'WCCHC Waianae','category_code':7},
                          {'name':'West Kauai Medical Center/KVMH','category_code':16},
                          {'name':'Wilcox','category_code':16}
                          ]
        for item in hard_code_list:
            sub_df= self.webiz_provider[self.webiz_provider['WebIZ Provider']==item['name']]
            for idx in sub_df.index:
                self.webiz_provider.loc[idx,'WebIZ Provider Category Code'] = item['category_code']

        print('Category code mapped')
        # Drop duplicates (considering all columns)
        self.webiz_provider = self.webiz_provider.drop_duplicates(ignore_index=True)
        self.webiz_provider.reset_index(drop=True,inplace=True)
        print('Length of provider list after dropping duplicates', len(self.webiz_provider))

    # Map prov type of practice to codes
    def get_practice_code(self):
        # Shorten the names to less than 35 characters because of DB restriction....add more as needed
        cat_list = []
        for category in self.webiz_provider.loc[:, 'WebIZ Provider Type of Practice']:
            if category == 'Private Hospital as agent of FQHC or RHC':
                cat_list.append('Private Hospital as FQHC/RHC')
            elif category == 'Other Public Health as agent of FQHC or RHC':
                cat_list.append('Public Other as FQHC/RHC')
            elif category == 'Private Practice as agent of FQHC/RHC':
                cat_list.append('Private Practice as FQHC/RHC')
            else:
                cat_list.append(category)

        self.webiz_provider.loc[:, 'WebIZ Provider Type of Practice'] = cat_list

        practice_type = [(1, 'FQHC/RHC'),
                         (2, 'Public Health Department'),
                         (3, 'Health Department as FQHC/RHC'),
                         (4, 'Public Hospital'),
                         (5, 'Public Hospital as FQHC/RHC'),
                         (6, 'Public Other'),
                         (7, 'Public Other as FQHC/RHC'),
                         (8, 'Private Hospital'),
                         (9, 'Private Hospital as FQHC/RHC'),
                         (10, 'Private Other'),
                         (11, 'Private Other as FQHC/RHC'),
                         (12, 'Private Practice'),
                         (13, 'Private Practice as FQHC/RHC'),
                         (14, 'Other Immunization Project'),
                         (15, 'Adolescent Only Provider - Private'),
                         (16, 'Adolescent Only Provider - Public'),
                         (17, 'Birthing Hospital'),
                         (18, 'Community Health Center - Private'),
                         (19, 'Community Health Center - Public'),
                         (20, 'Correctional Facility'),
                         (21, 'Drug Treatment Facility'),
                         (22, 'Juvenile Detention Center'),
                         (23, 'Migrant Health Facility'),
                         (24, 'Pharmacy'),
                         (25, 'Refugee Health Clinic'),
                         (26, 'School Based Clinic - Private'),
                         (27, 'School Based Clinic - Public'),
                         (28, 'Special Vaccine Clinic - Private'),
                         (29, 'Special Vaccine Clinic - Public'),
                         (30, 'Teen Health Center - Private'),
                         (31, 'Teen Health Center - Public'),
                         (32, 'Tribal or IHS Center')]
        # Map types to codes
        practice_type_dict = {}
        for t in practice_type:
            practice_type_dict[t[1]] = t[0]

        somelist = []
        for p_type in self.webiz_provider.loc[:, 'WebIZ Provider Type of Practice']:
            try:
                somelist.append(practice_type_dict[p_type])
            except:
                somelist.append('')

        self.webiz_provider.loc[:, 'WebIZ Provider Type of Practice'] = somelist

        print('Provider type of practice mapped')

    def build_csv(self):
        # Convert webiz_provider to a csv with appropriate column names
        self.webiz_provider =self.webiz_provider.sort_values(by=['WebIZ Provider'],ignore_index=True)

        # Add a fake webiz provider as parent for "patient record" clinic with doh address
        new_prov = pd.DataFrame([{'WebIZ Provider': 'Patient Record Provider',
                                  'WebIZ Provider Street Address': '1250 Punchbowl St',
                                  'WebIZ Provider City': 'Honolulu',
                                  'WebIZ Provider County': 'Honolulu', 'WebIZ Provider State': 'HI',
                                  'WebIZ Provider Zip': '96813',
                                  'WebIZ Provider Category Code': 1, 'WebIZ Provider Type of Practice': 2}])

        self.webiz_provider = pd.concat([self.webiz_provider, new_prov])
        self.webiz_provider.reset_index(drop=True, inplace=True)

        # Add Patient Record clinic to parent_child
        new_parent_child = pd.DataFrame([{'WebIZ Provider': 'Patient Record Provider', 'LEGACY CLINIC ID': '99999',
                                          'WebIZ Clinic': 'Patient Record'}])
        self.parent_child = pd.concat([self.parent_child, new_parent_child])
        self.parent_child.reset_index(drop=True, inplace=True)

        # Map provider name to provider id
        provider_map={}
        #print(self.webiz_provider.columns)

        # Set status to A for all providers
        self.webiz_provider['status_code']= 'A'

        # Rename columns
        self.webiz_provider.rename(columns={'WebIZ Provider':'provider_desc','WebIZ Provider Street Address':'mailing_address_line1',
                                            'WebIZ Provider City':'mailing_address_city','WebIZ Provider County':'mailing_address_county',
                                            'WebIZ Provider State':'mailing_address_state','WebIZ Provider Zip':'mailing_address_zip',
                                            'WebIZ Provider Category Code':'provider_category_code_id',
                                            'WebIZ Provider Type of Practice':'provider_type_of_practice_code_id'},inplace=True)
        id = 500000
        i=0
        while i<len(self.webiz_provider):
            self.webiz_provider.loc[i,'provider_unique_id']=id
            # Associate provider name with id
            provider_map[self.webiz_provider.loc[i,'provider_desc']] = id
            id+=1
            i+=1

        # Set Patient Record Provider ID to 99999 (Cindy's recommendation 4/2/25)
        last_index=len(self.webiz_provider)-1
        self.webiz_provider.loc[last_index,'provider_unique_id']=99999
        provider_map[self.webiz_provider.loc[last_index, 'provider_desc']] = 99999

        # Make sure provider id is int
        self.webiz_provider['provider_unique_id'] =self.webiz_provider['provider_unique_id'].astype(int)

        # Determine physical address
        self.webiz_provider.loc[:,'physical_address_line1'] = [street for street in self.webiz_provider.loc[:,'mailing_address_line1']]
        self.webiz_provider.loc[:,'physical_address_city'] =[city for city in self.webiz_provider.loc[:,'mailing_address_city']]
        self.webiz_provider.loc[:,'physical_address_county'] =[county for county in self.webiz_provider.loc[:,'mailing_address_county']]
        self.webiz_provider.loc[:,'physical_address_state']=[state for state in self.webiz_provider.loc[:,'mailing_address_state']]
        self.webiz_provider.loc[:,'physical_address_zip'] = [zip for zip in self.webiz_provider.loc[:,'mailing_address_zip']]

        # Messes with some names so removing
        #self.webiz_provider.loc[:,'provider_desc'] = [name.title() for name in self.webiz_provider.loc[:,'provider_desc']]

        # write webiz_provider to csv
        self.webiz_provider.to_csv('db_files/providers_bulk_insert.csv',index=False)

        # map provider name to corresponding id
        self.parent_child.loc[:, 'WebIZ Provider ID'] = [provider_map[prov] for prov in self.parent_child.loc[:, 'WebIZ Provider']]
        self.parent_child.to_csv('../webiz_child.csv', index=False)
        print('Num of webiz providers written',len(self.webiz_provider))
        print('webiz child file written')

# The end






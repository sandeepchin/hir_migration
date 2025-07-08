
#  Copyright (c) 2025. Sandeep Chintabathina

# Code to map vaccinations into vaccinations container

import pandas as pd
import numpy as np
# Import datetime
from datetime import datetime,date
pd.options.mode.chained_assignment = None


class Vaccinations:

    def __init__(self):
        names=["OTHER_IDENTIFIER","VACCINATION_IDENTIFIER","VACCINATION_DATE","CVX_CODE","MVX_CODE","LOT_NUMBER","NDC_NUMBER",
               "FUNDING_SOURCE_ID","EXPIRATION_DATE","BODY_SITE_CODE_ID","BODY_ROUTE_CODE_ID","DOSAGE_ML","REACTION_FLAG",
               "HISTORICAL_FLAG","CLINIC_UNIQUE_ID","VFC_CODE_ID","CREATION_DATE","UPDATED_DATE","LEGACY_CREATED_BY_NAME",
               "LEGACY_CREATED_BY_ID","LEGACY_UPDATED_BY_NAME","LEGACY_UPDATED_BY_ID","VIS_NAMES","VIS_DATES",
               "RECORD_SOURCE_ID","DELETED_FLAG","HEALTH_INSURANCE_CODE_ID","INSURANCE_ID","DATE_LAST_VERIFIED"]

        self.df_vax = pd.read_csv('input/vaccination_data.csv',sep=',',on_bad_lines='warn',na_filter=False,
                                  dtype={'OTHER_IDENTIFIER':str,'VACCINATION_IDENTIFIER':str,'CVX_CODE':str,'DOSAGE_ML':str,'CLINIC_UNIQUE_ID':str,
                                         'LEGACY_CREATED_BY_ID':str,"LEGACY_UPDATED_BY_ID":str,"RECORD_SOURCE_ID":str})

        self.df_adverse_reaction = pd.read_csv('input/vaccine_adverse_reactions.csv',na_filter=False)

        #print(self.df_vax['vis_names'].value_counts(dropna=False))

        #print(self.df_vax['DATE_LAST_VERIFIED'].value_counts(dropna=False))
        #print(self.df_vax['INSURANCE_ID'].value_counts(dropna=False))
        #print(self.df_vax['FUNDING_SOURCE_ID'].value_counts(dropna=False))

        self.df_vax=self.df_vax.drop(['DATE_LAST_VERIFIED','INSURANCE_ID'],axis=1)

        print(self.df_vax.info())
        self.prepare_vaccinations()


    def compare_with_patients(self):
        # Get existing patients from patient container
        df_patients = pd.read_csv('db_files/patients_bulk_insert.csv', dtype={'other_identifier': str},
                                  encoding='latin-1', na_filter=False,low_memory=False)
        # Extract id and dob
        df_patients_sub = df_patients[['other_identifier','dob']]
        # Merge with vax data
        df_outer = pd.merge(self.df_vax, df_patients_sub, on='other_identifier', how='outer', indicator=True)
        # Limit df_vax to common entries only
        self.df_vax = df_outer[df_outer['_merge'] == 'both']
        self.df_vax = self.df_vax.drop(['_merge'], axis=1)
        self.df_vax = self.df_vax.replace(np.nan, '')

        # There are patients without any vaccinations. Are these patients that opted out?
        patients_no_vax = df_outer[df_outer['_merge'] == 'right_only']
        patients_no_vax = patients_no_vax[['other_identifier']]
        patients_no_vax.to_csv('../vaccinations/patients_with_no_vax.csv',index=False)

        print('Compared with patients - reduced to',len(self.df_vax),'entries')

    # Calculate age at vax time (to determine vfc status later)
    def calculate_age(self):
        dobs = [datetime.strptime(dob, '%Y-%m-%d').date() for dob in self.df_vax.loc[:, 'dob']]
        vax_dates = [datetime.strptime(d, '%m/%d/%Y').date() for d in self.df_vax.loc[:, 'vaccination_date']]

        self.df_vax.loc[:, 'age'] = [vax_date.year - dob.year - ((vax_date.month, vax_date.day) < (dob.month, dob.day))
                                    for vax_date, dob in zip(vax_dates, dobs)]

        odd_records = self.df_vax[self.df_vax['age']<0]
        odd_records.to_csv('../vaccinations/vax_date_before_dob.csv',index=False)

        # Retain some odd vaccinations - these are in the UI and not just in the backend DB
        exclude_list = ['4257412','5904743','1337338','853049','13958840']

        self.df_vax = self.df_vax[self.df_vax['age']>=0]

        for id in exclude_list:
            rec = odd_records[odd_records['vaccination_identifier']==id]
            self.df_vax = pd.concat([self.df_vax,rec])
            self.df_vax.reset_index(drop=True, inplace=True)

        '''
        remove_list = list(odd_records.loc[:,'vaccination_identifier'])
        # Remove odd vaccinations
        for id in remove_list:
            if id not in exclude_list:
                results = self.df_vax[self.df_vax['vaccination_identifier']==id]
                for idx in results.index:
                    self.df_vax= self.df_vax.drop(idx,axis=0)
        self.df_vax.reset_index(drop=True, inplace=True)
        '''
        print('Removing odd vax before dob records - new size is',len(self.df_vax))

        print('Age calculated')

    # Calculate VFC codes for blank ones based on age
    def calculate_vfc_codes(self):
        # Mapping vfc values to id fields from the table
        vfc_code_ids = [(1, 'V00'),
                        (2, 'V01'),
                        (3, 'V02'),
                        (4, 'V03'),
                        (5, 'V04'),
                        (6, 'V05'),
                        (7, 'V07'),
                        (8, 'V22'),
                        (9, 'V23'),
                        (10, 'HI01'),
                        (11, 'HI02'),
                        (12, 'HI03'),
                        (13, 'HI04'),
                        (14, 'HI05')]

        vfc_code_dict = {}
        for t in vfc_code_ids:
            vfc_code_dict[t[1]] = t[0]

        self.df_vax.loc[:, 'vfc_code_id'] = ['' if code == '' else vfc_code_dict[code] for code in
                                            self.df_vax.loc[:, 'vfc_code_id']]
        # if age<=18 then V00 (1)
        # else V01 (2)
        ages = self.df_vax.loc[:, 'age']
        codes = self.df_vax.loc[:, 'vfc_code_id']

        self.df_vax.loc[:, 'vfc_code_id'] = [code if code != '' else 1 if age <= 18 else 2 for code, age in
                                            zip(codes, ages)]
        # Drop age and dob
        self.df_vax.drop(['dob', 'age'], axis=1, inplace=True)
        print('VFC codes calculated')

    # Compare vaccinations with clinics
    def compare_with_clinics(self):
        # Get existing clinics from clinics container
        df_clinics = pd.read_csv('db_files/clinics_bulk_insert.csv', dtype={'clinic_unique_id': str},
                                  na_filter=False)
        df_clinics_sub = df_clinics[['clinic_unique_id', 'clinic_desc']]
        # Merge with vax_data
        df_outer = pd.merge(self.df_vax, df_clinics_sub, on='clinic_unique_id', how='outer', indicator=True)
        # Limit df_vax to common entries only
        self.df_vax = df_outer[df_outer['_merge']=='both']
        self.df_vax = self.df_vax.drop(['_merge'], axis=1)
        self.df_vax = self.df_vax.replace(np.nan, '')

        # Clinics that do not have any vaccinations
        # 140 clinics....these are active clinics with no vaccinations?
        clinics_no_vax=df_outer[df_outer['_merge'] == 'right_only']
        clinics_no_vax = clinics_no_vax[['clinic_unique_id', 'clinic_desc']]
        clinics_no_vax.to_csv('../vaccinations/clinics_with_no_vax.csv', index=False)

        # Get rid of clinic desc column from previous merge
        self.df_vax = self.df_vax.drop(['clinic_desc'], axis=1)

        self.df_vax.reset_index(drop=True,inplace=True)

        print('Compared with clinics - reduced to',len(self.df_vax),'entries')

    def get_body_site_codes(self):

        # Ones with None do not appear in our data
        body_site_codes = [(1, 'Intranasal', 'NS'),
                           (2, 'Left Arm', 'LA'),
                           (3, 'Left Deltoid', 'LD'),
                           (4, 'Left Lower Forearm', 'LLFA'),
                           (5, 'Left Thigh', 'LT'),
                           (6, 'Left Upper Outer Quadrant Gluteous', 'LG'),
                           (7, 'Left Vastus Lateralis', 'LVL'),
                           (8, 'Left Ventral Gluteous', None),
                           (9, 'Oral', None),
                           (10, 'Right Arm', 'RA'),
                           (11, 'Right Deltoid', 'RD'),
                           (12, 'Right Lower Forearm', 'RLFA'),
                           (13, 'Right Thigh', 'RT'),
                           (14, 'Right Upper Outer Quadrant Gluteous', 'RG'),
                           (15, 'Right Vastus Lateralis', 'RVL'),
                           (16, 'Right Ventral Gluteous', None)
                           ]
        body_site_dict = {}
        for t in body_site_codes:
            body_site_dict[t[2]] = t[0]

        # None does not appear in dataset but blank could
        self.df_vax.loc[:, 'body_site_code_id'] = [body_site_dict[code] if code != '' else '' for code in
                                                    self.df_vax.loc[:, 'body_site_code_id']]

        print('Body site codes mapped')

    def get_body_route_codes(self):
        body_route_codes = [(1, 'Intradermal', 'ID', 'C38238'),
                            (2, 'Intramuscular', 'IM', 'C28161'),
                            (3, 'Intranasal', 'IN', 'C38284'),
                            (4, 'Intravenous', 'IV', 'C38276'),
                            (5, 'Nasal', 'NS', 'C38284'),
                            (6, 'Oral', 'PO', 'C38288'),
                            (7, 'Other/Miscellaneous', 'OTH', None),
                            (8, 'Percutaneous', None, 'C38676'),
                            (9, 'Subcutaneous', 'SC', 'C38299'),
                            (10, 'Transdermal', 'TD', 'C38305')
                            ]
        # C38284 refers to both intranasal and nasal
        # Intranasal is legacy code so will be using nasal (code 5)
        body_route_code_dict = {}
        for t in body_route_codes:
            body_route_code_dict[t[3]] = t[0]

        # Map IM to C28161
        self.df_vax.loc[:, 'body_route_code_id'] = ['C28161' if code == 'IM' else code for code in
                                                    self.df_vax.loc[:, 'body_route_code_id']]
        # Map PO to C38288
        self.df_vax.loc[:, 'body_route_code_id'] = ['C38288' if code == 'PO' else code for code in
                                                    self.df_vax.loc[:, 'body_route_code_id']]
        # Map SC to C38299
        self.df_vax.loc[:, 'body_route_code_id'] = ['C38299' if code == 'SC' else code for code in
                                                    self.df_vax.loc[:, 'body_route_code_id']]
        # Replace MP by None which maps to other(7)
        self.df_vax.loc[:, 'body_route_code_id'] = [None if code == 'MP' else code for code in
                                                    self.df_vax.loc[:, 'body_route_code_id']]

        self.df_vax.loc[:, 'body_route_code_id'] = [body_route_code_dict[code] if code!='' else '' for code in
                                                    self.df_vax.loc[:, 'body_route_code_id']]
        print('Body route codes are mapped')

    # Function to create vis data from the lists
    def create_vis(self):
        vis_names_df = self.df_vax[['vaccination_identifier','vis_names','vis_dates']]
        print('vis_names',vis_names_df.info())
        new_df= pd.DataFrame()
        #Convert names string into a list
        new_df.loc[:,'vis_names'] = [names.split(',') for names in vis_names_df.loc[:,'vis_names']]
        new_df.loc[:,'vis_dates'] = [dates.split(',') for dates in vis_names_df.loc[:,'vis_dates']]
        # Create a new dataframe by converting list items into columns
        new_df1=pd.DataFrame(new_df.vis_names.values.tolist(),new_df.index,dtype=object).fillna('').add_prefix('vis')
        new_df2=pd.DataFrame(new_df.vis_dates.values.tolist(),new_df.index,dtype=object).fillna('').add_prefix('effective_date')
        vis_names_df = vis_names_df.drop(['vis_names','vis_dates'], axis=1)

        vis_names_df = pd.concat([vis_names_df,new_df1,new_df2],axis=1)
        vis_names_df = vis_names_df.rename(columns={'vis0':'vis1_name','vis1':'vis2_name','vis2':'vis3_name','vis3':'vis4_name',
                                                    'effective_date0':'vis1_effective_date','effective_date1':'vis2_effective_date',
                                                    'effective_date2':'vis3_effective_date','effective_date3':'vis4_effective_date'})

        self.df_vax = self.df_vax.drop(['vis_names','vis_dates'], axis=1)
        # Merge with self.df_vax dataframe
        self.df_vax = pd.merge(self.df_vax,vis_names_df,on='vaccination_identifier',how='outer',indicator=True)
        #self.df_vax = df_merge[df_merge['_merge']=='both']
        self.df_vax= self.df_vax.drop(['_merge'],axis=1)
        self.df_vax = self.df_vax.replace(np.nan, '')
        print('merged',self.df_vax.info())


        '''
        # Add 4 new empty columns
        vis_names_df['vis1_name']=''
        vis_names_df['vis2_name']=''
        vis_names_df['vis3_name']=''
        vis_names_df['vis4_name']=''

        vis_names_list = vis_names_df.loc[:,'vis_names']
        # Dataframe row index
        idx=0
        for name in vis_names_list:
            tokens = name.split(',')
            i=0
            while i<len(tokens):
                vis_names_df[idx,'vis'+str(i+1)+'_name'] = tokens[i]
                i+=1
            idx+=1

        vis_names_df=vis_names_df.drop(['vis_names'],axis=1)

        df_merge = pd.merge(self.df_vax,vis_names_df,on='vaccination_identifier',how='outer',indicator=True)
        self.df_vax = df_merge[df_merge['_merge']=='both']
        self.df_vax = self.df_vax.drop(['_merge'], axis=1)
        self.df_vax = self.df_vax.replace(np.nan, '')

        print(len(self.df_vax))
        '''

    def prepare_vaccinations(self):
        print('Num of vaccination entries',len(self.df_vax))
        # Convert column names to lower case
        for c in list(self.df_vax.columns):
            self.df_vax.rename(columns={c: c.lower()}, inplace=True)

        # Drop duplicates
        self.df_vax.drop_duplicates(inplace=True, ignore_index=True)
        self.df_vax.drop_duplicates(subset=['vaccination_identifier'],inplace=True, ignore_index=True)
        self.df_vax.reset_index(drop=True, inplace=True)

        print('Vaccination Entries after dropping duplicates',len(self.df_vax))

        #Check against patient container - drop vaccinations for patients not in patients container
        self.compare_with_patients()
        self.calculate_age()
        self.calculate_vfc_codes()

        # Check against clinics container - drop vaccinations associated with clinics not in clinics container
        self.compare_with_clinics()
        #print('after clinics', self.df_vax.info())
        # Unrecognized value for MVX - change to OTH
        results=self.df_vax[self.df_vax['mvx_code'] == 'NOT']
        for idx in results.index:
            self.df_vax.loc[idx,'mvx_code'] = 'OTH'

        # Map GSK mvx code to SKB which is the correct one according to Glaxo smith
        self.df_vax.loc[:, 'mvx_code'] = ['SKB' if mvx == 'GSK' else mvx for mvx in self.df_vax.loc[:, 'mvx_code']]

        self.get_body_site_codes()
        self.get_body_route_codes()
        #print('after routes', self.df_vax.info())

        # Convert float type to int type
        self.df_vax.record_source_id = self.df_vax.record_source_id.astype('int64')

        # Truncate lot number to 20 characters since that is the max allotted
        self.df_vax.loc[:, 'lot_number'] = [lot[:20] for lot in self.df_vax.loc[:, 'lot_number']]

        # Clean up lot numbers
        self.df_vax.loc[:,'lot_number'] = [ Vaccinations.clean_up_lot_number(lot_number) if ((',' in lot_number) or ('(' in lot_number))
                                            else lot_number for lot_number in self.df_vax.loc[:, 'lot_number']]

        #print('after lot', self.df_vax.info())
        # Assign cvx code 999 (unknown) for empty ones
        self.df_vax.loc[:, 'cvx_code'] = ['999' if code == '' else code for code in self.df_vax.loc[:, 'cvx_code']]

        # Maintain limits
        #self.df_vax.loc[:,'vis1_name'] = [name[:50] for name in self.df_vax.loc[:,'vis1_name']]
        #self.df_vax.loc[:,'insurance_id'] =[id[:25] for id in self.df_vax.loc[:,'insurance_id']]

        #print('before vis',self.df_vax.info())
        # Add vis columns
        self.create_vis()
        # New columns: "LEGACY_PRESCRIBED_BY_NAME", "LEGACY_PRESCRIBED_BY_ID", "LEGACY_ADMINISTERED_BY_NAME", "LEGACY_ADMINISTERED_BY_ID"
        # Clean up legacy_prescribed_by
        self.df_vax.loc[:,'legacy_prescribed_by_name'] =[name.replace(',','').strip().title() for name in self.df_vax.loc[:,'legacy_prescribed_by_name']]
        self.df_vax.loc[:, 'legacy_administered_by_name'] = [name.replace(',', '').strip().title() for name in
                                                           self.df_vax.loc[:, 'legacy_administered_by_name']]



        self.df_vax.to_csv('db_files/vaccinations_bulk_insert.csv', index=False)
        print("Wrote",len(self.df_vax),"vaccination entries to file")

    @staticmethod
    def clean_up_lot_number(lot_num):
        if '(' in lot_num:
            if lot_num.startswith('(L)') or lot_num.startswith('(10)'):
                return lot_num.strip()
            else:
                tokens=lot_num.split('(')
                return tokens[0].strip()
        else:
            # split by comma and then explore
            tokens = lot_num.split(',')
            good_lot_num = ''
            for i in range(len(tokens)):
                tokens[i] = tokens[i].strip()
                alpha = False
                numeric = False
                for ch in tokens[i]:
                    if 'A' <= ch <= 'Z':
                        alpha = True
                    elif '0' <= ch <= '9':
                        numeric = True
                if alpha and numeric:
                    good_lot_num += tokens[i] + '/'

            return good_lot_num.strip('/')

    # Get vaccine adverse reactions
    def get_vaccine_adverse_reactions(self):
        print("Num of vaccine adverse reactions", len(self.df_adverse_reaction))
        for col in list(self.df_adverse_reaction.columns):
            self.df_adverse_reaction.rename(columns={col: col.lower()}, inplace=True)

        self.df_adverse_reaction = self.df_adverse_reaction.drop_duplicates(ignore_index=True)
        print("Num of vaccine adverse reactions after dropping duplicates", len(self.df_adverse_reaction))

        #self.df_vax=pd.read_csv('db_files/vaccinations_bulk_insert.csv',dtype={'vaccination_identifier':str},na_filter=False)
        df_vax_sub = self.df_vax[['vaccination_identifier']]
        self.df_adverse_reaction['vaccination_identifier'] = self.df_adverse_reaction['vaccination_identifier'].astype(str)
        self.df_adverse_reaction.loc[:,'allergy_risk_desc'] = [desc.replace('"','').replace('null','') for desc in self.df_adverse_reaction.loc[:,'allergy_risk_desc']]

        df_merge = pd.merge(self.df_adverse_reaction, df_vax_sub, on='vaccination_identifier', how='outer',
                            indicator=True)
        self.df_adverse_reaction = df_merge[df_merge['_merge'] == 'both']
        self.df_adverse_reaction = self.df_adverse_reaction.drop(['_merge'],axis=1)
        self.df_adverse_reaction.replace(np.nan, '', inplace=True)
        self.df_adverse_reaction['reaction_code_id'] = self.df_adverse_reaction['reaction_code_id'].astype(int)

        self.df_adverse_reaction.to_csv('db_files/vaccine_adverse_reactions_bulk_insert.csv', index=False)
        print("Wrote", len(self.df_adverse_reaction), 'adverse reactions to file')



    # For testing purposes
    def check_lot_numbers(self):

        # If lot number contains comma or parentheses
        df_lot = self.df_vax[(self.df_vax['lot_number'].str.contains(',|\\('))  ]

        df_lot_sub = df_lot[['other_identifier','vaccination_identifier','vaccination_date','cvx_code','mvx_code','lot_number']]

        df_lot_sub.loc[:,'lot_number_fixed'] = df_lot_sub.loc[:,'lot_number'].apply(lambda x: Vaccinations.clean_up_lot_number(x))

        #df_lot_sub.loc[:,'lot_number_fixed'] =[Vaccinations.clean_up_lot_number(lot) for lot in df_lot_sub.loc[:,'lot_number']]

        df_lot_sub.to_csv('misc/bad_lot_numbers.csv', index=False)




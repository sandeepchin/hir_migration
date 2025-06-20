
# Code to map patients into Patients container
import pandas as pd
import numpy as np
# Import datetime
from datetime import datetime,date

class Patient:

    def __init__(self):
        self.df_patients = pd.read_csv('input/patient_data.csv',dtype={'OTHER_IDENTIFIER':str},na_filter=False,encoding='latin-1')

        # Get the file containing vfc codes
        self.df_vfc = pd.read_csv('input/patient_funding_program_code.csv', na_filter=False)

        # Process file containing race data
        self.df_races = pd.read_csv('input/patient_race_list.csv', na_filter=False)

        # Get record source using last_updated_by_org_id
        self.df_record = pd.read_csv('input/patient_record_source.csv', dtype={'CLIENT_ID': str}, na_filter=False,low_memory=False)

        # Get patient insurance info
        self.df_insurance = pd.read_csv('input/patient_insurance.csv', dtype={'OTHER_IDENTIFIER': str},
                                        na_filter=False)

        # Get patient ids for patients identified as test patients
        self.df_test_patients = pd.read_csv('input/test_patients_reviewed.csv',dtype={'other_identifier':str},na_filter=False)

        # Get patient allergy risk data
        self.df_patient_allergy =pd.read_csv('input/patient_allergy_risks.csv',dtype={'other_identifier':str},na_filter=False)

        self.prepare_patients()

    # Map generation to a code
    def get_generation_codes(this,somedf):
        generation_codes = [(1, 'JR'),
                            (2, 'SR'),
                            (3, 'I'),
                            (4, 'II'),
                            (5, 'III'),
                            (6, 'IIII'),
                            (7, 'IV'),
                            (8, 'V'),
                            (9, 'VI'),
                            (10, 'VII'),
                            (11, 'VIII'),
                            (12, 'IX'),
                            (13, 'X')]
        generation_dict = {}
        for t in generation_codes:
            generation_dict[t[1]] = t[0]

        somedf.loc[:, 'name_generation_code_id'] = [g.strip() for g in somedf.loc[:, 'name_generation_code_id']]
        somelist = []
        for gen in somedf.loc[:, 'name_generation_code_id']:
            try:
                somelist.append(generation_dict[gen])
            except:
                somelist.append('')

        somedf.loc[:, 'name_generation_code_id'] = somelist
        print("Generation codes mapped")
        return somedf


    # Map gender to code
    def get_gender_codes(self):
        gender_codes = [(1, 'F'),
                        (2, 'M'),
                        (3, 'T'),
                        (4, 'U')]
        gender_dict = {}
        for t in gender_codes:
            gender_dict[t[1]] = t[0]

        self.df_patients.loc[:, 'gender_code_id'] = [g.strip() for g in self.df_patients.loc[:, 'gender_code_id']]
        somelist = []
        for gen in self.df_patients.loc[:, 'gender_code_id']:
            try:
                somelist.append(gender_dict[gen])
            except:
                somelist.append('')

        self.df_patients.loc[:, 'gender_code_id'] = somelist
        print('Gender codes mapped')

    # Map ethnicity codes
    def get_ethnicity_codes(self):
        ethnicity_codes = [(1, '2135-2'),
                           (2, '2186-5'),
                           (3, 'Unknown')]
        ethnicity_dict = {}
        for t in ethnicity_codes:
            ethnicity_dict[t[1]] = t[0]

        self.df_patients.loc[:, 'ethnicity_code_id'] = [e.strip() for e in self.df_patients.loc[:, 'ethnicity_code_id']]
        somelist = []
        for e in self.df_patients.loc[:, 'ethnicity_code_id']:
            try:
                somelist.append(ethnicity_dict[e])
            except:
                somelist.append('')

        self.df_patients.loc[:, 'ethnicity_code_id'] = somelist
        print('Ethnicity codes mapped')

    # Map VFC codes for patients
    def get_vfc_codes(self):
        # Get rid of any space
        self.df_vfc.loc[:, 'FUNDING_PROGRAM_CODE'] = [c.strip() for c in self.df_vfc.loc[:, 'FUNDING_PROGRAM_CODE']]

        # Associate patients ids with vfc code
        vfc_dict = {}
        for i in range(len(self.df_vfc)):
            vfc_dict[str(self.df_vfc.loc[i, 'CLIENT_ID'])] = self.df_vfc.loc[i, 'FUNDING_PROGRAM_CODE']

        somelist = []
        for client in self.df_patients.loc[:, 'other_identifier']:
            try:
                somelist.append(vfc_dict[client])
            except:
                somelist.append('')

        self.df_patients.loc[:, 'vfc_code_id'] = somelist

        # Now mapping above values to codes in code table
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

        somelist = []
        for code in self.df_patients.loc[:, 'vfc_code_id']:
            try:
                somelist.append(vfc_code_dict[code])
            except:
                somelist.append('')

        self.df_patients.loc[:, 'vfc_code_id'] = somelist

        # Cannot have null values for vfc code
        # calculate age to determine vfc code
        self.df_patients.loc[:, 'age'] = [datetime.strptime(dob, '%Y-%m-%d').date() for dob in self.df_patients.loc[:, 'dob']]
        today = date.today()
        self.df_patients.loc[:, 'age'] = [today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day)) for dob_date in
                                          self.df_patients.loc[:, 'age']]
        # if age<=18 then assign V00 (1)
        # else V01 (2)
        ages = self.df_patients.loc[:, 'age']
        codes = self.df_patients.loc[:, 'vfc_code_id']

        self.df_patients.loc[:, 'vfc_code_id'] = [code if code != '' else 1 if age <= 18 else 2 for code, age in
                                                  zip(codes, ages)]
        # drop age column since it is not used in container
        self.df_patients.drop('age', axis=1, inplace=True)
        print('VFC codes mapped')

    # map race values to codes
    def get_race_codes(self):
        # Completed adding additional races to patient notes toble
        race_dict = {}
        count = 0
        overflow = {}
        for i in range(len(self.df_races)):
            races = self.df_races.loc[i, 'RACE_LIST'].strip().split('|')
            # When less than 5 races just assign to patient
            if len(races) < 6:
                race_dict[self.df_races.loc[i, 'OTHER_PATIENT_IDENTIFIER']] = races
            else:
                picks = []
                # Pick nhpi if listed
                if '2076-8' in races:
                    picks.append('2076-8')
                # Pick native hi if listed
                if '2079-2' in races:
                    picks.append('2079-2')
                j = len(picks)
                for item in races:
                    if j < 5 and item not in picks:
                        picks.append(item)
                        j += 1
                # print(picks)
                remaining = []
                for r in races:
                    if r not in picks:
                        remaining.append(r)

                overflow[self.df_races.loc[i, 'OTHER_PATIENT_IDENTIFIER']] = remaining
                count += 1
                race_dict[self.df_races.loc[i, 'OTHER_PATIENT_IDENTIFIER']] = picks
        print('Number of patient with more than 5 races', count)

        # Write this additional race data to patient_notes table
        # Create patient_notes dataframe with three columns - other identifier, note type id, note text
        df_patient_notes = pd.DataFrame()
        df_patient_notes.loc[:, 'other_identifier'] = list(overflow.keys())
        df_patient_notes['note_type_id'] = 1
        df_patient_notes.loc[:, 'note_text'] = [" ".join(overflow[key]) for key in
                                                df_patient_notes.loc[:, 'other_identifier']]
        # Race codes table
        race_code_ids = [(1, 'American Indian or Alaska Native', '1002-5'),
                         (2, 'Asian', '2028-9'),
                         (3, 'Asian Indian', '2029-7'),
                         (4, 'Chinese', '2034-7'),
                         (5, 'Filipino', '2036-2'),
                         (6, 'Japanese', '2039-6'),
                         (7, 'Korean', '2040-4'),
                         (8, 'Okinawan', '2043-8'),
                         (9, 'Thai', '2046-1'),
                         (10, 'Vietnamese', '2047-9'),
                         (11, 'Black or African American', '2054-5'),
                         (12, 'Native Hawaiian or Pacific Islander', '2076-8'),
                         (13, 'Native Hawaiian', '2079-2'),
                         (14, 'Samoan', '2080-0'),
                         (15, 'Tahitian', '2081-8'),
                         (16, 'Tongan', '2082-6'),
                         (17, 'Guamanian or Chamorro', '2086-7'),
                         (18, 'Marshallese', '2090-9'),
                         (19, 'Palauan', '2091-7'),
                         (20, 'Kosraean', '2093-3'),
                         (21, 'Pohnpeian', '2094-1'),
                         (22, 'Kiribati', '2096-6'),
                         (23, 'Chuukese', '2097-4'),
                         (24, 'Yapese', '2098-2'),
                         (25, 'Fijian', '2101-4'),
                         (26, 'White', '2106-3'),
                         (27, 'Other', '2131-1'),
                         (28, 'Other Pacific Islander', '2500-7'),
                         (29, 'Unknown', '')]

        # map race code to code id in table
        race_code_map = {}
        for item in race_code_ids:
            race_code_map[item[2]] = item[0]

        # map race code to its name
        race_name_map = {}
        for item in race_code_ids:
            race_name_map[item[2]] = item[1]

        # Add the race name next to race code in the note text
        for i in range(len(df_patient_notes)):
            text = df_patient_notes.loc[i, 'note_text']
            # print(text)
            tokens = text.split(' ')
            note = 'Additional patient races: '
            for token in tokens:
                note += token + '(' + race_name_map[token] + ');'
            df_patient_notes.loc[i, 'note_text'] = note.strip().strip(';')

        # write df_patient_notes to file
        df_patient_notes.to_csv('db_files/patient_notes_bulk_insert.csv', index=False)
        print('Additional races added to patient notes')

        # Continue with adding race data to patient
        # Convert race_dict with race codes to code ids from code table
        for client in race_dict.keys():
            somelist = []
            # Map each race of client to an id
            for item in race_dict[client]:
                try:
                    somelist.append(race_code_map[item])
                except:
                    somelist.append(0)
            race_dict[client] = somelist

        # Preparing to merge this race data with patient dataframe (doing it other ways was inefficient)
        # Step 1:  Make all race code lists the same size
        for key in race_dict.keys():
            race_list = race_dict[key]
            if len(race_list) < 5:
                size = len(race_list)
                while size < 5:
                    race_list.append(0)
                    size += 1
                race_dict[key] = race_list

        # Step 2: Convert race_dict to a dataframe with key client id as index and 5 columns
        race_df = pd.DataFrame.from_dict(race_dict, orient='index',columns=['race_code_id1', 'race_code_id2', 'race_code_id3',
                                                                            'race_code_id4','race_code_id5'],dtype=int)
        # replace 0 by blank
        race_df.replace(0, '', inplace=True)
        # Make client id as one of the columns, so reset index
        race_df.reset_index(inplace=True)
        # Rename the new column to other_identifier
        race_df.rename(columns={'index': 'other_identifier'}, inplace=True)
        # Set type to str
        race_df['other_identifier'] = race_df['other_identifier'].astype(str)

        # Merge the two dataframes
        self.df_patients = pd.merge(self.df_patients, race_df, on='other_identifier', how='left')
        # Get rid of NaN values popping up during merge.
        self.df_patients.replace(np.nan, '', inplace=True)
        print('Race codes mapped')


    def get_record_sources(self):
        # Rename columns
        self.df_record.rename(columns={'CLIENT_ID': 'other_identifier', 'RECORD_SOURCE_ID': 'record_source_id'},inplace=True)

        # Get rid of existing empty column in df_patients
        self.df_patients.drop('record_source_id', axis=1, inplace=True)
        # Merge df_record with df_patients
        self.df_patients = pd.merge(self.df_patients, self.df_record, on='other_identifier', how='left')
        self.df_patients.replace(np.nan, '', inplace=True)
        print("Record source ids mapped")
        '''
        Old logic - not needed since calculation is being done in query 
        # Adding Frank Baum(4384) to list of hl7 senders (3/6/25) even though stc health sends data
        # To make sure that if last vax is from Frank Baum then source id is 2
        # Includes historical orgs that were parents like 4348(Wahiawa), 9642(Costco pharmacy), 12464(Quatris)
        hl7_senders = [3920, 4040, 4100, 4140, 4217, 4348, 4349, 7681, 7740, 7820,
                       8080, 8561, 8901, 8921, 9041, 9221, 9302, 9642, 11243, 11426, 11564,
                       11584, 11694, 12048, 12504, 13164, 13244, 13264, 13304, 13365, 13504, 12464, 4384]

        hl7_senders = [str(sender) for sender in hl7_senders]
        # If last updated by org id (client table) is in the hl7 sender list then 2 otherwise 1
        self.df_patients.loc[:, 'record_source_id'] = [2 if org in hl7_senders else 1 for org in
                                                       self.df_patients.loc[:, 'record_source_id']]
        '''

    def get_pseudo_first_names(self):
        # 7K records with match recognized by Lazaro
        missing_first_with_match = pd.read_csv('input/missing_first_match.csv', na_filter=False)
        # Get list of matched patient identifiers
        matched = list(missing_first_with_match.loc[:, 'NULL_CLIENT_ID'].astype(str))
        # Assign a pseudo name
        self.df_patients.loc[:, 'first_name'] = [name if name != '' else 'HIRDuplicate' if id in matched else 'HIRNoFirstName'
            for name, id in zip(self.df_patients.loc[:, 'first_name'], self.df_patients.loc[:, 'other_identifier'])]

        num_dupes = self.df_patients[self.df_patients['first_name']=='HIRDuplicate']
        num_no_first = self.df_patients[self.df_patients['first_name']=='HIRNoFirstName']
        print('Num of duplicate records',len(num_dupes))
        print('Num of no first name records', len(num_no_first))
        print('Pseudo first names assigned')


    def prepare_patients(self):
        # Change column names to lower case
        for c in list(self.df_patients.columns):
            self.df_patients.rename(columns={c: c.lower()}, inplace=True)

        self.df_patients.drop(columns=['title_code_id', 'occupation_code_id', 'language_code_id', 'alias_generation_code_id',
                                  'father_name_generation_code_id',
                                  'iz_program_clinic_inactive_reason_code_id',
                                  'iz_program_jurisdiction_reason_code_id'], axis=1, inplace=True)

        self.df_patients.drop(columns=['other_identifier_2', 'ssn', 'alias_first_name', 'alias_middle_name', 'alias_last_name',
                                       'cell_phone_number','work_phone_number', 'mother_middle_name', 'mother_last_name', 'father_first_name',
                                       'father_middle_name','father_last_name', 'clinic_unique_id', 'death_certificate_id',
                                       'iz_program_effective_date'],axis=1, inplace=True)

        print('Num of patients',len(self.df_patients))
        # Clean up various columns
        # Remove commas, double quotes
        self.df_patients.loc[:, 'first_name'] = [name.title().replace(',', '').replace('"', '').strip() for name in
                                                 self.df_patients.loc[:, 'first_name']]
        self.df_patients.loc[:, 'middle_name'] = [name.title().replace(',', '').replace('"', '').strip() for name in
                                                  self.df_patients.loc[:, 'middle_name']]
        self.df_patients.loc[:, 'last_name'] = [name.title().replace(',', '').replace('"', '').strip() for name in
                                                self.df_patients.loc[:, 'last_name']]

        self.df_patients.loc[:, 'mailing_address_line1'] = [address.replace(',', '').replace('"', '').strip() for address in
                                                            self.df_patients.loc[:, 'mailing_address_line1']]
        #  The combo '#800 can be seen as a html code? So replacing it specifically
        self.df_patients.loc[:, 'mailing_address_line1'] = [address.replace("'#", "#").strip() for address in
                                                            self.df_patients.loc[:, 'mailing_address_line1']]

        self.df_patients.loc[:, 'mailing_address_city'] = [city.title().replace(',', '').replace('"', '').strip() for city in
                                                           self.df_patients.loc[:, 'mailing_address_city']]
        self.df_patients.loc[:, 'mailing_address_county'] = [county.title().strip() for county in
                                                             self.df_patients.loc[:, 'mailing_address_county']]
        self.df_patients.loc[:, 'mailing_address_zip'] = [zip.replace(',', '').strip() for zip in
                                                          self.df_patients.loc[:, 'mailing_address_zip']]
        self.df_patients.loc[:, 'mailing_address_state'] = [state.replace(',', '').strip() for state in
                                                            self.df_patients.loc[:, 'mailing_address_state']]

        self.df_patients.loc[:, 'primary_physician_name'] = [phy.title().replace(',', '').replace('"', '').strip() for phy in
                                                             self.df_patients.loc[:, 'primary_physician_name']]

        self.df_patients.loc[:, 'primary_physician_contact_info'] = [phy.title().replace(',', '').replace('"', '').strip() for phy in
                                                                     self.df_patients.loc[:, 'primary_physician_contact_info']]

        self.df_patients.loc[:, 'mother_maiden_name'] = [mom.title().replace(',', '').replace('"', '').strip() for mom in
                                                         self.df_patients.loc[:, 'mother_maiden_name']]
        self.df_patients.loc[:, 'mother_first_name'] = [mom.title().replace(',', '').replace('"', '').strip() for mom in
                                                        self.df_patients.loc[:, 'mother_first_name']]

        self.df_patients.loc[:, 'legacy_created_by_name'] = [user.title().replace(',', '').replace('"', '').strip() for user in
                                                             self.df_patients.loc[:, 'legacy_created_by_name']]
        self.df_patients.loc[:, 'legacy_updated_by_name'] = [user.title().replace(',', '').replace('"', '').strip() for user in
                                                             self.df_patients.loc[:, 'legacy_updated_by_name']]

        self.df_patients.loc[:, 'email_address'] = [addr.replace(',', '').replace('"', '').strip() for addr in
                                                    self.df_patients.loc[:, 'email_address']]


        # Drop Duplicates all columns
        self.df_patients.drop_duplicates(inplace=True,ignore_index=True)
        # Drop duplicates in patient identifier column
        self.df_patients.drop_duplicates(subset=['other_identifier'],inplace=True,ignore_index=True)

        print('Num of patients after dropping duplicates',len(self.df_patients))

        # Dropping test patients
        df_outer = pd.merge(self.df_patients,self.df_test_patients,on='other_identifier',how='outer',indicator=True)
        self.df_patients = df_outer[df_outer['_merge']=='left_only']
        self.df_patients = self.df_patients.drop(['_merge'],axis=1)
        self.df_patients = self.df_patients.replace(np.nan,'')

        print('Dropped',len(df_outer[df_outer['_merge']=='both']),'test patients')

        # Map values to various code tables
        self.df_patients = self.get_generation_codes(self.df_patients)
        self.get_gender_codes()
        self.get_ethnicity_codes()
        self.get_vfc_codes()

        # Format phone numbers
        self.df_patients.loc[:, 'home_phone_number'] = [value[0:7] + '-' + value[7:] if value != '' else '' for value in
                                                        self.df_patients.loc[:, 'home_phone_number']]
        # Assign physical address
        self.df_patients.loc[:, 'physical_address_line1'] = self.df_patients.loc[:, 'mailing_address_line1']
        self.df_patients.loc[:, 'physical_address_line2'] = self.df_patients.loc[:, 'mailing_address_line2']
        self.df_patients.loc[:, 'physical_address_city'] = self.df_patients.loc[:, 'mailing_address_city']
        self.df_patients.loc[:, 'physical_address_county'] = self.df_patients.loc[:, 'mailing_address_county']
        self.df_patients.loc[:, 'physical_address_state'] = self.df_patients.loc[:, 'mailing_address_state']
        self.df_patients.loc[:, 'physical_address_zip'] = self.df_patients.loc[:, 'mailing_address_zip']

        # Get race codes mapped
        self.get_race_codes()
        # Get record source
        self.get_record_sources()
        # Assign pseudo names for patients with no first names
        self.get_pseudo_first_names()


        # Convert to csv for bulk upload
        self.df_patients.to_csv('db_files/patients_bulk_insert.csv', index=False)
        print(len(self.df_patients),"patients' data written to file")

    def get_insurance_codes(self):
        insurance_codes=[(1,'Aetna','AETNA'),
                         (2,'BC Life and Health Insurance Co.','BCBS'),
                         (3,'CIGNA','CIGNA'),
                         (4,'Connecticut General Life',''),
                         (5,'Great-West Life Assurance Company','GWL'),
                         (6,'Hawaii Electricians Health and Welfare Fund',''),
                         (7,'Hawaii Laborers Health and Welfare Fund',''),
                         (8,'HMA (Health Management Associates) - AFL and Hotel Workers Trust Fund','HMA-AFL'),
                         (9,'HMA (Health Management Associates) - EUTF','HMA-EUTF'),
                         (10,'HMAA (Hawaii Management Alliance Association)','HMAA'),
                         (11,'HMSA (Hawaii Medical Service Association)','HMSA'),
                         (12,'Humana Insurance Company','HUM'),
                         (13,'Kaiser - Added Choice',''),
                         (14,'Kaiser - Traditional',''),
                         (15,'Lovelace Health System Inc','LOVE'),
                         (16,'MDX (Medical Data Exchange)',''),
                         (17,'Medicaid','MediCAID'),
                         (18,'Medicare','MediCARE'),
                         (19,'Other',''),
                         (20,'Presbyterian Health Plan Inc','PRES'),
                         (21,'Quest/Aloha Care',''),
                         (22,'Quest/HMSA',''),
                         (23,'Quest/Kaiser',''),
                         (24,'Quest/Summerlin',''),
                         (25,'Summerlin Life & Health Insurance Company',''),
                         (26,'TriCare','TRI'),
                         (27,'UHA (University Health Alliance)','UHA'),
                         (28,'United Healthcare Insurance Company','UHC'),
                         (29,'Ohana',''),
                         (30,'Quest/United Healthcare','')]

        insurance_code_dict={}
        for tuple in insurance_codes:
            insurance_code_dict[tuple[1]] = tuple[0]

        somelist=[]
        for item in self.df_insurance.loc[:,'health_insurance_code_id']:
            try:
                code = insurance_code_dict[item]
                somelist.append(code)
            except:
                somelist.append('')

        self.df_insurance.loc[:,'health_insurance_code_id']=somelist

    # Build data for patient contact container
    def get_patient_insurance(self):

        for col in self.df_insurance.columns:
            self.df_insurance.rename(columns={col:col.lower()},inplace=True)

        print(len(self.df_insurance),'num of insurance entries')
        self.df_insurance.drop_duplicates(inplace=True,ignore_index=True)
        print(len(self.df_insurance), 'num of insurance entries after dropping duplicates')

        # Set primary insurance indicator to Y
        self.df_insurance.loc[:,'primary_insurance_indicator'] ='Y'
        # Except for duplicates
        dupes = self.df_insurance[self.df_insurance.duplicated(subset=['other_identifier'])]
        #print(dupes)
        for idx in dupes.index:
            self.df_insurance.loc[idx,'primary_insurance_indicator']='N'

        # Merge df_insurance with df_patients to make sure it does not have patients not in df_patients
        df_patients_sub = self.df_patients[['other_identifier']]

        df_outer = pd.merge(self.df_insurance,df_patients_sub,on='other_identifier',how='outer',indicator=True)

        # Only the common patients
        self.df_insurance = df_outer[df_outer['_merge']=='both']

        print('Num of insurance entries after merge',len(self.df_insurance))

        self.df_insurance=self.df_insurance.drop(['_merge'],axis=1)
        self.df_insurance=self.df_insurance.replace(np.nan,'')

        # Map insurance names to codes in code table
        # Clean up
        self.df_insurance.loc[:,'health_insurance_code_id'] = [v.strip() for v in self.df_insurance.loc[:,'health_insurance_code_id']]
        # Map insurance to code table id
        self.get_insurance_codes()
        # Clean up insurance id
        self.df_insurance.loc[:, 'insurance_id'] = [v.strip() for v in self.df_insurance.loc[:, 'insurance_id']]

        self.df_insurance.to_csv('db_files/patient_insurance_bulk_insert.csv',index=False)
        print("Wrote",len(self.df_insurance),"insurance entries to file")

    #get patient contact type code id
    def get_patient_contact_type_id(self):
        # Code table
        contact_codes=[(1, 'BROTHER', 'BRO'),
                        (2, 'CAREGIVER', 'CGV'),
                        (3, 'CHILD', 'CHD'),
                        (4, 'EXTENDED FAMILY','EXF'),
                        (5, 'FATHER', 'FTH'),
                        (6, 'FOSTER CHILD', 'FCH'),
                        (7, 'GRANDCHILD','GCH'),
                        (8, 'GRANDPARENT', 'GRP'),
                        (9, 'GUARDIAN', 'GRD'),
                        (10,'LIFE PARTNER','DOM'),
                        (11, 'MOTHER', 'MTH'),
                        (12, 'NONE','NON'),
                        (13, 'OTHER', 'OTH'),
                        (14, 'PARENT', 'PAR'),
                        (15, 'SELF', 'SEL'),
                        (16, 'SIBLING', 'SIB'),
                        (17, 'SISTER', 'SIS'),
                        (18, 'SPOUSE', 'SPO'),
                        (19, 'STEPCHILD', 'SCH'),
                        (20, 'UNKNOWN','UNK')]

        contact_code_dict={}
        for tuple in contact_codes:
            contact_code_dict[tuple[2]] = tuple[0]

        somelist=[]
        for item in self.df_contacts.loc[:,'patient_contact_type_code_id']:
            try:
                somelist.append(contact_code_dict[item])
            except:
                somelist.append('')

        self.df_contacts.loc[:,'patient_contact_type_code_id'] = somelist
        print('patient contact type codes mapped')

    # Build data for patient contact container
    def get_patient_contacts(self):
        # Get patient contact info
        self.df_contacts = pd.read_csv('input/patient_contacts.csv', dtype={'OTHER_IDENTIFIER': str},
                                        na_filter=False)

        for col in self.df_contacts.columns:
            self.df_contacts.rename(columns={col:col.lower()},inplace=True)

        print(len(self.df_contacts), 'num of contact entries')
        '''
        Doing this in sql code
        self.df_contacts.loc[:, 'first_name'] = [name.title().replace(',', '').replace('"', '').replace('.','').strip() for name in
                                                 self.df_contacts.loc[:, 'first_name']]
        self.df_contacts.loc[:, 'middle_name'] = [name.title().replace(',', '').replace('"', '').replace('.','').strip() for name in
                                                 self.df_contacts.loc[:, 'middle_name']]
        '''
        # Last name must be 30 chars max so truncating
        self.df_contacts.loc[:, 'last_name'] = [name[:30] for name in self.df_contacts.loc[:, 'last_name']]

        self.df_contacts.drop_duplicates(inplace=True, ignore_index=True)
        # Drop duplicates for same patient and contacts
        self.df_contacts.drop_duplicates(subset=['other_identifier', 'first_name', 'last_name'], inplace=True,
                                         ignore_index=True)
        print(len(self.df_contacts), 'num of contact entries after dropping duplicates')

        '''
        # Doing this in SQL code 
        # Replace first names and last names that are Pt,Patient,Time,Listed,Per,Per Pt,Perpt, Permom, Permother,Given,To, Give, Mother, Parent, -
        remove_list=['None','Pt','Patient','Time','Listed','Per','Per Pt','Perpt', 'Permom', 'Permother','Given','To', 'Give', 'Mother', 'Parent','-','No','Contact','Contacts']

        # Replace unwanted names with blanks
        self.df_contacts.loc[:, 'first_name'] = [name if name not in remove_list else '' for name in self.df_contacts.loc[:, 'first_name']]
        self.df_contacts.loc[:, 'last_name'] = [name if name not in remove_list else '' for name in self.df_contacts.loc[:, 'last_name']]
        self.df_contacts.loc[:, 'middle_name'] = [name if name not in remove_list else '' for name in self.df_contacts.loc[:, 'middle_name']]
        '''
        # Format phone numbers
        self.df_contacts.loc[:, 'cell_phone_number'] = [ph[0:7] + '-' + ph[7:] if ph != '' else '' for ph in
                                                        self.df_contacts.loc[:, 'cell_phone_number']]
        self.df_contacts.loc[:, 'work_phone_number'] = [ph[0:7] + '-' + ph[7:] if ph != '' else '' for ph in
                                                        self.df_contacts.loc[:, 'work_phone_number']]
        self.df_contacts.loc[:, 'home_phone_number'] = [ph[0:7] + '-' + ph[7:] if ph != '' else '' for ph in
                                                        self.df_contacts.loc[:, 'home_phone_number']]
        self.df_contacts.loc[:, 'emergency_phone_number'] = [ph[0:7] + '-' + ph[7:] if ph != '' else '' for ph in
                                                             self.df_contacts.loc[:, 'emergency_phone_number']]

        #create unwanted rows - blank first,last, and phone numbers
        df_unwanted = self.df_contacts[(self.df_contacts['first_name']=='') & (self.df_contacts['last_name']=='') & (self.df_contacts['cell_phone_number']=='')&
                                       (self.df_contacts['home_phone_number']=='') & (self.df_contacts['work_phone_number']=='')
                                       & (self.df_contacts['emergency_phone_number']=='') & (self.df_contacts['email_address']=='')]
        # drop unwanted rows
        for idx in df_unwanted.index:
            self.df_contacts.drop(idx,axis=0,inplace=True)

        self.df_contacts.reset_index(drop=True,inplace=True)
        print(len(self.df_contacts), 'num of contact entries after dropping empty contacts')

        # Merge df_contacts with df_patients to make sure it does not have patients not in df_patients
        df_patients_sub = self.df_patients[['other_identifier']]

        df_outer = pd.merge(self.df_contacts, df_patients_sub, on='other_identifier', how='outer', indicator=True)

        # Only the common patients
        self.df_contacts = df_outer[df_outer['_merge'] == 'both']

        self.df_contacts = self.df_contacts.drop(['_merge'], axis=1)
        self.df_contacts = self.df_contacts.replace(np.nan, '')
        print('Num of contact entries after merge', len(self.df_contacts))

        # Adjusting for typo in EXF - converting EFX to EXF
        self.df_contacts.loc[:,'patient_contact_type_code_id'] = [ v if v!='EFX' else 'EXF' for v in self.df_contacts.loc[:,'patient_contact_type_code_id']]
        self.get_patient_contact_type_id()

        # Drop period fromm name generation code
        self.df_contacts.loc[:,'name_generation_code_id'] =[v.strip('.') for v in self.df_contacts.loc[:,'name_generation_code_id']]
        # Replace Junior and First with contractions
        self.df_contacts.loc[:,'name_generation_code_id']=[v if v!='JUNIOR' else 'JR' for v in
                                                           self.df_contacts.loc[:,'name_generation_code_id']]
        self.df_contacts.loc[:, 'name_generation_code_id'] = [v if v != 'FIRST' else 'I' for v in
                                                              self.df_contacts.loc[:, 'name_generation_code_id']]

        # Map to name generation code ids
        self.df_contacts=self.get_generation_codes(self.df_contacts)

        #self.df_contacts.reset_index(drop=True,inplace=True)
        # bool vector
        dup_indicator_list=list(self.df_contacts.duplicated(subset=['other_identifier']))
        # Set non-duplicate row as primary contact and duplicate row as non-primary
        self.df_contacts.loc[:, 'primary_contact_indicator'] = ['Y' if v==False else 'N' for v in dup_indicator_list]

        '''
        # Approach 2: list of dictionaries
        # Set primary contact indicator to Y
        self.df_contacts.loc[:, 'primary_contact_indicator'] = 'Y'
        # Except for duplicates
        dupes = self.df_contacts[self.df_contacts.duplicated(subset=['other_identifier'])]
        indices=list(dupes.index)

        # Using List of dictionaries for efficiency
        df_contacts_dict = self.df_contacts.to_dict('records')
        for i in indices:
            item = df_contacts_dict[i]
            item['primary_contact_indicator']='N'
            
        self.df_contacts =pd.DataFrame(df_contacts_dict)
        # This approach was taking too long
        # Approach 3
        #for idx in dupes.index:
        #    #print(idx)
        #    self.df_contacts.loc[idx, 'primary_contact_indicator'] = 'N'
        '''

        print(self.df_contacts['primary_contact_indicator'].value_counts(dropna=False))

        # Map blank first and last names to some dummy name
        # ContactNoFirstName ContactNoLastName
        self.df_contacts.loc[:,'first_name'] = [name if name!='' else 'ContactNoFirstName' for name in self.df_contacts.loc[:,'first_name']]
        self.df_contacts.loc[:, 'last_name'] = [name if name!='' else 'ContactNoLastName' for name in self.df_contacts.loc[:, 'last_name']]

        self.df_contacts.to_csv('db_files/patient_contacts_bulk_insert.csv', index=False)
        print("Wrote", len(self.df_contacts), "contact entries to file")


    # patient allergy risks - precautions/contraindications
    def get_patient_allergy_risks(self):

        print("Num of patient allergy risk entries", len(self.df_patient_allergy))
        for col in list(self.df_patient_allergy.columns):
            self.df_patient_allergy.rename(columns={col: col.lower()}, inplace=True)

        self.df_patient_allergy=self.df_patient_allergy.drop_duplicates(ignore_index=True)
        print("Num of patient allergy risk entries after dropping duplicates", len(self.df_patient_allergy))

        df_patient_sub = self.df_patients[['other_identifier']]
        self.df_patient_allergy['other_identifier'] =self.df_patient_allergy['other_identifier'].astype(str)
        df_merge=pd.merge(self.df_patient_allergy,df_patient_sub,on='other_identifier',how='outer',indicator=True)
        self.df_patient_allergy = df_merge[df_merge['_merge']=='both']
        self.df_patient_allergy= self.df_patient_allergy.drop(['_merge'],axis=1)
        self.df_patient_allergy.replace(np.nan,'',inplace=True)

        self.df_patient_allergy.to_csv('db_files/patient_allergy_risks_bulk_insert.csv',index=False)
        print("Wrote",len(self.df_patient_allergy),'patient allergy risks to file')









# Code to map user data into users and other containers

import pandas as pd
import numpy as np

class Users:

    def __init__(self):
        self.df_users = pd.read_csv('input/users.csv', dtype={'OTHER_USER_IDENTIFIER': str}, na_filter=False)
        self.df_userprofile = pd.read_csv('input/user_clinics_vfc_hl7.csv', dtype={'OTHER_USER_IDENTIFIER': str}, na_filter=False)
        self.df_user_clinics = pd.read_csv('input/user_clinics.csv', dtype={'OTHER_USER_IDENTIFIER': str, 'CLINIC_UNIQUE_ID': str},
                          na_filter=False)
        self.df_hl7_clinics = pd.read_csv('input/hl7senders_and_clinics.csv', dtype={'CLINIC_UNIQUE_ID': str}, na_filter=False)
        self.df_hl7_users = pd.DataFrame()
        self.prepare_users()

    def prepare_users(self):
        # Rename columns
        for col in list(self.df_users.columns):
            self.df_users.rename(columns={col: col.lower()}, inplace=True)

        self.df_users.loc[:, 'username'] = [username.strip() for username in self.df_users.loc[:, 'username']]
        self.df_users.loc[:, 'first_name'] = [first_name.replace(",", "").strip() for first_name in
                                              self.df_users.loc[:, 'first_name']]
        self.df_users.loc[:, 'last_name'] = [last_name.replace(",", "").strip() for last_name in
                                             self.df_users.loc[:, 'last_name']]
        self.df_users.loc[:, 'middle_name'] = [middle_name.replace(",", "").strip() for middle_name in self.df_users.loc[:, 'middle_name']]
        self.df_users.loc[:, 'address_line1'] = [address_line.replace(",", "").strip() for address_line in
                                                 self.df_users.loc[:, 'address_line1']]
        self.df_users.loc[:, 'address_line2'] = [address_line.replace(",", "").strip() for address_line in
                                                 self.df_users.loc[:, 'address_line2']]
        self.df_users.loc[:, 'other_user_identifier'] = [identifier.strip() for identifier in
                                                         self.df_users.loc[:, 'other_user_identifier']]
        self.df_users.loc[:, 'address_city'] = [address_city.replace(",", "").strip() for address_city in
                                                self.df_users.loc[:, 'address_city']]

        print('number of users',len(self.df_users))
        # Drop duplicates
        self.df_users.drop_duplicates(subset=['username'],inplace=True,ignore_index=True)
        print('number of users after dropping duplicates',len(self.df_users))

        # Clean up email addresses
        self.df_users.loc[:, 'primary_email_address'] = [email.replace(",", "").strip() for email in
                                                         self.df_users.loc[:, 'primary_email_address']]

        # Split email addresses in to primary and secondary if multiple exist
        for i in range(len(self.df_users)):
            tokens = self.df_users.loc[i, 'primary_email_address'].split(' ')
            if len(tokens) >= 2:
                #print(tokens)
                primary = True
                # print(df_users.loc[i,'username'],df_users.loc[i,'last_name'])
                for token in tokens:
                    if '@' in token:
                        if primary:
                            self.df_users.loc[i, 'primary_email_address'] = token
                            primary = False
                        else:
                            self.df_users.loc[i, 'secondary_email_address'] = token

        # Combine user address line1, line 2 and city information into comments
        addr1 = [a.replace(",", '') for a in self.df_users.loc[:, 'address_line1']]
        addr2 = [a.replace(",", '') for a in self.df_users.loc[:, 'address_line2']]
        city = [a.replace(",", '') for a in self.df_users.loc[:, 'address_city']]

        self.df_users.loc[:, 'comments'] = [((a + ' ' + b).strip() + ' ' + c).strip() for a, b, c in zip(addr1, addr2, city)]

        # Clean up city names - remove gibberish values
        i = 0
        while i < len(self.df_users.loc[:, 'address_city']):
            tokens = self.df_users.loc[i, 'address_city'].split(' ')
            if len(tokens) > 2:
                self.df_users.loc[i, 'address_city'] = ''
            else:
                characters = list(self.df_users.loc[i, 'address_city'])
                for c in characters:
                    # if not letters or space or single quote
                    if not ((c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z') or c == ' ' or c == "'"):
                        self.df_users.loc[i, 'address_city'] = ''
            i += 1

        # Set address line1 and line2 to blanks (this syntax sets entire column to one value)
        self.df_users.loc[:, 'address_line1'] = ''
        self.df_users.loc[:, 'address_line2'] = ''

    @staticmethod
    def get_highest_level(somelist):
        if 11 in somelist and 7 in somelist:
            return 7
        elif 11 in somelist:
            return 11
        elif 7 in somelist:
            return 7
        elif 6 in somelist:
            return 6
        elif 9 in somelist:
            return 9
        else:
            return 8

    # Assign a profile id to each user
    def get_security_profile(self):

        # Assign security profile ids manually
        level_admin = ['ron.balajadia', 'jihae.goo', 'elizabeth.trevias', 'heather.winfield-smith', 'jihyun.choi']
        level_data_analyst = ['sandeep.chintabathina', 'michael.li', 'gail.watkins']
        level_help_desk = ['theresa.borja', 'stephanie.misaki', 'thomas.jones', 'macrommel.bautista','nathaniel.antonio','myra.meade']
        level_vaccine_supply_distribution = ['josephine.araki', 'loraine.lim', 'melvin.reyes', 'elizabeth.ricon',
                                             'esera.vegas', 'kealohi.corpos']
        level_epidemiology_surveillance = ['augustina.manuzak', 'kenneth.evans', 'laarni.igawa', 'cathy.wu',
                                           'kaylynn.adolfo', 'anjali.vyas']

        for i in range(len(self.df_users)):
            username = self.df_users.loc[i, 'username']
            if username in level_admin:
                self.df_users.loc[i, 'security_profile_id'] = 1
            elif username in level_data_analyst:
                self.df_users.loc[i, 'security_profile_id'] = 2
            elif username in level_help_desk:
                self.df_users.loc[i, 'security_profile_id'] = 3
            elif username in level_vaccine_supply_distribution:
                self.df_users.loc[i, 'security_profile_id'] = 4
            elif username in level_epidemiology_surveillance:
                self.df_users.loc[i, 'security_profile_id'] = 5
            else:
                self.df_users.loc[i, 'security_profile_id'] = ''

        #print(self.df_userprofile.info())
        # For Frank Baum, set hl7_sender to Y and profile id to 7 (vtrcks pin + hl7 sender)
        results=self.df_userprofile[self.df_userprofile['CLINIC_UNIQUE_ID']==4384]
        for idx in results.index:
            self.df_userprofile.loc[idx,'HL7_SENDER']='Y'
            self.df_userprofile.loc[idx,'SECURITY_PROFILE_ID']=7

        # Group by user id to determine what profile id to assign
        groups = self.df_userprofile.groupby(by=['OTHER_USER_IDENTIFIER'])
        # apply function "get_highest_level" to every group x
        # function uses values listed in security_profile_id column
        profile_ids = groups.apply(lambda x: Users.get_highest_level(list(x['SECURITY_PROFILE_ID']))).reset_index(name='id')

        # profile_ids is a new dataframe with a new column called id that has the returned values
        mapper = {}
        for i in range(len(profile_ids)):
            user_id = profile_ids.loc[i, 'OTHER_USER_IDENTIFIER']
            mapper[user_id] = profile_ids.loc[i,'id']


        for i in range(len(self.df_users)):
            if self.df_users.loc[i, 'security_profile_id'] == '':
                try:
                    self.df_users.loc[i, 'security_profile_id'] = mapper[self.df_users.loc[i, 'other_user_identifier']]
                except:
                    pass

        print("Security profile ids mapped")

    # write to csv
    def build_users_csv(self):
        # Write dataframe to csv
        self.df_users.to_csv('db_files/users_bulk_insert.csv',index=False)
        print(len(self.df_users),'users written to file')

    @staticmethod
    def is_contained(df_set1,df_set2,key):
        # Check what elements of set2 are not in set 1
        codes = list(df_set1.loc[:, key])
        somelist = []
        for code in df_set2.loc[:, key]:
            if code not in codes:
                somelist.append(code)
        return somelist

    # prepare user clinics data
    def prepare_user_clinics(self):
        #Rename columns
        for col in list(self.df_user_clinics.columns):
            self.df_user_clinics.rename(columns={col: col.lower()}, inplace=True)
        print("num of user-clinic entries",len(self.df_user_clinics))
        # drop duplicates
        self.df_user_clinics.drop_duplicates(inplace=True,ignore_index=True)
        print("num of user-clinic entries after dropping duplicates", len(self.df_user_clinics))

        # Get current clinics in container
        # Read file containing clinics in clinics container
        df_clinics = pd.read_csv('../clinics/clinics_in_container.csv', dtype={'clinic_unique_id': str}, na_filter=False)

        # Compare clinics in user-clinics and clinics container
        somelist = Users.is_contained(self.df_user_clinics,df_clinics,'clinic_unique_id')
        print("orgs in clinic container but not in user_clinics - either clinic is inactive or does not have a user")
        print(somelist)

        somelist = Users.is_contained(df_clinics,self.df_user_clinics, 'clinic_unique_id')
        print("orgs in user_clinics but not in clinics container")
        print(somelist)

        # Remove duplicates
        somelist = list(set(somelist))
        # Have to get rid of user clinics not in clinics container
        if len(somelist)>0:
            for id in somelist:
                # Get the sub df containing ids to be removed
                print('Dropping',id,'from user_clinics')
                df_user_clinics_sub = self.df_user_clinics[self.df_user_clinics['clinic_unique_id'] == id]
                # Drop every row matching index
                for idx in df_user_clinics_sub.index:
                    self.df_user_clinics.drop(idx, axis=0, inplace=True)

            self.df_user_clinics.reset_index(drop=True,inplace=True)

        # Compare users in user-clinics and users container
        somelist = Users.is_contained(self.df_user_clinics,self.df_users,key='other_user_identifier')
        print('Users in users container but not in user-clinics')
        print(somelist)

        # Remove duplicates
        somelist = list(set(somelist))
        # Have to get rid of users not in users container
        if len(somelist) > 0:
            for id in somelist:
                # Get the sub df containing ids to be removed
                print('Dropping', id, 'from users')
                df_users_sub = self.df_users[self.df_users['other_user_identifier'] == id]
                # Drop every row matching index
                for idx in df_users_sub.index:
                    self.df_users.drop(idx, axis=0, inplace=True)

            self.df_users.reset_index(drop=True, inplace=True)

        somelist = Users.is_contained(self.df_users, self.df_user_clinics, key='other_user_identifier')
        print('Users in user_clinics but not in users container')
        print(somelist)

        # Remove duplicates
        somelist = list(set(somelist))
        # Have to get rid of users not in users container
        if len(somelist)>0:
            for id in somelist:
                # Get the sub df containing ids to be removed
                print('Dropping',id,'from user_clinics')
                df_user_clinics_sub = self.df_user_clinics[self.df_user_clinics['other_user_identifier'] == id]
                # Drop every row matching index
                for idx in df_user_clinics_sub.index:
                    self.df_user_clinics.drop(idx, axis=0, inplace=True)

            self.df_user_clinics.reset_index(drop=True,inplace=True)

        print('Num of user-clinic entries after comparison',len(self.df_user_clinics))

    # write to csv
    def build_user_clinics_csv(self):
        # Write dataframe to csv
        self.df_user_clinics.to_csv('db_files/user_clinics_bulk_insert.csv', index=False)
        print(len(self.df_user_clinics), 'user-clinics written to file')

    def prepare_hl7_users_clinics(self):
        # Rename df_hl7_clinics columns
        for col in list(self.df_hl7_clinics.columns):
            self.df_hl7_clinics.rename(columns={col: col.lower()}, inplace=True)

        #print(self.df_hl7_clinics.info())
        # Remove spaces from names
        self.df_hl7_clinics.loc[:, 'hl7_sender'] = [v.strip().replace(',','') for v in self.df_hl7_clinics.loc[:, 'hl7_sender']]

        # Create a row for clinic (Frank Baum) 4384 with STC Health as hl7 sender
        df_new = pd.DataFrame([{'hl7_sender':'STC Health - Hub','clinic_unique_id':'4384'}])

        # Add row to existing df
        self.df_hl7_clinics = pd.concat([self.df_hl7_clinics,df_new])

        self.df_hl7_clinics.reset_index(drop=True,inplace=True)


        # Mapping hl7 senders to their abbreviations
        # mapping to abbreviations
        mapper = {}
        mapper['Hawaii Pacific Health'] = 'hawaii_pacific'
        #mapper['CVS/Pharmacy - STC'] = 'cvs_stc'   # Removed 4/2
        mapper["Queen's Health System"] = 'queens'
        mapper['Athena Health'] = 'athena_health'
        mapper['Kaiser Permanente'] = 'kaiser'
        mapper['Cerner Corporation - ALL Hub'] = 'cerner_all_hub'
        mapper['HICHC Parent'] = 'hichc'
        #mapper['Walgreens - STC'] = 'walgreens_stc' # Removed 4/2
        #mapper['Safeway - STC'] = 'safeway_stc'  # Removed 4/2
        mapper['Waianae Coast Comp HC Hub'] = 'waianae_coast'
        mapper['Iron Bridge - Hub'] = 'iron_bridge'
        # mapper['PrescribeWellness- Hub'] = 'prescribe_wellness'  # Renamed to outcomes
        # mapper['Costco Pharmacy Hub - PrescribeWellness'] = 'costco_prescribe_wellness'
        mapper['Hawaii Health Systems Corp'] = 'hhsc'
        #mapper["Wal-Mart and Sam's Club Pharmacy - STC"] = 'walmart_sams_stc'
        mapper['Alliance of Chicago'] = 'alliance_chicago'
        mapper['eClinicalWorks - Hub'] = 'eclinicalworks'
        mapper['Maui Health Systems - Hub'] = 'maui_health'
        mapper['Medical Informatics Engineering Inc.'] = 'medical_informatics_engg'
        mapper['STC Health - Hub'] = 'stc_health'
        mapper['HCNetwork Parent'] = 'hc_network'
        #mapper['Cerner Corporation - Hub'] = 'cerner_hub'   # Removed 4/2
        mapper['Waimanalo Health Center Hub'] = 'waimanalo_health'
        #mapper['Medical Transcription Billing Corp - MTBC'] = 'med_transcription_billing' #Removed 4/12
        mapper['Kokua Kalihi Valley - Parent'] = 'kokua_kalihi_valley'
        mapper['Netsmart Technologies'] = 'netsmart_tech'
        mapper['Flatiron Health - Parent'] = 'flatiron'
        # mapper['Wahiawa General Hospital - Parent'] = 'wahiawa_general'
        mapper['OCHIN'] = 'ochin'
        mapper['Physicians Computer Company'] = 'physicians_computer'
        mapper['Point and Click Solutions Inc.'] = 'point_and_click'
        # mapper['AthenaPractice - Hub'] = 'athena_practice'
        # mapper['Quatris Healthco'] = 'quatris'
        mapper['Outcomes'] ='outcomes'  # New addition 3/4/25 will replace PrescribeWellness - HUB


        # Create hl7 users
        # first name  - abbreviation of hl7 sender
        first_name = []
        for key in mapper.keys():
            first_name.append(mapper[key])

        # Create lastnames containing the word HL7
        last_name = 'HL7 ' * len(mapper.keys())
        last_name = last_name.strip().split(' ')

        # Add HL7 in front of first
        username = []
        for f in first_name:
            username.append('HL7.' + f)

        self.df_hl7_users = pd.DataFrame(zip(first_name, last_name, username),
                                    columns=['first_name', 'last_name', 'username'])

        # Add username to df_hl7_clinics
        # Create username as HL7.abbreviated org name
        self.df_hl7_clinics.loc[:, 'username'] = ['HL7.' + mapper[h] for h in self.df_hl7_clinics.loc[:, 'hl7_sender']]

        # Drop hl7_sender column
        self.df_hl7_clinics.drop(['hl7_sender'],axis=1,inplace=True)

        self.df_hl7_clinics.drop_duplicates(inplace=True, ignore_index=True)
        print("Number of hl7 clinics after dropping duplicates", len(self.df_hl7_clinics))

    # write to csv
    def build_hl7_users_clinics_csv(self):
        # Write dataframe to csv
        self.df_hl7_users.to_csv('db_files/hl7_users_bulk_insert.csv', index=False)
        print(len(self.df_hl7_users), 'hl7 users written to file')

        self.df_hl7_clinics.to_csv('db_files/hl7_clinics_bulk_insert.csv', index=False)
        print(len(self.df_hl7_clinics), 'hl7 clinics written to file')



#  Copyright (c) 2025. Sandeep Chintabathina

# Code to map school data into schools container

import pandas as pd
import numpy as np

class Schools:

    def __init__(self):
        self.df_schools = pd.read_csv('input/schools.csv',dtype={'mailing_address_zip':str,
                                                                 'physical_address_zip':str},na_filter=False)

        self.df_school_districts = pd.read_csv('input/school_districts.csv',na_filter=False)

        self.prepare_schools()

    def prepare_schools(self):
        # Drop duplicates
        self.df_schools = self.df_schools.drop_duplicates()
        self.df_schools = self.df_schools.drop_duplicates(subset=['school_name'])
        self.df_schools.reset_index(drop=True,inplace=True)
        print('Dropping duplicate schools - num of schools',len(self.df_schools))

        self.df_school_districts = self.df_school_districts.drop_duplicates()
        self.df_school_districts = self.df_school_districts.drop_duplicates(subset=['district_name'])
        self.df_school_districts.reset_index(drop=True, inplace=True)
        print('Dropping duplicate school districts - num of school districts', len(self.df_school_districts))

        # Drop empty columns
        self.df_schools.drop(['school_bldg_number','primary_contact_first_name','primary_contact_last_name','primary_contact_email_address',
                              'secondary_contact_first_name','secondary_contact_last_name','secondary_contact_phone_number','secondary_contact_fax_number',
                              'secondary_contact_email_address','approximate_capacity','mailing_address_line2','physical_address_line2'],axis=1,inplace=True)
        #print(self.df_schools.columns)

        self.df_school_districts.drop(['primary_contact_first_name','primary_contact_last_name','secondary_contact_first_name',
                                       'secondary_contact_last_name','secondary_contact_phone_number','secondary_contact_fax_number',
                                       'secondary_contact_email_address','mailing_address_line2','physical_address_line2'],axis=1,inplace=True)
        #print(self.df_school_districts.columns)

        #print(self.df_school_districts.info())
        # Clean up commas and spaces
        self.df_schools.loc[:,'school_name'] = [name.replace(',','').strip() for name in self.df_schools.loc[:,'school_name']]
        self.df_schools.loc[:, 'status_code'] = [status.strip() for status in self.df_schools.loc[:, 'status_code']]
        self.df_schools.loc[:, 'principal_name'] = [name.replace(',', '').strip() for name in self.df_schools.loc[:, 'principal_name']]
        self.df_schools.loc[:, 'primary_contact_phone_number'] = [num.strip() for num in self.df_schools.loc[:, 'primary_contact_phone_number']]
        self.df_schools.loc[:, 'primary_contact_fax_number'] = [num.strip() for num in self.df_schools.loc[:,'primary_contact_fax_number']]
        self.df_schools.loc[:, 'mailing_address_line1'] = [addr.replace(',', '').strip() for addr in self.df_schools.loc[:, 'mailing_address_line1']]
        self.df_schools.loc[:, 'mailing_address_city'] = [city.replace(',', '').strip() for city in self.df_schools.loc[:, 'mailing_address_city']]
        self.df_schools.loc[:, 'mailing_address_county'] = [county.split(' ')[0] for county in self.df_schools.loc[:, 'mailing_address_county']]
        self.df_schools.loc[:, 'mailing_address_state'] = [state.strip() for state in self.df_schools.loc[:, 'mailing_address_state']]
        self.df_schools.loc[:, 'mailing_address_zip'] = [zip.strip() for zip in self.df_schools.loc[:, 'mailing_address_zip']]
        self.df_schools.loc[:, 'physical_address_line1'] = self.df_schools.loc[:, 'mailing_address_line1']
        self.df_schools.loc[:, 'physical_address_city'] = self.df_schools.loc[:, 'mailing_address_city']
        self.df_schools.loc[:, 'physical_address_county'] =  self.df_schools.loc[:, 'mailing_address_county']
        self.df_schools.loc[:, 'physical_address_state'] =  self.df_schools.loc[:, 'mailing_address_state']
        self.df_schools.loc[:, 'physical_address_zip'] =  self.df_schools.loc[:, 'mailing_address_zip']

        self.df_school_districts.loc[:,'district_name'] = [name.replace(',','').strip() for name in self.df_school_districts.loc[:,'district_name']]
        #self.df_school_districts.loc[:, 'district_code'] = [code.strip() for code in self.df_school_districts.loc[:, 'district_code']]
        self.df_school_districts.loc[:, 'status_code'] = [code.strip() for code in self.df_school_districts.loc[:, 'status_code']]
        self.df_school_districts.loc[:, 'superintendent_name'] = [name.replace(',','').strip() for name in self.df_school_districts.loc[:, 'superintendent_name']]
        self.df_school_districts.loc[:, 'primary_contact_phone_number'] = [num.strip() for num in self.df_school_districts.loc[:, 'primary_contact_phone_number']]
        self.df_school_districts.loc[:, 'primary_contact_fax_number'] = [num.strip() for num in self.df_school_districts.loc[:, 'primary_contact_fax_number']]
        self.df_school_districts.loc[:, 'primary_contact_email_address'] = [addr.strip() for addr in self.df_school_districts.loc[:,'primary_contact_email_address']]
        self.df_school_districts.loc[:, 'mailing_address_line1'] = [addr.replace(',','').strip() for addr in self.df_school_districts.loc[:,'mailing_address_line1']]
        self.df_school_districts.loc[:, 'mailing_address_city'] = [city.replace(',', '').strip() for city in self.df_school_districts.loc[:,'mailing_address_city']]
        self.df_school_districts.loc[:, 'mailing_address_county'] = [county.strip() for county in self.df_school_districts.loc[:,'mailing_address_county']]
        self.df_school_districts.loc[:, 'mailing_address_state'] = [state.strip() for state in self.df_school_districts.loc[:,'mailing_address_state']]
        self.df_school_districts.loc[:, 'mailing_address_zip'] = [zip.strip() for zip in self.df_school_districts.loc[:,'mailing_address_zip']]
        self.df_school_districts.loc[:, 'physical_address_line1'] = self.df_school_districts.loc[:, 'mailing_address_line1']
        self.df_school_districts.loc[:, 'physical_address_city'] = self.df_school_districts.loc[:, 'mailing_address_city']
        self.df_school_districts.loc[:, 'physical_address_county'] = self.df_school_districts.loc[:, 'mailing_address_county']
        self.df_school_districts.loc[:, 'physical_address_state'] = self.df_school_districts.loc[:, 'mailing_address_state']
        self.df_school_districts.loc[:, 'physical_address_zip'] = self.df_school_districts.loc[:, 'mailing_address_zip']

        school_codes = self.df_schools.loc[:,'school_type_code_id']
        district_codes = self.df_schools.loc[:,'district_code']
        # Calculate district code based on school code
        self.df_schools.loc[:,'district_code'] = [17 if school_code==1 else 16 if school_code==3 else district_code
                                                  for (school_code,district_code) in zip(school_codes,district_codes)]

        # write schools to csv
        self.df_schools.to_csv('db_files/schools_bulk_insert.csv', index=False)
        # Write school districts to csv
        self.df_school_districts.to_csv('db_files/school_districts_bulk_insert.csv', index=False)

        print('Wrote',len(self.df_schools),'schools to file')
        print('Wrote', len(self.df_school_districts), 'school districts to file')









# Code to map clinic data into clinic container

import pandas as pd
import numpy as np

class Clinic:

    def __init__(self):
        self.df_clinics = pd.read_csv('input/clinics_data.csv',dtype={'MAILING_ADDRESS_ZIP':str,
                                'CLINIC_CODE':str,
                                'MAILING_ADDRESS_LINE2':str,
                                'MAILING_ADDRESS_CITY':str,
                                'PHYSICAL_ADDRESS_ZIP':str,
                                'SENDS_HL7_MESSAGES':str,
                                'HL7_SENDING_CLINIC_UNIQUE_ID':str,
                                'HL7_FACILITY_CODE': str,
                                'CLINIC_UNIQUE_ID':str,
                                'CLINIC_LEGACY_DATA_STATUS':str,
                                'CLINIC_ONBOARDING_STATUSES':str},
                                na_filter=False)
        self.prepare_data()

    def prepare_data(self):
        # Rename columns to lower case
        for c in list(self.df_clinics.columns):
            self.df_clinics.rename(columns={c: c.lower()}, inplace=True)

        self.df_clinics.loc[:, 'mailing_address_line1'] = [address.replace(",", "").strip() for address in
                                                      self.df_clinics.loc[:, 'mailing_address_line1']]
        self.df_clinics.loc[:, 'mailing_address_city'] = [str(city).replace(",", "").title().strip() for city in
                                                     self.df_clinics.loc[:, 'mailing_address_city']]
        self.df_clinics.loc[:, 'mailing_address_county'] = [str(county).title().strip() for county in
                                                       self.df_clinics.loc[:, 'mailing_address_county']]
        self.df_clinics.loc[:, 'mailing_address_zip'] = [str(zip).strip() for zip in
                                                    self.df_clinics.loc[:, 'mailing_address_zip']]
        self.df_clinics.loc[:, 'mailing_address_state'] = [str(state).strip() for state in
                                                      self.df_clinics.loc[:, 'mailing_address_state']]

        # Use physical address if available otherwise use mailing address
        self.df_clinics.loc[:, 'physical_address_line1'] = [address.replace(",", "").strip() if address.strip()!='' else mailing for (address,mailing) in
                                                           zip(self.df_clinics.loc[:, 'physical_address_line1'],self.df_clinics.loc[:,'mailing_address_line1'])]
        self.df_clinics.loc[:, 'physical_address_city'] = [str(city).replace(",", "").title().strip() if city.strip()!='' else mailing for (city,mailing) in
                                                          zip(self.df_clinics.loc[:, 'physical_address_city'],self.df_clinics.loc[:, 'mailing_address_city'])]
        self.df_clinics.loc[:, 'physical_address_county'] = [str(county).title().strip() if county.strip()!='' else mailing for (county,mailing) in
                                                            zip(self.df_clinics.loc[:, 'physical_address_county'],self.df_clinics.loc[:, 'mailing_address_county'])]
        self.df_clinics.loc[:, 'physical_address_zip'] = [str(zip_code).strip() if zip_code.strip()!='' else mailing for (zip_code,mailing) in
                                                         zip(self.df_clinics.loc[:, 'physical_address_zip'],self.df_clinics.loc[:, 'mailing_address_zip'])]
        self.df_clinics.loc[:, 'physical_address_state'] = [str(state).replace(",",'').strip() if state.strip()!='' else mailing for (state,mailing) in
                                                           zip(self.df_clinics.loc[:, 'physical_address_state'],self.df_clinics.loc[:, 'mailing_address_state'])]

        self.df_clinics.loc[:, 'clinic_desc'] = [clinic.replace(",", "").strip() for clinic in
                                            self.df_clinics.loc[:, 'clinic_desc']]
        self.df_clinics.loc[:, 'physician_name'] = [phy.replace(",", "").title().strip() for phy in
                                               self.df_clinics.loc[:, 'physician_name']]

        print("Num of clinic entries",len(self.df_clinics))

        self.df_clinics.drop_duplicates(inplace=True, ignore_index=True)
        print("Num of clinic entries after dropping entire duplicate rows", len(self.df_clinics))

        # Drop ones that have duplicates clinic ids too
        self.df_clinics.drop_duplicates(subset=['clinic_unique_id'],inplace=True, ignore_index=True)
        print("Num of clinic entries after dropping duplicate ids", len(self.df_clinics))


    # Get clinic type of practice
    def get_practice_code(self):
        # Shorten the names to less than 35 characters because of DB restriction....add more as needed
        cat_list = []
        for category in self.df_clinics.loc[:, 'provider_type_of_practice_code_id']:
            if category == 'Private Hospital as agent of FQHC or RHC':
                cat_list.append('Private Hospital as FQHC/RHC')
            elif category == 'Other Public Health as agent of FQHC or RHC':
                cat_list.append('Public Other as FQHC/RHC')
            elif category == 'Private Practice as agent of FQHC/RHC':
                cat_list.append('Private Practice as FQHC/RHC')
            else:
                cat_list.append(category)


        self.df_clinics.loc[:, 'provider_type_of_practice_code_id'] = cat_list

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

        practice_type_dict = {}
        for t in practice_type:
            practice_type_dict[t[1]] = t[0]

        somelist = []
        for p_type in self.df_clinics.loc[:, 'provider_type_of_practice_code_id']:
            try:
                somelist.append(practice_type_dict[p_type])
            except:
                somelist.append('')

        self.df_clinics.loc[:, 'provider_type_of_practice_code_id'] = somelist

        print('Practice codes mapped')

    # Get phone and fax number
    def get_contact_num(self):
        # Get the contact number from supplementary files
        df_clinic_contact = pd.read_csv('input/clinic_contact_number.csv', na_filter=False)

        for c in list(df_clinic_contact.columns):
            df_clinic_contact.rename(columns={c: c.lower()}, inplace=True)
        # Format phone numbers
        df_clinic_contact.loc[:, 'contact_primary_phone_number'] = [ph[:7] + '-' + ph[7:] if ph != '' else ph for ph in
                                                                    df_clinic_contact.loc[:,'contact_primary_phone_number']]

        df_clinic_contact.loc[:, 'contact_fax_number'] = [ph[:7] + '-' + ph[7:] if ph != '' else ph for ph in
                                                          df_clinic_contact.loc[:, 'contact_fax_number']]

        df_clinic_contact.loc[:, 'clinic_desc'] = [clinic.replace(",", '') for clinic in
                                                   df_clinic_contact.loc[:, 'clinic_desc']]
        # Merge it with df_clinics
        self.df_clinics = self.df_clinics.merge(df_clinic_contact, on='clinic_desc')

        print("Added contact and fax number")
        print('Num of clinic entries',len(self.df_clinics))


    # Get secondary contact info
    def get_secondary_contact(self):
        # Get data from file
        df_clinic_secondary = pd.read_csv('input/clinic_secondary_contact.csv', na_filter=False)

        for c in list(df_clinic_secondary.columns):
            df_clinic_secondary.rename(columns={c: c.lower()}, inplace=True)

        # Get rid of duplicate rows
        df_clinic_secondary.drop_duplicates(inplace=True, ignore_index=True)

        # Get rid of duplicate clinic names too
        df_clinic_secondary.drop_duplicates(subset=['clinic_desc'], inplace=True, ignore_index=True)
        # Not needed
        df_clinic_secondary.reset_index(drop=True, inplace=True)
        # Format number
        df_clinic_secondary.loc[:, 'contact_secondary_phone_number'] = [ph[:7] + '-' + ph[7:] if ph != '' else ph for ph
                                                                        in df_clinic_secondary.loc[:,'contact_secondary_phone_number']]
        # Get rid of commas
        df_clinic_secondary.loc[:, 'clinic_desc'] = [clinic.replace(',', '') for clinic in
                                                     df_clinic_secondary.loc[:, 'clinic_desc']]

        self.df_clinics = self.df_clinics.merge(df_clinic_secondary, on='clinic_desc')
        print("Added secondary number")
        print('Num of clinic entries', len(self.df_clinics))


    # Get site admin info
    def get_site_admin(self):
        # Get site admin info
        df_clinic_site = pd.read_csv('input/clinic_site_admin.csv', na_filter=False)

        for c in list(df_clinic_site.columns):
            df_clinic_site.rename(columns={c: c.lower()}, inplace=True)
        # Format numbers
        df_clinic_site.loc[:, 'site_administrator_phone_number'] = [ph[:7] + '-' + ph[7:] if ph != '' else ph for ph in
                                                                    df_clinic_site.loc[:,'site_administrator_phone_number']]

        df_clinic_site.loc[:, 'site_administrator_fax_number'] = [ph[:7] + '-' + ph[7:] if ph != '' else ph for ph in
                                                                  df_clinic_site.loc[:,'site_administrator_fax_number']]

        # Adjusting the title
        df_clinic_site.loc[:, 'site_administrator_title'] = [title.replace('HIR', 'HiSIS') for title in
                                                             df_clinic_site.loc[:, 'site_administrator_title']]

        df_clinic_site.loc[:, 'site_administrator_name'] = [name.replace(",", "").strip() for name in df_clinic_site.loc[:, 'site_administrator_name']]

        df_clinic_site.loc[:, 'site_administrator_email_address'] = [name.replace(",", "").strip() for name in df_clinic_site.loc[:, 'site_administrator_email_address']]

        # Remove commas
        df_clinic_site.loc[:, 'clinic_desc'] = [clinic.replace(",", "") for clinic in df_clinic_site.loc[:, 'clinic_desc']]

        # Merge it with df_clinics
        self.df_clinics = self.df_clinics.merge(df_clinic_site, on='clinic_desc')
        print("Added site admin info")
        print('Num of clinic entries', len(self.df_clinics))


    # Get tech contact info
    def get_tech_contact(self):
        # Get tech contact info
        df_clinic_tech = pd.read_csv('input/clinic_tech_contact.csv', na_filter=False)

        for c in list(df_clinic_tech.columns):
            df_clinic_tech.rename(columns={c: c.lower()}, inplace=True)

        # Format numbers
        df_clinic_tech.loc[:, 'tech_contact_phone_number'] = [ph[:7] + '-' + ph[7:] if ph != '' else ph for ph in
                                                              df_clinic_tech.loc[:, 'tech_contact_phone_number']]

        df_clinic_tech.loc[:, 'tech_contact_fax_number'] = [ph[:7] + '-' + ph[7:] if ph != '' else ph for ph in
                                                            df_clinic_tech.loc[:, 'tech_contact_fax_number']]
        # Adjust title
        df_clinic_tech.loc[:, 'tech_contact_title'] = [title + ' Contact' for title in
                                                       df_clinic_tech.loc[:, 'tech_contact_title']]
        # Remove commas
        df_clinic_tech.loc[:, 'clinic_desc'] = [clinic.replace(",", "") for clinic in
                                                df_clinic_tech.loc[:, 'clinic_desc']]
        df_clinic_tech.loc[:, 'tech_contact_name'] = [clinic.replace(",", "") for clinic in
                                                      df_clinic_tech.loc[:, 'tech_contact_name']]
        df_clinic_tech.loc[:, 'tech_contact_email_address'] = [clinic.replace(",", "") for clinic in
                                                               df_clinic_tech.loc[:, 'tech_contact_email_address']]

        # Merge it with df_clinics
        self.df_clinics = self.df_clinics.merge(df_clinic_tech, on='clinic_desc')

        print("Added tech contact info")
        print('Num of clinic entries', len(self.df_clinics))

    # Add patient record clinic
    def add_pseudo_clinic(self):
        new_clinic = pd.DataFrame([{'clinic_desc': 'Patient Record', 'status_code': 'A', 'provider_type_of_practice_code_id': 2,
                                    'mailing_address_line1': '1250 Punchbowl St', 'mailing_address_line2': '',
                                    'mailing_address_city': 'Honolulu',
                                    'mailing_address_county': 'Honolulu', 'mailing_address_state': 'HI',
                                    'mailing_address_zip': '96813',
                                    'physical_address_line1': '1250 Punchbowl St', 'physical_address_line2': '',
                                    'physical_address_city': 'Honolulu',
                                    'physical_address_county': 'Honolulu', 'physical_address_state': 'HI',
                                    'physical_address_zip': '96813',
                                    'vfc_pin': '', 'hl7_facility_code': '', 'ehr_vendor': '',
                                    'clinic_unique_id': '99999',
                                    'inventory_tracking_type': 1, 'funding_source_vfc': 0, 'funding_source_state': 0,
                                    'funding_source_private': 0, 'funding_source_317': 0, 'funding_source_chip': 0,
                                    'funding_source_pandemic': 0,
                                    'clinic_legacy_data_status': '5', 'clinic_onboarding_statuses': '12'}])

        self.df_clinics = pd.concat([self.df_clinics, new_clinic])

        self.df_clinics.reset_index(drop=True, inplace=True)
        # Replace nan values
        self.df_clinics.replace(np.nan, '', inplace=True)
        print('Patient Record clinic added, num of clinics',len(self.df_clinics))

    # Calculate 'sends_hl7_messages' and 'hl7_facility_code' columns
    def get_sends_hl7_messages(self):

        # hl7 facility code is the clinic unique id but only filled for ones that are active and sending hl7

        # If clinic is active and has a hl7 facility code then it sends hl7 messages
        # If it is active but does not have a hl7 facility code then it does not send hl7 messages
        # If inactive it does not send hl7 messages
        for i in range(len(self.df_clinics)):
            if self.df_clinics.loc[i, 'status_code'] == 'A':
                if self.df_clinics.loc[i, 'hl7_facility_code'] != '':
                    self.df_clinics.loc[i, 'sends_hl7_messages'] = 'Y'
                else:
                    self.df_clinics.loc[i, 'sends_hl7_messages'] = 'N'
            else:
                self.df_clinics.loc[i, 'sends_hl7_messages'] = 'N'

        self.df_clinics.loc[:, 'hl7_facility_code'] = ['HI' + (str(code).zfill(5)) if code != '' else code for code in
                                                  self.df_clinics.loc[:, 'hl7_facility_code']]

        # Frank Baum special case
        # Set sends_hl7_message to 'Y' and add hl7 facility code
        df_special = self.df_clinics[self.df_clinics['clinic_unique_id']=='4384']
        #print('Frank Baum',df_special)
        for idx in df_special.index:
            self.df_clinics.loc[idx, 'sends_hl7_messages'] = 'Y'
            self.df_clinics.loc[idx,'hl7_facility_code'] = 'HI'+'04384'

        print('sends hl7 and hl7 facility code calculated')

    # Determine ehr vendor product id
    def get_ehr_vendor_product_id(self):
        # Envision list
        ehr_vendor_list = [(1, 'Acrendo Software, Inc - A.I. Med Pro'),
                           (2, 'Acumen - Acumen'),
                           (3, 'ADL Data Systems - ADL Data Systems'),
                           (4, 'AdvancedMD - AdvancedMD'),
                           (5, 'AdvantaChart Inc - AdvantaChart'),
                           (6, 'Allscripts - Allscripts'),
                           (7, 'Allscripts - Allscripts ED'),
                           (8, 'Allscripts - Allscripts Enterprise EHR'),
                           (9, 'Allscripts - Allscripts ePrescribe'),
                           (10, 'Allscripts - Allscripts FollowMyHealth'),
                           (11, 'Allscripts - Allscripts Professional EHR'),
                           (12, 'Allscripts - Allscripts TouchWorks EHR (Complete)'),
                           (13, 'Allscripts - Allscripts TouchWorks EHR (Modular)'),
                           (14, 'Allscripts - dbMotion'),
                           (15, 'Allscripts - Sunrise Acute Care'),
                           (16, 'Allscripts - Sunrise Ambulatory Care'),
                           (17, 'Alphamed Technologies - Medisoft Clinical'),
                           (18, 'Alphamed Technologies - Lytec MD'),
                           (19, 'Alphamed Technologies - Practice Partner'),
                           (20, 'Altos Solutions, Inc - OncoEMR'),
                           (21, 'AmazingCharts.com, Inc - Amazing Charts'),
                           (22, 'AmazingCharts.com, Inc - Caretracker PM/EMR'),
                           (23, 'AmazingCharts.com, Inc - Clinix'),
                           (24, 'AmazingCharts.com, Inc - digiChart EMR'),
                           (25, 'AmazingCharts.com, Inc - MEDfx'),
                           (26, 'American Healthtech - American Healthtech'),
                           (27, 'American Immunization Registry Association - AIRA'),
                           (28, 'AMS Software, Inc. - AMS Software, Inc.'),
                           (29, 'Aprima Medical Software, Inc - Aprima Medical Software, Inc'),
                           (30, 'Aprima Medical Software, Inc - EHR'),
                           (31, 'Aprima Medical Software, Inc - PRM 2014'),
                           (32, 'Ardenet Health Services - Ardenet Health Services'),
                           (33, 'athenahealth, Inc - athenaClinicals'),
                           (34, 'athenahealth, Inc - athenaCommunicator'),
                           (35, 'athenahealth, Inc - athenahealth, Inc'),
                           (36, 'Atlas MD - Atlas MD'),
                           (37, 'Atrium Health - Carolinas Health Care'),
                           (38, 'Bizmatics - Bizmatics'),
                           (39, 'Bizmatics - PrognoCIS'),
                           (40, 'Care Management System Healthgram - Healthgram'),
                           (41, 'CareCloud - CareCloud'),
                           (42, 'Cerner Corporation - Cerner Community Behavioral Health'),
                           (43, 'Cerner Corporation - Cerner Corporation'),
                           (44, 'Cerner Corporation - Cerner Network Patient Viewer'),
                           (45, 'Cerner Corporation - Cerner Patient Portal and FirstNet'),
                           (46, 'Cerner Corporation - Cerner Patient Portal and Powerchart'),
                           (47,
                            'Cerner Corporation - Cerner Sentinel Cloud Audit Reporting and Cerner Sentinel Cloud Audit Service'),
                           (48, 'Cerner Corporation - FirstNet'),
                           (49, 'Cerner Corporation - FirstNet (Clinical)'),
                           (50, 'Cerner Corporation - FirstNet (CQM)'),
                           (51, 'Cerner Corporation - FirstNet (eRX)'),
                           (52, 'Cerner Corporation - FirstNet (Image Results)'),
                           (53, 'Cerner Corporation - HealtheLife and FirstNet'),
                           (54, 'Cerner Corporation - HealtheLife and Powerchart'),
                           (55, 'Cerner Corporation - HealthSentry'),
                           (56, 'Cerner Corporation - P2 Sentinel (Powered by Sensage)'),
                           (57, 'Cerner Corporation - PathNet'),
                           (58, 'Cerner Corporation - PowerChart'),
                           (59, 'Cerner Corporation - PowerChart (All CQMs)'),
                           (60, 'Cerner Corporation - Powerchart (Clinical)'),
                           (61, 'Cerner Corporation - Powerchart (CQM)'),
                           (62, 'Cerner Corporation - Powerchart (eRX)'),
                           (63, 'Cerner Corporation - Powerchart (Image Results)'),
                           (64, 'Cerner Corporation - Powerchart Touch Ambulatory'),
                           (65, 'Cerner Corporation - Powerchart Touch Inpatient'),
                           (66, 'CGM - CompuGroup Medical - CGM - CompuGroup Medical'),
                           (67, 'CGS - PC-ACE Pro32'),
                           (68, 'ChiroTouch - ChiroTouch'),
                           (69, 'CHS - Community Health Systems - CHS - Community Health Systems'),
                           (70, 'Citrix IT - Health'),
                           (71, 'Compugroup Medical - Enterprise EHR'),
                           (72, 'Conceptual MindWorks - Conceptual MindWorks'),
                           (73, 'Connexin Software, Inc - Office Practicum'),
                           (74, 'CorrecTek - CorrecTek 2014'),
                           (
                           75, 'CPSI (Computer Programs and Systems), Inc - CPSI (Computer Programs and Systems), Inc'),
                           (76, 'CPSI (Computer Programs and Systems), Inc - CPSI Medical Practice EMR'),
                           (77, 'CPSI (Computer Programs and Systems), Inc - CPSI System'),
                           (78, 'DavLong Business Solutions - DavLong Business Solutions'),
                           (79, 'DavLong Business Solutions - Medinformatix'),
                           (80, 'DocuTap - DocuTap'),
                           (81, 'e-MDs, Inc - e-MDs Cloud Solutions'),
                           (82, 'e-MDs, Inc - e-MDs Solution Series'),
                           (83, 'e-MDs, Inc - e-MDs, Inc'),
                           (84, 'eClinicalWorks LLC - eClinicalWorks'),
                           (85, 'eClinicalWorks LLC - eClinicalWorks LLC'),
                           (86, 'eClinicalWorks LLC - healow'),
                           (87, 'Elation Health - EHR'),
                           (88, 'Elation Health - Elation Health'),
                           (89, 'Elekta - Elekta'),
                           (90, 'Elekta - Mosaiq'),
                           (91, 'Emdeon - Emdeon'),
                           (92, 'Epic Systems Corporation - Beacon Oncology 2014 Certified Module'),
                           (93, 'Epic Systems Corporation - Epic Systems Corporation'),
                           (94, 'Epic Systems Corporation - EpicCare Ambulatory 2014 Certified EHR Suite'),
                           (95, 'Epic Systems Corporation - EpicCare Inpatient 2014 Certified EHR Suite'),
                           (96, 'Epic Systems Corporation - EpicCare Inpatient 2014 Certified EHR Suite (with Beaker)'),
                           (97, 'Epic Systems Corporation - OpTime Surgical 2014 Certified Module'),
                           (98,
                            'Epic Systems Corporation - Outgoing Public Health Reporting from EpicCare Functionality'),
                           (99, 'Evident - Evident'),
                           (100, 'Fox Meadows - IMS'),
                           (101, 'GE Healthcare - Centricity EMR'),
                           (102, 'GE Healthcare - Centricity Enterprise (CE)'),
                           (103, 'GE Healthcare - Centricity Patient Online'),
                           (104, 'GE Healthcare - Centricity Perinatal'),
                           (105, 'GE Healthcare - Centricity Practice Solution'),
                           (106, 'GE Healthcare - Centricity RIS-IC'),
                           (107, 'GE Healthcare - GE Healthcare'),
                           (108, 'GeeseMed - EHR'),
                           (109, 'GeeseMed - GeeseMed'),
                           (110, 'Glenwood Systems LLC - GlaceEMR'),
                           (111, 'Global Health - Global Health'),
                           (112, 'gloStream, Inc - gloSuite'),
                           (113, 'Greenway Health, LLC - Greenway Health, LLC'),
                           (114, 'Greenway Health, LLC - Greenway Intergy Meaningful Use Edition'),
                           (115, 'Greenway Health, LLC - Greenway PrimeSUITE'),
                           (116, 'Greenway Health, LLC - MediaDent using Intergy'),
                           (117, 'Greenway Health, LLC - MediaDent using Success EHS'),
                           (118, 'Greenway Health, LLC - SuccessEHS'),
                           (119, 'Harris Care Tracker - Harris Care Tracker'),
                           (120, 'Harris Healthcare - EHR'),
                           (121, 'HBS - Health Business Systems Inc - HBS - Health Business Systems Inc'),
                           (122, 'Health Care Systems, Inc - Healthcare Management Systems w/ Patient Logic'),
                           (123, 'Health Network Solutions - Health Network Solutions'),
                           (124, 'Healthcare Management Systems, Inc - Healthcare Management Systems'),
                           (125, 'HealthCareXchange - HealthCareXchange'),
                           (126, 'HealthCareXchange - TheVaccinator'),
                           (127, 'HealthFusion - Meditouch'),
                           (128, 'Healthland, Inc - Healthland Centric'),
                           (129, 'Healthland, Inc - Healthland Centriq Clinic'),
                           (130, 'Healthland, Inc - Healthland Clinical Information System'),
                           (131, 'Healthland, Inc - Healthland, Inc'),
                           (132, 'Helix Pharmacy System - Helix Pharmacy System'),
                           (133, 'ICS Software - Sammy EHR'),
                           (134, 'Indian Health Service - Resource and Patient Management System (RPMS)'),
                           (135, 'InSync Healthcare Solutions - InSync'),
                           (136, 'ios Health Systems - Medios'),
                           (137, 'Ipatient Care - Ipatient Care'),
                           (138, 'Iron Bridge Integration - Iron Bridge Integration'),
                           (139, 'Itelagen - EHR'),
                           (140, 'J.M. Smith Corporation - J.M. Smith Corporation'),
                           (141, 'Kroger Health - Kroger Health'),
                           (142, 'Lagniappe Health - Lagniappe Health'),
                           (143, 'Life Point Health - Life Point Health'),
                           (144,
                            'LSS Data Systems - Medical and Practice Management (MPM) 6.0 Continuity of Care (CCD) Interface Suite'),
                           (
                           145, 'LSS Data Systems - Medical and Practice Management (MPM) 6.0 Incorporate Lab Results'),
                           (146,
                            'LSS Data Systems - Medical and Practice Management (MPM) 6.0 Patient and Consumer Health Portal'),
                           (147,
                            'LSS Data Systems - Medical and Practice Management (MPM) 6.0 Transmission to Immunization Registries'),
                           (148,
                            'LSS Data Systems - Medical and Practice Management (MPM) 6.0 Transmission to Public Health Agencies'),
                           (149,
                            'LSS Data Systems - Medical and Practice Management (MPM) Client/Server Continuity of Care (CCD) Interface Suite'),
                           (150,
                            'LSS Data Systems - Medical and Practice Management (MPM) Client/Server Incorporate Lab Results'),
                           (151,
                            'LSS Data Systems - Medical and Practice Management (MPM) Client/Server Patient and Consumer Health Portal'),
                           (152,
                            'LSS Data Systems - Medical and Practice Management (MPM) Client/Server Transmission to Immunization Registries'),
                           (153,
                            'LSS Data Systems - Medical and Practice Management (MPM) Client/Server Transmission to Public Health Agencies'),
                           (154,
                            'LSS Data Systems - Medical and Practice Management (MPM) MAGIC Continuity of Care (CCD) Interface Suite'),
                           (155,
                            'LSS Data Systems - Medical and Practice Management (MPM) MAGIC Patient and Consumer Health Portal'),
                           (156,
                            'LSS Data Systems - Medical and Practice Management (MPM) MAGIC Transmission to Immunization Registries'),
                           (157,
                            'LSS Data Systems - Medical and Practice Management (MPM) MAGIC Transmission to Public Health Agencies'),
                           (158, 'Macpractice - Macpractice'),
                           (159, 'McKesson - Horizon Ambulatory Care'),
                           (160, 'McKesson - Horizon Lab'),
                           (161, 'McKesson - Horizon Medical Imaging'),
                           (162, 'McKesson - InteGreat EHR'),
                           (163, 'McKesson - Lytec MD'),
                           (164, 'McKesson - McKesson'),
                           (165, 'McKesson - McKesson Business Insight'),
                           (166, 'McKesson - McKesson Horizon Clinicals'),
                           (167, 'McKesson - McKesson Lab'),
                           (168,
                            'McKesson - McKesson Patient Folder with McKesson Patient Folder Release of Information module'),
                           (169, 'McKesson - McKesson Practice Choice'),
                           (170, 'McKesson - McKesson Quality eMeasures for Hospitals'),
                           (171, 'McKesson - McKesson Quality eMeasures for Professionals'),
                           (172, 'McKesson - Medisoft Clinical'),
                           (173, 'McKesson - Paragon with McKesson Quality eMeasures'),
                           (174, 'McKesson - Paragon with McKesson Quality eMeasures? for Hospitals'),
                           (175, 'McKesson - Practice Partner'),
                           (176, 'McKesson - Practice Partner with RelayClinical Solutions'),
                           (177, 'McKesson - RelayClinical Solutions'),
                           (178, 'McKesson Specialty Health - iKnowMed EHR'),
                           (179, 'McKesson Specialty Health - iKnowMed Generation 2'),
                           (180, 'McKesson Specialty Health - McKesson Specialty Health'),
                           (181, 'MDI Achieve - Matrix Care'),
                           (182, 'Medhost - EHR'),
                           (183, 'Medhost - Medhost'),
                           (184, 'Medent - Medent Cloud SaaS'),
                           (185, 'Medical Information Technology, Inc - Medical and Practice Management (MPM)'),
                           (186, 'Medical Information Technology, Inc - Medical Information Technology, Inc'),
                           (187, 'Medical Information Technology, Inc - Meditech'),
                           (188, 'Medical Information Technology, Inc - Meditech MAGIC'),
                           (189, 'Medical Micro Systems Inc - Oversite'),
                           (190, 'Medicat - Medicat'),
                           (191, 'MedInformatix, Inc - MedInformatix Complete EHR'),
                           (192, 'Meditab Software, Inc - IMS'),
                           (193, 'Mednetworkx - Mednetworkx'),
                           (194, 'MedShpere - MedShpere'),
                           (195, 'ModernizingMedicine (gMed) - gGastro'),
                           (196, 'ModuleMD - ModuleMD WISE'),
                           (197, 'Nemours - NemoursOne'),
                           (198, 'Net Health - AgilityWP'),
                           (199, 'Net Health - Net Health'),
                           (200, 'Netsmart - EHR'),
                           (201, 'Netsmart - Netsmart'),
                           (202, 'New Tech Medical - New Tech Medical'),
                           (203, 'NextGen Healthcare - NextGen Ambulatory EHR'),
                           (204, 'NextGen Healthcare - NextGen EDR'),
                           (205, 'NextGen Healthcare - NextGen Emergency Department Solution'),
                           (206, 'NextGen Healthcare - NextGen Healthcare'),
                           (207, 'NextGen Healthcare - NextGen Inpatient Clinicals'),
                           (208, 'NextGen Healthcare - NextGen Patient Portal'),
                           (209, 'NextGen Healthcare - SCHIEx'),
                           (210, 'OA Systems Healthcare - Panacea EHR'),
                           (211, 'OCHIN - OCHIN'),
                           (212, 'Office Ally - Office Ally'),
                           (213, 'Optimal Revenue Management Services, Inc - Optimal Revenue Management Services, Inc'),
                           (214, 'Optum - Optum'),
                           (215, 'Palmetto GBA - Palmetto GBA'),
                           (216, 'PassageWare - Passport Health'),
                           (217, 'Patagonia Health - Patagonia Health EHR'),
                           # (218, 'PC Ace Pro32'),  -- DUPLICATE OF "CGS - PC-ACE Pro32"
                           (219, 'PDX - Pharmacy Software'),
                           (220, 'Physicians Computer Company - PCC EHR'),
                           (221, 'Pioneer RX - Pioneer RX'),
                           (222, 'Point and Click - Point and Click Solutions'),
                           (223, 'Practice Fusion - Practice Fusion EHR'),
                           (224, 'Practice Velocity - EMR'),
                           (225, 'PracticeSuite - EHR'),
                           (226, 'Prescribewellness - Script Manage Print (SMP)'),
                           (227, 'Public Consulting Group (PCG) - EdPlan'),
                           (228, 'Pulse Systems, Inc - Pulse Complete EHR'),
                           (229, 'QRS Inc - Paradigm'),
                           (230, 'QS/1 - QS/1'),
                           (231, 'Quest Diagnostics - Quest Diagnostics'),
                           (232, 'Quickmar - CareSuite'),
                           (233,
                            'RPMS - Resource and Patient Management System - RPMS - Resource and Patient Management System'),
                           (234, 'RxNT - RxNT EHR'),
                           (235, 'Scientific Technologies Corporation - ImmsLink'),
                           (236, 'Script Management Partners - ImSRV'),
                           (237, 'Sevocity - Sevocity'),
                           (238, 'Sevocity Software - EHR'),
                           (239, 'Siemens Medical Solutions USA Inc - MedSeries4 Clinical Suite Inpatient'),
                           (240, 'Siemens Medical Solutions USA Inc - MobileMD Clinical Portal'),
                           (241, 'Siemens Medical Solutions USA Inc - MobileMD Patient Portal'),
                           (242, 'Siemens Medical Solutions USA Inc - Siemens Analytics'),
                           (243, 'Siemens Medical Solutions USA Inc - Siemens NOVIUS Lab'),
                           (244, 'Siemens Medical Solutions USA Inc - Soarian Clinicals Ambulatory'),
                           (245, 'Siemens Medical Solutions USA Inc - Soarian Clinicals Inpatient'),
                           (246, 'Siemens Medical Solutions USA Inc - Soarian EDM'),
                           (247, 'Siemens Medical Solutions USA Inc - syngo Dynamics'),
                           (248, 'SOAPware, Inc - SOAPware'),
                           (249, 'Sure Scripts - Sure Scripts'),
                           (250, 'Systemedx Inc - Systemedx Clinical Navigator'),
                           (251, 'Transact RX - Transact RX'),
                           (252, 'Transaction Data - RX30'),
                           (253, 'UL - Systoc'),
                           (254, 'Ulrich Medical Concepts - TCC 2014'),
                           (255, 'Ulrich Medical Concepts - Team Chart Concept'),
                           (256, 'Ulrich Medical Concepts - Ulrich Medical Concepts'),
                           (257, 'Varian - Aria'),
                           (258, 'Vaxcare - VaxHub'),
                           (259, 'WellMed - WellMed'),
                           (260, 'Xchange Technology Group - Xchange Technology Group'),
                           # Hawaii EHRs
                           (261, 'Alliance of Chicago'),
                           (262, 'Athena Health'),
                           (263, 'Cerner Corporation - ALL Hub'),
                           (264, 'Cerner Corporation - Hub'),
                           (265, 'Costco Pharmacy Hub - PrescribeWellness'), #disabled
                           (266, 'CVS/Pharmacy - STC'),
                           (267, 'eClinicalWorks - Hub'),
                           (268, 'Flatiron Health - Parent'),
                           (269, 'Hawaii Health Systems Corp'),
                           (270, 'Hawaii Pacific Health'),
                           (271, 'HCNetwork Parent'),
                           (272, 'HICHC Parent'),
                           (273, 'Iron Bridge - Hub'),
                           (274, 'Kaiser Permanente'),
                           (275, 'Kokua Kalihi Valley - Parent'),
                           (276, 'Maui Health Systems - Hub'),
                           (277, 'Medical Informatics Engineering, Inc.'),
                           (278, 'Medical Transcription Billing Corp - MTBC'),
                           (279, 'Netsmart Technologies'),
                           (280, 'Physicians Computer Company'),
                           (281, 'Point and Click Solutions, Inc.'),
                           (282, 'Outcomes'),  # Replaced PrescribeWellness - Hub
                           (283, "Queen's Health System"),
                           (284, 'Safeway - STC'),
                           (285, 'STC Health - Hub'),
                           (286, 'Waianae Coast Comp HC Hub'),
                           (287, 'Waimanalo Health Center Hub'),
                           (288, "Wal-Mart and Sam's Club Pharmacy - STC"),
                           (289, 'Walgreens - STC')]

        ehr_vendor_dict = {}
        for t in ehr_vendor_list:
            ehr_vendor_dict[t[1]] = t[0]

        self.df_clinics.rename(columns={'ehr_vendor': 'ehr_vendor_product_id'}, inplace=True)

        # Replace ochin with matching name in envision list
        results =self.df_clinics[self.df_clinics['ehr_vendor_product_id'] == 'OCHIN']
        #print(results)
        # Renaming OCHIN to 'OCHIN - OCHIN' to match with what is stored in envision DB
        for i in results.index:
            #print(i)
            self.df_clinics.loc[i,'ehr_vendor_product_id'] = 'OCHIN - OCHIN'

        # Assign STC Health - Hub as hl7 sender for Frank Baum (4384)
        results = self.df_clinics[self.df_clinics['clinic_unique_id'] == '4384']
        self.df_clinics.loc[results.index[0],'ehr_vendor_product_id'] = 'STC Health - Hub'

        somelist = []
        for vendor in self.df_clinics.loc[:, 'ehr_vendor_product_id']:
            try:
                somelist.append(ehr_vendor_dict[vendor])
            except:
                somelist.append('')

        self.df_clinics.loc[:, 'ehr_vendor_product_id'] = somelist
        print('ehr vendor product id mapped')

    # Obtain webiz provider for each clinic
    def get_provider_id(self):
        # This files associates providers with clinics
        webiz_providers = pd.read_csv('../webiz_child.csv', na_filter=False)

        print("Number of provider-clinic pairs",len(webiz_providers))

        # Map clinic id to provider id
        mapper = {}
        for i in range(len(webiz_providers)):
            # get child org id
            key = str(webiz_providers.loc[i,'LEGACY CLINIC ID'])
            # Assign the webiz provider(parent)
            mapper[key] = str(webiz_providers.loc[i, 'WebIZ Provider ID'])

        # In[221]:

        # drop 12464
        # drop 4348
        # drop 9642 (all disabled hl7 senders)
        drop_list=['4348','9642','12464','4040','4217','9221','7820','7681','8561']
        print("Dropping",drop_list)
        for org in drop_list:
            results=self.df_clinics[self.df_clinics['clinic_unique_id'] == org]
            print(results)
            for i in results.index:
                self.df_clinics.drop(i,axis=0,inplace=True)

        self.df_clinics.reset_index(drop=True, inplace=True)

        # Add the provider unique id to df_clinics
        self.df_clinics.loc[:, 'provider_unique_id'] = [mapper[clinic_id] for clinic_id in self.df_clinics.loc[:, 'clinic_unique_id']]

        print("Provider id mapped, num of clinics",len(self.df_clinics))

        #print('empty physical address', self.df_clinics[self.df_clinics['physical_address_line1'] == ''])
        #print('empty mailing address', self.df_clinics[self.df_clinics['mailing_address_line1'] == ''])
        # Some mailing addresses (5) were empty 6/2/2025
        empty_street = self.df_clinics[self.df_clinics['mailing_address_line1'] == '']
        for idx in empty_street.index:
            self.df_clinics.loc[idx,'mailing_address_line1'] = self.df_clinics.loc[idx,'physical_address_line1']
        print('empty mailing address?', self.df_clinics[self.df_clinics['mailing_address_line1'] == ''])

    # Get region based on county info
    def get_region_id(self):
        # Region mapping based on county for now
        '''
        1	Hawaii
        2	Oahu
        3	Maui
        4	Kauai
        5	Molokai
        6	Lanai
        7   Other
        '''
        counties = self.df_clinics.loc[:, 'mailing_address_county']
        regions = []
        for i in range(len(counties)):
            if counties[i] == 'Hawaii':
                regions.append(1)
            elif counties[i] == 'Honolulu':
                regions.append(2)
            elif counties[i] == 'Maui':
                regions.append(3)
            elif counties[i] == 'Kauai':
                regions.append(4)
            else:
                regions.append(7)

        self.df_clinics.loc[:, 'region_id'] = regions
        print("Region ids mapped")



    # Build csv
    def build_csv(self):
        # Dump df_clinics to csv
        self.df_clinics.to_csv('db_files/clinics_bulk_insert.csv',index=False)

        # Create a csv file again for building other containers
        self.df_clinics.to_csv('../clinics/clinics_in_container.csv', index=False)

        print('Completed building',len(self.df_clinics),'clinics')
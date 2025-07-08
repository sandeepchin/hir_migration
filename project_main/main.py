
#  Copyright (c) 2025. Sandeep Chintabathina

# Main program code to build various containers

from provider import Provider
from clinic import Clinic
from users import Users
from clinic_notes import Clinic_Notes
from patients import Patient
from vaccinations import Vaccinations
from schools import Schools

def main():
    
    p =  Provider()
    p.get_provider_type_of_practice()
    p.get_category_code()
    p.get_practice_code()
    p.build_csv()


    c= Clinic()
    c.get_practice_code()
    c.get_contact_num()
    c.get_secondary_contact()
    c.get_site_admin()
    c.get_tech_contact()
    c.add_pseudo_clinic()
    c.get_sends_hl7_messages()
    c.get_ehr_vendor_product_id()
    c.get_provider_id()
    c.get_region_id()
    c.build_csv()


    u = Users()
    u.get_security_profile()
    u.prepare_user_clinics()
    u.build_users_csv()
    u.build_user_clinics_csv()
    u.prepare_hl7_users_clinics()
    u.build_hl7_users_clinics_csv()

    c = Clinic_Notes()
    c.build_clinic_notes_csv()

    p = Patient()
    p.get_patient_insurance()
    p.get_patient_contacts()
    p.get_patient_allergy_risks()
    
    v = Vaccinations()
    v.get_vaccine_adverse_reactions()

    s = Schools()

if __name__=='__main__':
    main()

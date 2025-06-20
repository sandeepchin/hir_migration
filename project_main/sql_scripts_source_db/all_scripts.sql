

SET SQLFORMAT csv
--set loadformat enclosures off
set feedback off
--set markup csv on quote off

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\parent_child_orgs_list_with_addresses.csv";
     
/* Extract parent-child relationship from org_children and provider_organization tables*/
/* Used for container */
/* parent_child_orgs_list_with_addresses.csv */

select po.provider_organization_id as legacy_parent_org_id,
        po.name as hl7_sender, 
        --lk.description as legacy_org_type,
        '' as "WebIZ_Provider",
        '' as "WebIZ_Provider_Street_Address",
        '' as "WebIZ_Provider_City",
        '' as "WebIZ_Provider_County",
        '' as "WebIZ_Provider_Zip",
        --'' as "WebIZ_Provider_Category_Code",
        lk.description as "WebIZ_Provider_Category_Code",  --Trial instead of getting data from static file
        '' as "WebIZ_Provider_Type_of_Practice",
        ch.child_organization_id as legacy_clinic_id,
        po1.name as "WebIZ_Clinic",
        po1.active_yn as active,
        ad.street_address_line ||' '|| ad.other_address_line as "WebIZ_Clinic_Street_Address",
        ad.city_name as "WebIZ_Clinic_City",
        get_county(ad.zip_code) as "WebIZ_Clinic_County",
        ad.zip_code as "WebIZ_Clinic_Zip",
        lk.description as "WebIZ_Clinic_Category_Code",
        lk1.description as "WebIZ_Clinic_Provider_Type_of_Practice"
    from 
        prd_irowner.org_children ch join PRD_IROWNER.provider_organization po
        on ch.master_organization_id= po.provider_organization_id
        join PRD_IROWNER.provider_organization po1
        on ch.child_organization_id = po1.provider_organization_id
        left join prd_irowner.address ad
        on po1.address_id = ad.address_id
        join prd_irowner.lookup lk 
        on po1.organization_type = lk.lookup_value
        left join prd_irowner.org_state_vaccine_profile os
        on os.provider_organization_id = po1.provider_organization_id
        left join prd_irowner.lookup lk1
        on os.provider_type_code = lk1.lookup_value
    where
        lk.lookup_type_name='ORGTYPE' 
        /* remove orgs that are inactive and have no vaccinations */
        and po1.provider_organization_id not in 
            ( select po2.provider_organization_id 
                from prd_irowner.provider_organization po2
                join prd_irowner.org_children ch1
                on po2.provider_organization_id=ch1.child_organization_id
                where ch1.child_organization_id not in 
                (select im.entered_by_org_id from prd_irowner.immunizations im
                group by im.entered_by_org_id)
                and po2.active_yn='N'
            )
    order by po.provider_organization_id,ch.child_organization_id;
    
spool off;  


spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\stand_alone_orgs_with_addresses.csv";
/* Script to get stand alone orgs(not a parent or child) from HIR*/
/* stand_alone_orgs_with_addresses.xlsx*/

select '' as "WebIZ_Provider",
        '' as "WebIZ_Provider_Street_Address",
        '' as "WebIZ_Provider_City",
        '' as "WebIZ_Provider_County",
        '' as "WebIZ_Provider_Zip",
        --'' as "WebIZ_Provider_Category_Code",
        lk.description as "WebIZ_Provider_Category_Code",   --Trial instead of getting data from static file
        '' as "WebIZ_Provider_Type_of_Practice",
        po.provider_organization_id as legacy_clinic_id,
        po.name as "WebIZ_Clinic",
        po.active_yn as active,
        ad.street_address_line ||' '|| ad.other_address_line as "WebIZ_Clinic_Street_Address",
        ad.city_name as "WebIZ_Clinic_City",
        get_county(ad.zip_code) as "WebIZ_Clinic_County",
        ad.zip_code as "WebIZ_Clinic_Zip",
        --po.organization_type as "WebIZ_Clinic_Category_Code",
        lk.description as "WebIZ_Clinic_Category_Code",
        lk1.description as "WebIZ_Clinic_Provider_Type_of_Practice"
    from 
        prd_irowner.provider_organization po
        left join prd_irowner.address ad
        on po.address_id = ad.address_id
        join prd_irowner.lookup lk    
        on po.organization_type = lk.lookup_value
        left join prd_irowner.org_state_vaccine_profile os
        on os.provider_organization_id = po.provider_organization_id
        left join prd_irowner.lookup lk1
        on os.provider_type_code = lk1.lookup_value
    where 
       /* orgs not listed as children or parents*/
        lk.lookup_type_name='ORGTYPE' and
        po.provider_organization_id not in 
        (select ch.child_organization_id from prd_irowner.org_children ch)
        and po.provider_organization_id not in 
        (select ch1.master_organization_id from prd_irowner.org_children ch1
            group by ch1.master_organization_id)
        /* weed out ones that do not have any vaccinations*/
        and po.provider_organization_id not in
        (select po1.provider_organization_id
            from prd_irowner.provider_organization po1
                where po1.provider_organization_id not in 
                (select ch2.child_organization_id from prd_irowner.org_children ch2)
                and po1.provider_organization_id not in 
                (select ch3.master_organization_id from prd_irowner.org_children ch3
                     group by ch3.master_organization_id)
                and po1.provider_organization_id not in 
                (select im.entered_by_org_id from prd_irowner.immunizations im
                     group by im.entered_by_org_id)
                and po1.active_yn='N'
            )
        --and po.provider_organization_id > 0
    order by po.provider_organization_id;
    
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\clinics_data.csv";
/* Build clinic query incrementally */
/* clinics_data.xlsx */
select distinct po.name as clinic_desc,
        '' as clinic_code,
        case when po.active_yn='Y' then 'A'
         when po.active_yn='N' then 'I' 
         else '' end as status_code,
        lk1.description as provider_type_of_practice_code_id,
        trim(org_con.first_name||' '||org_con.last_name) as physician_name,
        
        sub1.mailing_address_line1 as mailing_address_line1,
        sub1.mailing_address_line2 as mailing_address_line2,
        sub1.mailing_address_city as mailing_address_city,
        sub1.mailing_address_county as mailing_address_county,
        sub1.mailing_address_state as mailing_address_state,
        sub1.mailing_address_zip as mailing_address_zip,
        
        sub2.physical_address_line1 as physical_address_line1,
        sub2.physical_address_line2 as physical_address_line2,
        sub2.physical_address_city as physical_address_city,
        sub2.physical_address_county as physical_address_county,
        sub2.physical_address_state as physical_address_state,
        sub2.physical_address_zip as physical_address_zip,
        
        po.vfc_pin as vfc_pin,
        '' as sends_hl7_messages,
        '' as hl7_sending_clinic_unique_id,
        ch.child_organization_id as hl7_facility_code,
        po1.name as ehr_vendor,
        po.provider_organization_id as clinic_unique_id,
        case when po.vfc_pin is not null then 3 
            else 1 end as inventory_tracking_type,
        case when po.vfc_pin is not null then 1
            else 0 end as funding_source_vfc,
        case when po.vfc_pin is not null then 1
            else 0 end as funding_source_state,
        0 as funding_source_private,
        case when po.vfc_pin is not null then 1
            else 0 end as funding_source_317,
        0 as funding_source_chip,
        0 as funding_source_pandemic,
        5 as clinic_legacy_data_status,
        case when ch.child_organization_id is not null then 10
            else 12 end as clinic_onboarding_statuses
    from 
        prd_irowner.provider_organization po
        left join prd_irowner.org_state_vaccine_profile os
        on os.provider_organization_id = po.provider_organization_id
        left join prd_irowner.lookup lk1
        on os.provider_type_code = lk1.lookup_value
        left join prd_irowner.org_contact org_con
        on po.provider_organization_id=org_con.provider_organization_id
        and org_con.contact_type_code in ('Z2')  -- physician type
        
        left join( select org_con1.provider_organization_id as provider_organization_id,
                        max(ad1.street_address_line ||' '|| ad1.other_address_line) as mailing_address_line1,
                        max(case when ad1.po_box_route_line is not null then 'PO Box '||replace(replace(ad1.po_box_route_line,'"',''),',','') else '' end) as mailing_address_line2,
                        max(ad1.city_name) as mailing_address_city,
                        get_county(max(ad1.zip_code)) as mailing_address_county,
                        max(ad1.state_code) as mailing_address_state,
                        max(ad1.zip_code) as mailing_address_zip
                    from
                        prd_irowner.org_contact org_con1 left join prd_irowner.address ad1
                        on org_con1.address_id =ad1.address_id and ad1.address_type='M'  -- mailing address
                    group by org_con1.provider_organization_id
                    ) sub1 on po.provider_organization_id=sub1.provider_organization_id
        
        left join( select org_con2.provider_organization_id as provider_organization_id,
                        max(ad2.street_address_line ||' '|| ad2.other_address_line) as physical_address_line1,
                        max(case when ad2.po_box_route_line is not null then 'PO Box '||replace(replace(ad2.po_box_route_line,'"',''),',','') else '' end) as physical_address_line2,
                        max(ad2.city_name) as physical_address_city,
                        get_county(max(ad2.zip_code)) as physical_address_county,
                        max(ad2.state_code) as physical_address_state,
                        max(ad2.zip_code) as physical_address_zip
                    from
                        prd_irowner.org_contact org_con2 left join prd_irowner.address ad2
                        on org_con2.address_id = ad2.address_id and ad2.address_type='S'  -- shipping address
                    group by org_con2.provider_organization_id
                    ) sub2 on po.provider_organization_id=sub2.provider_organization_id

        left join prd_irowner.org_children ch
        on po.provider_organization_id=ch.child_organization_id
        and po.active_yn='Y'
        left join prd_irowner.provider_organization po1
        on ch.master_organization_id = po1.provider_organization_id
    where
        --Not any orgs that are inactive and vaccine-less
        po.provider_organization_id not in
        (
            select po1.provider_organization_id from 
                prd_irowner.provider_organization po1
            where 
                po1.provider_organization_id not in 
                (select im.entered_by_org_id from prd_irowner.immunizations im
                     group by im.entered_by_org_id)
                and po1.active_yn='N' 
          ) and --not a master org
          po.provider_organization_id not in
          (
            select org_c.master_organization_id from prd_irowner.org_children org_c
                     group by org_c.master_organization_id
          )
          ;

spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\clinic_contact_number.csv";
/* Get primary phone number via HIRPrimary Contact (more complete than VACOrdering Primary)*/
/* Get the fax number also via HIRPrimary Contact */
/* clinic_contact_number.xlsx */
select po.name as clinic_desc,
        case when ph.phone_number is not null then
            case when ph.area_code is not null then  
                case when ph.extension is not null then 
                    ph.area_code||'-'||ph.phone_number||'x'||ph.extension 
                else 
                    ph.area_code||'-'||ph.phone_number 
                end
            else  
                (case when ph.extension is not null then 
                    '808-'||ph.phone_number||'x'||ph.extension 
                else 
                   '808-'||ph.phone_number 
                end)
            end
        else '' end as contact_primary_phone_number,
        case when ph1.phone_number is not null then 
            case when ph1.area_code is not null then 
                ph1.area_code||'-'||ph1.phone_number
            else
                '808-'||ph1.phone_number
            end
        else '' end as contact_fax_number
    from
        prd_irowner.provider_organization po
        left join prd_irowner.org_contact org_con
        on po.provider_organization_id=org_con.provider_organization_id
        and org_con.position_code = 'HIRPC'
        left join PRD_IROWNER.phone_number ph
        on org_con.phone_id = ph.phone_number_id
        left join prd_irowner.phone_number ph1
        on org_con.facsimile_id = ph1.phone_number_id
     where
        --Not any orgs that are inactive and vaccine-less
        po.provider_organization_id not in
        (
            select po1.provider_organization_id from 
                prd_irowner.provider_organization po1
            where 
                po1.provider_organization_id not in 
                (select im.entered_by_org_id from prd_irowner.immunizations im
                     group by im.entered_by_org_id)
                and po1.active_yn='N' 
          ) and --not a master org
          po.provider_organization_id not in
          (
            select org_c.master_organization_id from prd_irowner.org_children org_c
                     group by org_c.master_organization_id
          );

spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\clinic_secondary_contact.csv";
/* Get secondary phone number via VACOrderingSecondary - more values filled than HIRSC*/
/* clinic_secondary_contact.xlsx*/
select po.name as clinic_desc,
        case when ph.phone_number is not null then
            case when ph.area_code is not null then  
                case when ph.extension is not null then 
                    ph.area_code||'-'||ph.phone_number||'x'||ph.extension 
                else 
                    ph.area_code||'-'||ph.phone_number 
                end
            else  
                (case when ph.extension is not null then 
                    '808-'||ph.phone_number||'x'||ph.extension 
                else 
                   '808-'||ph.phone_number 
                end)
            end
        else '' end as contact_secondary_phone_number
    from
        prd_irowner.provider_organization po
        left join prd_irowner.org_contact org_con
        on po.provider_organization_id=org_con.provider_organization_id
        and org_con.position_code = 'VACOS'
        left join PRD_IROWNER.phone_number ph
        on org_con.phone_id = ph.phone_number_id
     where
        --Not any orgs that are inactive and vaccine-less
        po.provider_organization_id not in
        (
            select po1.provider_organization_id from 
                prd_irowner.provider_organization po1
            where 
                po1.provider_organization_id not in 
                (select im.entered_by_org_id from prd_irowner.immunizations im
                     group by im.entered_by_org_id)
                and po1.active_yn='N' 
          ) and --not a master org
          po.provider_organization_id not in
          (
            select org_c.master_organization_id from prd_irowner.org_children org_c
                     group by org_c.master_organization_id
          );

spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\clinic_site_admin.csv";
/* Get site admin info via HIRPrimaryContact */
/* clinic_site_admin.xlsx */
select po.name as clinic_desc,
        org_con.first_name||' '||org_con.last_name as site_administrator_name,
        'HIR Primary Contact' as site_administrator_title,
        ad.email_address as site_administrator_email_address,
        case when ph.phone_number is not null then
            case when ph.area_code is not null then  
                case when ph.extension is not null then 
                    ph.area_code||'-'||ph.phone_number||'x'||ph.extension 
                else 
                    ph.area_code||'-'||ph.phone_number 
                end
            else  
                (case when ph.extension is not null then 
                    '808-'||ph.phone_number||'x'||ph.extension 
                else 
                   '808-'||ph.phone_number 
                end)
            end
        else '' end as site_administrator_phone_number,
        case when ph1.phone_number is not null then 
            case when ph1.area_code is not null then 
                ph1.area_code||'-'||ph1.phone_number
            else
                '808-'||ph1.phone_number
            end
        else '' end as site_administrator_fax_number
    from
        prd_irowner.provider_organization po
        left join prd_irowner.org_contact org_con
        on po.provider_organization_id=org_con.provider_organization_id
        and org_con.position_code = 'HIRPC'
        left join PRD_IROWNER.phone_number ph
        on org_con.phone_id = ph.phone_number_id
        left join prd_irowner.phone_number ph1
        on org_con.facsimile_id = ph1.phone_number_id 
        left join prd_irowner.address ad
        on org_con.address_id = ad.address_id
     where
        --Not any orgs that are inactive and vaccine-less
        po.provider_organization_id not in
        (
            select po1.provider_organization_id from 
                prd_irowner.provider_organization po1
            where 
                po1.provider_organization_id not in 
                (select im.entered_by_org_id from prd_irowner.immunizations im
                     group by im.entered_by_org_id)
                and po1.active_yn='N' 
          ) and --not a master org
          po.provider_organization_id not in
          (
            select org_c.master_organization_id from prd_irowner.org_children org_c
                     group by org_c.master_organization_id
          );
          
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\clinic_tech_contact.csv";
/* Get tech contact info via VACcineOrderingPrimary */
/* clinic_tech_contact.xlsx */
select po.name as clinic_desc,
        org_con.first_name||' '||org_con.last_name as tech_contact_name,
        'Vaccine Ordering Primary' as tech_contact_title,
        ad.email_address as tech_contact_email_address,
        case when ph.phone_number is not null then
            case when ph.area_code is not null then  
                case when ph.extension is not null then 
                    ph.area_code||'-'||ph.phone_number||'x'||ph.extension 
                else 
                    ph.area_code||'-'||ph.phone_number 
                end
            else  
                (case when ph.extension is not null then 
                    '808-'||ph.phone_number||'x'||ph.extension 
                else 
                   '808-'||ph.phone_number 
                end)
            end
        else '' end as tech_contact_phone_number,
        case when ph1.phone_number is not null then 
            case when ph1.area_code is not null then 
                ph1.area_code||'-'||ph1.phone_number
            else
                '808-'||ph1.phone_number
            end
        else '' end as tech_contact_fax_number
    from
        prd_irowner.provider_organization po
        left join prd_irowner.org_contact org_con
        on po.provider_organization_id=org_con.provider_organization_id
        and org_con.position_code = 'VACOP'
        left join PRD_IROWNER.phone_number ph
        on org_con.phone_id = ph.phone_number_id
        left join prd_irowner.phone_number ph1
        on org_con.facsimile_id = ph1.phone_number_id 
        left join prd_irowner.address ad
        on org_con.address_id = ad.address_id
     where
        --Not any orgs that are inactive and vaccine-less
        po.provider_organization_id not in
        (
            select po1.provider_organization_id from 
                prd_irowner.provider_organization po1
            where 
                po1.provider_organization_id not in 
                (select im.entered_by_org_id from prd_irowner.immunizations im
                     group by im.entered_by_org_id)
                and po1.active_yn='N' 
          ) and --not a master org
          po.provider_organization_id not in
          (
            select org_c.master_organization_id from prd_irowner.org_children org_c
                     group by org_c.master_organization_id
          );
          
spool off;

/*
spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\users.csv";
-- Queries to get user data
-- Tables of interest
-- ptl_users, ptl_app_user_links, provider_organization
-- ptl_status contains meaning of status IDs used in ptl_users
-- join with ptl_app_user_links so that we only get user associated with a clinic
-- Only get users associated with active clinics (hl7 and non hl7) (reduced from 3K to 1.4K)
-- users.xlsx

select  users.user_id as other_user_identifier,
        case when users.status_id=1 then 'A'
            else 'I' end as status_code,
        users.username as username,
        '' as npi,
        users.first_name as first_name,
        users.middle_initial as middle_name,
        users.last_name as last_name,
        '' as title_code_id,
        replace(ad.email_address,',','') as primary_email_address,
        '' as secondary_email_address,
        '' as phone_number,
        '' as alt_phone_number1,
        '' as alt_phone_number2,
        '' as alt_phone_number3,
        ad.street_address_line as address_line1,
        ad.other_address_line as address_line2,
        ad.city_name as address_city,
        get_county(ad.zip_code) as address_county,
        ad.state_code as address_state,
        ad.zip_code as address_zip,
        '' as security_profile_id,
        '' as clinic_unique_id, -- Going to keep this blank and list clinic-user association in other tables
        'N' as prescribes,
        'N' as administers,
        0 as hepb_flag,
        '' as comments
    from
        prd_irowner.ptl_users users
        join 
        (  -- from ptl_app_user_links pick users active with respect to at least one org making sure org is active too
            select linker.user_id as user_id
            from
                prd_irowner.ptl_app_user_links linker join prd_irowner.provider_organization po
                on linker.org_id = po.provider_organization_id
                where po.active_yn='Y' and
                po.provider_organization_id not in  -- make sure none of the orgs are hl7 senders 
                ( 
                    select oc.master_organization_id from prd_irowner.org_children oc
                    group by oc.master_organization_id
                )
                group by user_id
                having min(linker.status_id)=1 -- atleast one org in the group is active
        )sub
        on users.user_id = sub.user_id
        left join prd_irowner.address ad  -- always left join with address
        on users.address_id=ad.address_id
    order by users.username;
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\user_clinics.csv";
--user_clinics
-- query to get clinics associated with each user
-- Make sure only active clinics are retrieved and users are active wrt that clinic  - reduced from 6K to 1.4K
-- user_clinics.xlsx

select distinct linker.user_id as other_user_identifier,
        linker.org_id as clinic_unique_id,
        case when po.vfc_pin is not null then 'Y'
            else 'N' end as manage_vaccine_orders_returns
    from 
        prd_irowner.ptl_app_user_links linker
        join prd_irowner.provider_organization po
        on linker.org_id = po.provider_organization_id
    where 
        linker.status_id=1 and  -- make sure user is active wrt org
        po.active_yn='Y' and    -- make sure org is active
        po.provider_organization_id not in  -- make sure none of the orgs are hl7 senders
        ( select oc.master_organization_id from prd_irowner.org_children oc
            group by oc.master_organization_id
        ) 
        ;

spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\user_clinics_vfc_hl7.csv";
-- Query to list all clinics, their users, their vtrcks pic, and if they send hl7
-- This is needed to determine security profile id 
-- user_clinics_vfc_hl7.xlsx

select distinct linker.user_id as other_user_identifier,
        linker.org_id as clinic_unique_id,
        po.vfc_pin as vtrcks_pin,
        case when oc.master_organization_id is null then 'N'
            else 'Y' end as hl7_sender,
        case 
            when roles.role_display_name in ('Insurer','Patient Look-Up') then 11
            when po.vfc_pin is not null and oc.master_organization_id is not null then 7
            when po.vfc_pin is not null and oc.master_organization_id is null then 6
            when po.vfc_pin is null and oc.master_organization_id is not null then 9
            when po.vfc_pin is null and oc.master_organization_id is null then 8
            else null end as security_profile_id
    from
        prd_irowner.ptl_app_user_links linker
        join prd_irowner.provider_organization po
        on linker.org_id=po.provider_organization_id
        left join prd_irowner.org_children oc
        on po.provider_organization_id= oc.child_organization_id
        join prd_irowner.ptl_app_roles roles
        on linker.role_id = roles.role_id
    where 
        linker.status_id=1 and  -- make sure user is active wrt org
        po.active_yn='Y' and    -- make sure org is active
        po.provider_organization_id not in  -- make sure none of the orgs are hl7 senders
        ( select oc1.master_organization_id from prd_irowner.org_children oc1
            group by oc1.master_organization_id
        )
        ;
        
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\hl7senders_and_clinics.csv";
-- Query to get the hl7 senders and their associated clinics 
--hl7senders_and_clinics.xlsx  -- ONLY active reduces count from 610 to 449

select po.name as hl7_sender,
        oc.child_organization_id as clinic_unique_id
    from
        prd_irowner.org_children oc join PRD_IROWNER.provider_organization po
        on oc.master_organization_id= po.provider_organization_id
        join PRD_IROWNER.provider_organization po1
        on oc.child_organization_id = po1.provider_organization_id
    where
        po1.active_yn='Y';  -- Just bring in active orgs. Inactive orgs (even ones with vaccines) don't need users
spool off;

*/
spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\clinic_notes.csv";
/* Sql code to retrieve all types of clinic notes for providers */
/* Mainly two types of notes in HIR - SystemInfo and VacProfile */
/* SystemInfo contains general comments about enrollment
    VacProfile contains comments for VFC portion if provider is a VFC provider*/
/* clinic_notes.csv */  
-- CR = carriage return
-- LF = line feed

select --poc.comment_id as note_id,  --removing note_id 3/31
        poc.provider_organization_id as clinic_unique_id,
        -- Remove , and CR and LF.  CR is chr(13) and LF is chr(10) in oracle. Windows uses both and unix uses just LF
        replace(replace(poc.comment_txt,',',''),chr(13)||chr(10),'') as note_text,
        poc.comment_type as common_category_id,
        to_char(to_date(poc.create_date,'DD-MON-YY'),'YYYY-MM-DD') as audit_created_date
    from
        prd_irowner.provider_organization_comment poc
    where poc.provider_organization_id not in
        (  --disregard inactive orgs without vaccinations
            select po1.provider_organization_id from 
                prd_irowner.provider_organization po1
            where 
                po1.provider_organization_id not in 
                (select im.entered_by_org_id from prd_irowner.immunizations im
                     group by im.entered_by_org_id)
                and po1.active_yn='N' 
          ) and --not a master org
          poc.provider_organization_id not in
          (
            select oc.master_organization_id from prd_irowner.org_children oc
                     group by oc.master_organization_id
          )
        order by poc.provider_organization_id;
        
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\patient_race_list.csv";
-- Starting with retrieving race data for each patient  - excluding h1n1 patients
-- patient_race_list.csv file 

select c.client_id as other_patient_identifier,
        --listagg(ROWNUM,',') as race_order, -- this gives row order of result set. SQL does not store track insertion order by row number
        listagg(cr.race_code,'|') as race_list
    from
        prd_irowner.clients c join prd_irowner.client_race cr
        on c.client_id = cr.client_id
    where c.client_id not in (
        select distinct sub.client_id from (
        SELECT imm.client_id as client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id 
        FROM prd_irowner.immunizations imm
        JOIN prd_irowner.clients cl ON cl.client_id = imm.client_id
        WHERE imm.vaccination_date >= TO_DATE('01-JAN-2009', 'DD-MON-YYYY')
          AND cl.consent_ind = 'N'
        GROUP BY imm.client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id
        HAVING COUNT(DISTINCT imm.vaccine_id) = 1
           AND imm.vaccine_id IN (
           SELECT vaccine_id 
           FROM prd_irowner.vaccine_group_children 
           WHERE vaccine_group_id = 1131 )
        )sub
    )
    group by c.client_id
    ;
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\patient_funding_program_code.csv";
/* Managing to get most recent VFC eligibility for a client - patient_funding_program_code.csv file */ 

select cf.client_id,cf.funding_program_code from
    ( select client_id,
            max(screen_date) as max_screen_date
        from 
            prd_irowner.client_funding_program
    group by client_id) sub
    join prd_irowner.client_funding_program cf
    on sub.max_screen_date=cf.screen_date
    and sub.client_id = cf.client_id
    where cf.client_id not in (
        select distinct sub2.client_id from (
        SELECT imm.client_id as client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id 
        FROM prd_irowner.immunizations imm
        JOIN prd_irowner.clients cl ON cl.client_id = imm.client_id
        WHERE imm.vaccination_date >= TO_DATE('01-JAN-2009', 'DD-MON-YYYY')
          AND cl.consent_ind = 'N'
        GROUP BY imm.client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id
        HAVING COUNT(DISTINCT imm.vaccine_id) = 1
           AND imm.vaccine_id IN (
           SELECT vaccine_id 
           FROM prd_irowner.vaccine_group_children 
           WHERE vaccine_group_id = 1131 )
        )sub2
    )
    ;
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\patient_record_source.csv";
/* Associate client with last_updated_org_id to determine record source - patient_record_source.csv file */
/* If the org id is either a child or master org id then it is 2 (hl7) otherwise 1(user interface)*/
/* In case of Frank Baum 4384 as well the source is 2(hl7) */
select c.client_id,
        case when c.last_updated_by_org_id in (select child_organization_id from prd_irowner.org_children oc) then 2
        when c.last_updated_by_org_id in (select master_organization_id from prd_irowner.org_children oc) then 2
        when c.last_updated_by_org_id = 4384 then 2
        else 1 end as record_source_id
    from
        prd_irowner.clients c
    where c.client_id not in (
        select distinct sub.client_id from (
        SELECT imm.client_id as client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id 
        FROM prd_irowner.immunizations imm
        JOIN prd_irowner.clients cl ON cl.client_id = imm.client_id
        WHERE imm.vaccination_date >= TO_DATE('01-JAN-2009', 'DD-MON-YYYY')
          AND cl.consent_ind = 'N'
        GROUP BY imm.client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id
        HAVING COUNT(DISTINCT imm.vaccine_id) = 1
           AND imm.vaccine_id IN (
           SELECT vaccine_id 
           FROM prd_irowner.vaccine_group_children 
           WHERE vaccine_group_id = 1131 )
            )sub
        )
    order by c.client_id;
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\hl7_senders.csv";
/* hl7 senders -  hl7_senders.csv */
select master_organization_id --,po.name
    from
        PRD_IROWNER.org_children ch join 
        prd_irowner.provider_organization po
        on ch.master_organization_id=po.provider_organization_id
    group by master_organization_id --,po.name
    order by master_organization_id;
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\patient_data.csv";
/* patient_data.csv file*/
select distinct replace(c.first_name,',','') as first_name,
        replace(c.middle_name,',','') as middle_name,
        replace(c.last_name,',','') as last_name,
        replace(c.name_suffix,',','') as name_generation_code_id,
        '' as title_code_id,  -- Does not seem like a title is associated with a client
        c.sex_code as gender_code_id,
        to_char(c.birth_date,'YYYY-MM-DD') as dob,
        '' as vfc_code_id,  -- calculated separately
        c.client_id as other_identifier,
        '' as other_identifier_2,
        '' as ssn,
        '' as occupation_code_id,   --added in version 2.0
        '' as language_code_id,  --language code for all clients is empty in db
        '' as alias_first_name,
        '' as alias_middle_name,
        '' as alias_last_name,
        '' as alias_generation_code_id,
        '' as cell_phone_number,
        '' as work_phone_number,
        case when (ph.phone_number is not null and ph.phone_number !='0000000')
            then case when ph.area_code is not null then  
                    ph.area_code||'-'||ph.phone_number
                else '808-'||ph.phone_number end
            else '' end as home_phone_number,
        replace(ad.email_address,',','') as email_address,
        'N' as send_reminder_recall,
        trim(replace(ad.street_address_line,',','') ||' '|| replace(ad.other_address_line,',','')) as mailing_address_line1,
        case when ad.po_box_route_line is not null then 'PO Box '||replace(replace(replace(replace(ad.po_box_route_line,'"',''),',',''),'.',''),'PO BOX ','') else '' end as mailing_address_line2,
        replace(ad.city_name,',','') as mailing_address_city,
        get_county(ad.zip_code) as mailing_address_county,
        replace(ad.state_code,',','') as mailing_address_state,
        ad.zip_code as mailing_address_zip,
        --physical address
        c.ethnicity_code as ethnicity_code_id,
        -- race codes
        case when py.first_name is not null then
            case when py.middle_name is not null then 
                trim(replace(py.first_name||' '||py.middle_name||' '||py.last_name,',','')) 
            else
                trim(replace(py.first_name||' '||py.last_name,',','')) end
        else '' end as primary_physician_name,
        trim(replace(ad1.street_address_line ||' '|| ad1.other_address_line ||' '||ad1.city_name||' '||ad1.zip_code,',','')) as primary_physician_contact_info,
        -- Birth info field - nothing to migrate
        replace(c.mothers_maiden_last,',','') as mother_maiden_name,
        replace(c.mothers_first_name,',','') as mother_first_name,
        '' as mother_middle_name,
        '' as mother_last_name,
        '' as father_first_name,
        '' as father_middle_name,
        '' as father_last_name,
        '' as father_name_generation_code_id,
        '' as clinic_unique_id,  -- no default clinic for patient, established via last administered non-flu vaccination
        to_char(c.death_date,'YYYY-MM-DD') as death_date,
        '' as death_certificate_id,
        case when c.opt_out='Y' then 4
            when c.death_date is not null then 3
            --when ((ad.zip_code not like '967%') AND (ad.zip_code not like '968%')) then 2  --removed this after discussion with Jim 1/31
            else 1 end as iz_program_clinic_status_code_id,
        '' as iz_program_clinic_inactive_reason_code_id,  --questions surrounding this. Need to circle back
        case when c.opt_out='Y' then 4
            when c.death_date is not null then 3
            when ((ad.zip_code not like '967%') AND (ad.zip_code not like '968%')) then 2  -- physical address is not within state
            else 1 end as iz_program_jurisdiction_status_code_id,
        '' as iz_program_jurisdiction_reason_code_id,     --questions surrounding this. Need to circle back
        '' as iz_program_effective_date,   -- Let envision choose this
        to_char(c.date_entered,'MM/DD/YYYY') as creation_date,
        to_char(c.last_updated_date,'MM/DD/YYYY') as updated_date,
        replace(users.first_name||' '||users.last_name,',','') as legacy_created_by_name,
        c.create_user_id as legacy_created_by_id,
        replace(users1.first_name||' '||users1.last_name,',','') as legacy_updated_by_name,
        c.last_updated_by_user_id as legacy_updated_by_id,
        '' as record_source_id --could be calculated later by using last_updated_by_org_id
    from 
        prd_irowner.clients c left join prd_irowner.address ad --to get address
        on c.address_id=ad.address_id
        left join prd_irowner.phone_number ph  --to get phone number
        on c.phone_number_id=ph.phone_number_id
        left join prd_irowner.physician py   --to get primary physician
        on c.physician_id=py.physician_id
        left join prd_irowner.address ad1  -- to get address of physician
        on py.address_id =ad1.address_id
        left join prd_irowner.ptl_users users  -- to get name of user who created the client record
        on c.create_user_id=users.user_id
        left join prd_irowner.ptl_users users1  --to get name of user who last updated the client record
        on c.last_updated_by_user_id=users1.user_id
        
    where c.client_id not in (
        select distinct sub.client_id from (
        SELECT imm.client_id as client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id 
        FROM prd_irowner.immunizations imm
        JOIN prd_irowner.clients cl ON cl.client_id = imm.client_id
        WHERE imm.vaccination_date >= TO_DATE('01-JAN-2009', 'DD-MON-YYYY')
          AND cl.consent_ind = 'N'
        GROUP BY imm.client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id
        HAVING COUNT(DISTINCT imm.vaccine_id) = 1
           AND imm.vaccine_id IN (
           SELECT vaccine_id 
           FROM prd_irowner.vaccine_group_children 
           WHERE vaccine_group_id = 1131 )
        )sub
    )
    ;
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\patient_insurance.csv";
/* Query to get patient insurance data*/
/* patient_insurance.csv */

select ci.client_id as other_identifier,
        replace(i.name,',','') as health_insurance_code_id,
        ci.policy_nbr as insurance_id
        
    from
        prd_irowner.client_insurer ci join prd_irowner.insurer i
        on ci.insurer_id=i.insurer_id
    where ci.client_id not in (
        select distinct sub.client_id from (
        SELECT imm.client_id as client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id 
        FROM prd_irowner.immunizations imm
        JOIN prd_irowner.clients cl ON cl.client_id = imm.client_id
        WHERE imm.vaccination_date >= TO_DATE('01-JAN-2009', 'DD-MON-YYYY')
          AND cl.consent_ind = 'N'
        GROUP BY imm.client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id
        HAVING COUNT(DISTINCT imm.vaccine_id) = 1
           AND imm.vaccine_id IN (
           SELECT vaccine_id 
           FROM prd_irowner.vaccine_group_children 
           WHERE vaccine_group_id = 1131 )
        )sub
    )
    ;
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\patient_contacts.csv";
/*Query to get patient contacts */
/* patient_contacts.csv */

select rp.client_id as other_identifier,
        rp.relationship_to_client as patient_contact_type_code_id,
        rds_irowner.clean_up_name(initcap(trim(replace(replace(replace(rp.first_name,',',''),'"', ''),'.','')))) as first_name,
        rds_irowner.clean_up_name(initcap(trim(replace(replace(replace(rp.middle_name,',',''),'"', ''),'.','')))) as middle_name,
        rds_irowner.clean_up_name(initcap(trim(replace(replace(replace(rp.last_name,',',''),'"', ''),'.','')))) as last_name,
        replace(rp.name_suffix,',','') as name_generation_code_id,
        case when ph.device_type_code='PH' and ph.phone_number is not null and ph.phone_number not in ('0000000','9999999','8888888')
            then case when ph.area_code is not null then  
                    ph.area_code||'-'||ph.phone_number
                else
                    '808-'||ph.phone_number end
            else '' end as cell_phone_number,
        case when ph.device_type_code='HO' and ph.phone_number is not null and ph.phone_number not in ('0000000','9999999','8888888')
            then case when ph.area_code is not null then  
                    ph.area_code||'-'||ph.phone_number
                else
                    '808-'||ph.phone_number end
            else '' end as work_phone_number,
        case when ph.device_type_code='H' and ph.phone_number is not null and ph.phone_number not in ('0000000','9999999','8888888')
            then case when ph.area_code is not null then  
                    ph.area_code||'-'||ph.phone_number
                else
                    '808-'||ph.phone_number end
            else '' end as home_phone_number,
        case when ph.device_type_code='7' and ph.phone_number is not null and ph.phone_number not in ('0000000','9999999','8888888')
            then case when ph.area_code is not null then  
                    ph.area_code||'-'||ph.phone_number
                else
                    '808-'||ph.phone_number end 
            else '' end as emergency_phone_number,
        
        replace(ad.email_address,',','') as email_address,
        rp.primary_ind as primary_contact_indicator
        
    from
        prd_irowner.responsible_person rp join prd_irowner.address ad
        on rp.address_id = ad.address_id
        join prd_irowner.phone_number ph 
        on rp.responsible_person_id=ph.responsible_person_id
    where rp.client_id not in (
        select distinct sub.client_id from (
        SELECT imm.client_id as client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id 
        FROM prd_irowner.immunizations imm
        JOIN prd_irowner.clients cl ON cl.client_id = imm.client_id
        WHERE imm.vaccination_date >= TO_DATE('01-JAN-2009', 'DD-MON-YYYY')
          AND cl.consent_ind = 'N'
        GROUP BY imm.client_id, cl.first_name, cl.middle_name, cl.last_name, cl.birth_date, imm.vaccination_date, imm.vaccine_id
        HAVING COUNT(DISTINCT imm.vaccine_id) = 1
           AND imm.vaccine_id IN (
           SELECT vaccine_id 
           FROM prd_irowner.vaccine_group_children 
           WHERE vaccine_group_id = 1131 )
        )sub
    ) 
    ;
spool off;

--set SQLFORMAT
--SET SQLFORMAT csv
--set loadformat enclosures off
--set feedback off

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\vaccination_data.csv";
-- Queries to get vaccination data
-- tables of interest 
-- immunizations
/* vaccination_data.csv file */
select  imm.client_id as other_identifier
        ,imm.immunization_id as vaccination_identifier
        ,to_char(imm.vaccination_date,'MM/DD/YYYY') as vaccination_date
        ,vac.cvx_code
        ,man.manufacturer_code as mvx_code
        ,case 
            when vl.lot_number is null then imm.historical_lot_number
            else vl.lot_number end as lot_number
        ,ndc_list.ndc_number as ndc_number
        ,case /* We also have funding type public but not clear if state or VFC so not considering*/
            when imm.funding_type='PRIVATE' then 3
            else null end as funding_source_id
        ,to_char(vl.expiration_date,'MM/DD/YYYY') as expiration_date
        ,imm.body_site_code as body_site_code_id
        ,imm.administration_route_code as body_route_code_id
        ,case 
            when vl.dose is null then vac.default_dose_size
            else vl.dose end as dosage_ml
        ,case when rl.reaction_code is not null then 'Y'
            else 'N' end as reaction_flag
        ,case when imm.historical_ind='00' then 'N'  -- 00 means N and 01 means Y
            else 'Y' end as historical_flag
        ,case when rds_irowner.is_hl7sender(imm.entered_by_org_id)='false' then imm.entered_by_org_id 
            else 99999 end as clinic_unique_id
        ,case
            when imm.funding_program_code is null then cfp.funding_program_code
            else imm.funding_program_code end as vfc_code_id     -- blanks need to be filled using age criteria
        ,to_char(imm.date_entered,'MM/DD/YYYY') as creation_date
        ,to_char(imm.last_updated_date,'MM/DD/YYYY') as updated_date
        ,trim(users1.first_name||' '||users1.last_name) as legacy_created_by_name
        ,imm.create_user_id as legacy_created_by_id
        ,trim(users2.first_name||' '||users2.last_name) as legacy_updated_by_name
        ,imm.last_updated_user_id as legacy_updated_by_id
        --added 6/4/25
        ,trim(clinician_ord.first_name||' '||trim(clinician_ord.last_name)) as legacy_prescribed_by_name   
        --,imm.provider_id as legacy_prescribed_by_id
        ,trim(clinician_adm.first_name||' '||trim(clinician_adm.last_name)) as legacy_administered_by_name
        --,imm.administered_by_id as legacy_administered_by_id
        -- adding vis 05/22/2025
        ,sub.name_list as vis_names
        ,sub.date_list as vis_dates
        
        ,imm.source_id as record_source_id   -- 1 is user interface 2 is hl7 or batch load
        ,'N' as deleted_flag  --No immunizations from immunizations_delete table are in immunizations table
        ,rds_irowner.get_insurance_code(imm.sfas_insurance_id) as health_insurance_code_id   -- vaccination level insurance added 5/21/25
        ,case
            when imm.sfas_insurance_id not in (null,0,5,10,57) then trim(replace(imm.sfas_insurance_policy,',',''))
            else '' end as insurance_id  -- added 5/21/25
        ,case
            when imm.sfas_insurance_id not in (null,0,5,10,57) then to_char(imm.last_updated_date,'MM/DD/YYYY')
            else '' end as date_last_verified  --added 5/21/25
    from
        prd_irowner.immunizations imm left join prd_irowner.vaccine vac
        on imm.vaccine_id=vac.vaccine_id
        left join prd_irowner.vaccine_lot vl
        on imm.vaccine_lot_id = vl.vaccine_lot_id
        left join prd_irowner.ndc_listing ndc_list
        on vl.ndc_listing_id = ndc_list.ndc_listing_id
        left join prd_irowner.reaction_link rl
        on imm.immunization_id=rl.immunization_id
        left join prd_irowner.ptl_users users1
        on imm.create_user_id=users1.user_id
        left join prd_irowner.ptl_users users2
        on imm.last_updated_user_id=users2.user_id
        left join prd_irowner.manufacturer man
        on imm.manufacturer_id=man.manufacturer_id
        left join prd_irowner.client_funding_program cfp
        on imm.client_id = cfp.client_id and imm.vaccination_date=cfp.screen_date
        
        left join 
        (
            select vrr.immunization_id as imm_id,
            listagg(to_char(vr.vis_revision_date,'MM/DD/YYYY'),',') as date_list,
            listagg(trim(vg.display_name),',') as name_list
            from 
                prd_irowner.vis_revision_received vrr join prd_irowner.vis_revision vr
                on vrr.vis_revision_id= vr.vis_revision_id
                join prd_irowner.vaccine_group vg
                on vr.vaccine_group_id = vg.vaccine_group_id
            group by vrr.immunization_id
        ) sub
        on imm.immunization_id = sub.imm_id 
        left join prd_irowner.clinician clinician_ord
        on imm.provider_id=clinician_ord.clinician_id
        left join prd_irowner.clinician clinician_adm
        on imm.administered_by_id=clinician_adm.clinician_id
    ;
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\patient_allergy_risks.csv";

select cc.client_id as other_identifier,
        trim(replace(sc.comment_text,',','')) as allergy_risk_desc,
       case
        when sc.comment_code='03' then 10021 
        when sc.comment_code='04' then 10005
        when sc.comment_code='10_130' then 10026
        when sc.comment_code='10_26' then 10037
        when sc.comment_code='26' then 10008
        when sc.comment_code='27' then 10009
        when sc.comment_code='28' then 10010
        when sc.comment_code='31' then 10011
        when sc.comment_code='33' then 10012
        when sc.comment_code='33A' then 10013
        when sc.comment_code='36' then 10002
        when sc.comment_code='HEPA_I' then 10007
        else null end as allergy_risk_code_id,
       --cc.provider_organization_id as clinic_unique_id,
       to_char(cc.applies_to_date,'MM/DD/YYYY') as start_date,
       to_char(cc.applies_to_end_date,'MM/DD/YYYY') as end_date
    from 
        prd_irowner.client_comment cc  join prd_irowner.standard_comment sc
        on cc.comment_code = sc.comment_code;
    
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\vaccine_adverse_reactions.csv";

select rl.immunization_id as vaccination_identifier,
        case
            when rl.reaction_code='10' then 2 
            when rl.reaction_code='HYPOTON' then 3
            when rl.reaction_code='CRYING' then 4
            when rl.reaction_code='HI009' then 6 
            when rl.reaction_code='FEVER105' then 7 
            when rl.reaction_code='HI011' then 8
            when rl.reaction_code='HI013' then 9 
            when rl.reaction_code='SEIZURE' then 12 
            when rl.reaction_code='HI001' then 13 
            when rl.reaction_code='HI003' then 14 
            when rl.reaction_code='HI005' then 15 
            when rl.reaction_code='HI007' then 16 
            when rl.reaction_code='HI015' then 17 
            when rl.reaction_code='HI017' then 18 
            when rl.reaction_code='HI019' then 19
            when rl.reaction_code='OTH' then 20
            else null end as reaction_code_id,
        to_char(rl.applies_to_date,'MM/DD/YYYY') as reaction_date,
        trim(replace(replace(replace(rl.description_text,',',''),chr(13),''),chr(10),'')) as allergy_risk_desc
    from 
        prd_irowner.reaction_link rl
    ;
spool off;

spool "C:\Users\S.Chintabathina\Desktop\query_results\data_files\missing_first_match.csv";

WITH NullNameClients AS (
    SELECT 
        c.CLIENT_ID AS null_client_id,
        c.birth_date AS null_birth_date,
        c.last_name AS null_last_name,
        c.MOTHERS_FIRST_NAME AS null_mother_first_name,
        c.MOTHERS_MAIDEN_LAST AS null_mother_maiden_last,
        c.date_entered,
        c.last_updated_date,
        c.create_org_id,
        c.CREATE_SRC_ID,
        i.IMMUNIZATION_ID AS null_immunization_id,
        i.PROVIDER_ORGANIZATION_ID AS null_provider_org_id,
        i.DATE_ENTERED AS null_vaccine_date
    FROM prd_irowner.clients c
    LEFT JOIN prd_irowner.immunizations i ON c.CLIENT_ID = i.CLIENT_ID
    WHERE c.first_name IS NULL
      --AND i.vaccine_id = 34
),
MatchedClients AS (
    SELECT 
        distinct n.null_client_id,
        o.CLIENT_ID AS match_client_id,
        o.first_name AS match_first_name,
        o.last_name AS match_last_name,
        o.birth_date AS match_birth_date,
        o.MOTHERS_FIRST_NAME AS match_mother_first_name,
        o.MOTHERS_MAIDEN_LAST AS match_mother_maiden_last,
        o.date_entered AS match_date_entered,
        o.last_updated_date AS match_last_updated_date,
        o.create_org_id AS match_create_org_id,
        o.CREATE_SRC_ID AS match_create_src_id,
        i.IMMUNIZATION_ID AS match_immunization_id,
        i.PROVIDER_ORGANIZATION_ID AS match_provider_org_id,
        i.DATE_ENTERED AS match_vaccine_date,
        ROW_NUMBER() OVER (
            PARTITION BY n.null_client_id 
            ORDER BY o.CLIENT_ID
        ) AS rn
    FROM NullNameClients n
    JOIN prd_irowner.clients o 
        ON n.null_birth_date = o.birth_date
        and n.null_last_name = o.last_name
        /*AND (n.null_mother_first_name = o.MOTHERS_FIRST_NAME 
             OR UTL_MATCH.EDIT_DISTANCE(n.null_mother_first_name, o.MOTHERS_FIRST_NAME) <= 2)
        AND (n.null_mother_maiden_last = o.MOTHERS_MAIDEN_LAST 
             OR n.null_mother_maiden_last LIKE '%' || o.MOTHERS_MAIDEN_LAST || '%')*/
        AND o.first_name IS NOT NULL
    LEFT JOIN prd_irowner.immunizations i ON o.CLIENT_ID = i.CLIENT_ID
    WHERE i.vaccine_id = 34 --HepB Peds
)
SELECT 
    null_client_id,
    match_client_id,
    match_first_name,
    match_last_name,
    match_birth_date,
    match_mother_first_name,
    match_mother_maiden_last,
    match_date_entered,
    match_last_updated_date,
    match_create_org_id,
    match_create_src_id,
    match_immunization_id,
    match_provider_org_id,
    match_vaccine_date
FROM MatchedClients
WHERE rn = 1 
ORDER BY null_client_id, match_client_id;

spool off;
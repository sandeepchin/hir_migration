
/* Copyright (c) 2025. Sandeep Chintabathina */

/* A function that return whether or not an org is a hl7 sender */

--boolean values do not work in oracle sql but will work in oracle pl/sql
-- So using varchar2 as return value here
create or replace function  is_hl7sender
    (org_id in number)
    return varchar2 as
    begin
      if org_id in (3920,4100,4140,4349,7740,8080,8901,8921,9041,9302,
      11243,11426,11564,11584,11694,12048,12504,13164,13244,13264,13304,13365,13504) then
            return 'true';
        elsif org_id in (4040,4217,4348,7681,7820,8561,9221,9642,12464) then /*Making this elsif to identify former hl7 senders*/
            return 'true';
        else
            return 'false';
        end if;
    end is_hl7sender;
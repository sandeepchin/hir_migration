
/* Copyright (c) 2025. Sandeep Chintabathina */

create or replace FUNCTION clean_up_name
    (name in varchar2)
    RETURN VARCHAR2 AS 
    BEGIN
       if name in ('None','Pt','Patient','Time','Listed','Per','Per Pt','Perpt', 'Permom', 'Permother','Given','To', 'Give', 'Mother', 'Parent','-','No','Contact','Contacts','Unknown','Unk','X','Here') then
            return null;
       else
            return name;
        end if;
    END clean_up_name;
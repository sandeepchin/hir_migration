
/* Copyright (c) 2025. Sandeep Chintabathina */

create or replace function get_county
      (zipcode in varchar2)
    return varchar2
    as
    begin
      case zipcode
        when '96701' then return 'Honolulu';
        when '96703' then return 'Kauai';
        when '96704' then return 'Hawaii';
        when '96705' then return 'Kauai';
        when '96706' then return 'Honolulu';
        when '96707' then return 'Honolulu';
        when '96708' then return 'Maui';
        when '96709' then return 'Honolulu';
        when '96710' then return 'Hawaii';
        when '96712' then return 'Honolulu';
        when '96713' then return 'Maui';
        when '96714' then return 'Kauai';
        when '96715' then return 'Kauai';
        when '96716' then return 'Kauai';
        when '96717' then return 'Honolulu';
        when '96718' then return 'Hawaii';
        when '96719' then return 'Hawaii';
        when '96720' then return 'Hawaii';
        when '96721' then return 'Hawaii';
        when '96722' then return 'Kauai';
        when '96725' then return 'Hawaii';
        when '96726' then return 'Hawaii';
        when '96727' then return 'Hawaii';
        when '96727' then return 'Hawaii';
        when '96728' then return 'Hawaii';
        when '96729' then return 'Maui';
        when '96730' then return 'Honolulu';
        when '96731' then return 'Honolulu';
        when '96732' then return 'Maui';
        when '96733' then return 'Maui';
        when '96734' then return 'Honolulu';
        when '96737' then return 'Hawaii';
        when '96738' then return 'Hawaii';
        when '96739' then return 'Hawaii';
        when '96740' then return 'Hawaii';
        when '96741' then return 'Kauai';
        when '96742' then return 'Maui';
        when '96743' then return 'Hawaii';
        when '96744' then return 'Honolulu';
        when '96745' then return 'Hawaii';
        when '96746' then return 'Kauai';
        when '96747' then return 'Kauai';
        when '96748' then return 'Maui';
        when '96749' then return 'Hawaii';
        when '96750' then return 'Hawaii';
        when '96751' then return 'Kauai';
        when '96752' then return 'Kauai';
        when '96753' then return 'Maui';
        when '96753' then return 'Maui';
        when '96754' then return 'Kauai';
        when '96755' then return 'Hawaii';
        when '96756' then return 'Kauai';
        when '96757' then return 'Maui';
        when '96759' then return 'Honolulu';
        when '96760' then return 'Hawaii';
        when '96761' then return 'Maui';
        when '96762' then return 'Honolulu';
        when '96763' then return 'Maui';
        when '96764' then return 'Hawaii';
        when '96765' then return 'Kauai';
        when '96766' then return 'Kauai';
        when '96767' then return 'Maui';
        when '96768' then return 'Maui';
        when '96769' then return 'Kauai';
        when '96770' then return 'Maui';
        when '96771' then return 'Hawaii';
        when '96772' then return 'Hawaii';
        when '96773' then return 'Hawaii';
        when '96774' then return 'Hawaii';
        when '96776' then return 'Hawaii';
        when '96777' then return 'Hawaii';
        when '96778' then return 'Hawaii';
        when '96779' then return 'Maui';
        when '96780' then return 'Hawaii';
        when '96781' then return 'Hawaii';
        when '96782' then return 'Honolulu';
        when '96783' then return 'Hawaii';
        when '96784' then return 'Maui';
        when '96785' then return 'Hawaii';
        when '96786' then return 'Honolulu';
        when '96788' then return 'Maui';
        when '96789' then return 'Honolulu';
        when '96790' then return 'Maui';
        when '96791' then return 'Honolulu';
        when '96792' then return 'Honolulu';
        when '96793' then return 'Maui';
        when '96795' then return 'Honolulu';
        when '96796' then return 'Kauai';
        when '96797' then return 'Honolulu';
        when '96801' then return 'Honolulu';
        when '96802' then return 'Honolulu';
        when '96803' then return 'Honolulu';
        when '96804' then return 'Honolulu';
        when '96805' then return 'Honolulu';
        when '96806' then return 'Honolulu';
        when '96807' then return 'Honolulu';
        when '96808' then return 'Honolulu';
        when '96809' then return 'Honolulu';
        when '96810' then return 'Honolulu';
        when '96811' then return 'Honolulu';
        when '96812' then return 'Honolulu';
        when '96813' then return 'Honolulu';
        when '96814' then return 'Honolulu';
        when '96815' then return 'Honolulu';
        when '96816' then return 'Honolulu';
        when '96817' then return 'Honolulu';
        when '96818' then return 'Honolulu';
        when '96819' then return 'Honolulu';
        when '96820' then return 'Honolulu';
        when '96821' then return 'Honolulu';
        when '96822' then return 'Honolulu';
        when '96823' then return 'Honolulu';
        when '96824' then return 'Honolulu';
        when '96825' then return 'Honolulu';
        when '96826' then return 'Honolulu';
        when '96827' then return 'Honolulu';
        when '96828' then return 'Honolulu';
        when '96830' then return 'Honolulu';
        when '96835' then return 'Honolulu';
        when '96836' then return 'Honolulu';
        when '96837' then return 'Honolulu';
        when '96838' then return 'Honolulu';
        when '96839' then return 'Honolulu';
        when '96850' then return 'Honolulu';
        when '96853' then return 'Honolulu';
        when '96854' then return 'Honolulu';
        when '96857' then return 'Honolulu';
        when '96857' then return 'Honolulu';
        when '96858' then return 'Honolulu';
        when '96859' then return 'Honolulu';
        when '96860' then return 'Honolulu';
        when '96861' then return 'Honolulu';
        when '96862' then return 'Honolulu';
        when '96863' then return 'Honolulu';
        when '96898' then return 'Honolulu';
        else return '';
    end case;
end;

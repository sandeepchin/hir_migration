
/* Copyright (c) 2025. Sandeep Chintabathina */

CREATE OR REPLACE FUNCTION GET_INSURANCE_CODE 
        (sfas_code in INTEGER)
    RETURN INTEGER AS 
    BEGIN
        case 
            when sfas_code=50 then return 11; /* HMSA */
            when sfas_code=51 then return 22; /* Quest/HMSA */
            when sfas_code=52 then return 14; /* Kaiser */
            when sfas_code=53 then return 23; /* Quest/Kaiser */
            when sfas_code=54 then return 21; /* Quest/Alohacare */
            when sfas_code=55 then return 10; /* HMAA */
            when sfas_code=56 then return 27; /* UHA */
                                             /* 57 not mapped */
            when sfas_code=58 then return 26; /* Champus/Tricare */
            when sfas_code=59 then return 29; /* Ohana */
            when sfas_code=60 then return 28; /* United Healthcare */
            when sfas_code=61 then return 30; /* Quest/United Healthcare */
            when sfas_code=62 then return 26; /* Champus */
            when sfas_code=63 then return 16; /* MDX */
            when sfas_code=64 then return 9; /* HMA */
            when sfas_code=1 then return 19; /* Other */
            else return null; /* 5,10,57,0 cases */
        end case;
    END GET_INSURANCE_CODE;
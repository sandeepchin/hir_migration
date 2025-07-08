
/* Copyright (c) 2025. Sandeep Chintabathina */

/* Bulk inserting providers, clinics, users, user_clinics, hl7_users, hl7_clinics, patient notes, 
clinics notes, patient insurance, patient contacts, schools, school districts, patient allergy risks, 
and adverse reactions in that order */

use webiz_import_stage_hi;
go

bulk insert dbo.provider_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\providers_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.clinic_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\clinics_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.user_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\users_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.user_clinic_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\user_clinics_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.hl7_user_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\hl7_users_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.hl7_clinic_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\hl7_clinics_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)

bulk insert dbo.patient_notes_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\patient_notes_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.clinic_notes_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\clinic_notes_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.patient_insurance_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\patient_insurance_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.patient_contacts_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\patient_contacts_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.schools_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\schools_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.school_districts_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\school_districts_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.patient_allergy_risks_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\patient_allergy_risks_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO

bulk insert dbo.adverse_reactions_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\db_files\vaccine_adverse_reactions_bulk_insert.csv'
with 
(
	--FORMAT='csv',
	--DATAFILETYPE = 'char',
	FIELDTERMINATOR = ',',
	ROWTERMINATOR = '\n',
	FIRSTROW = 2,
	BATCHSIZE=100000
	--ERRORFILE = 'C:\Users\envSQLadmin\Desktop\SQLscripts\bulk_errors.txt'
)
GO
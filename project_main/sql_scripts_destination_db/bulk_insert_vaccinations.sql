
/* Copyright (c) 2025. Sandeep Chintabathina */

/* Query to bulk insert vaccination data into vaccination_view and thus patient_vaccinations table */

bulk insert dbo.vaccination_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\vaccinations_bulk_insert.csv'
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
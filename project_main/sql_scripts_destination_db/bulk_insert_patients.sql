
/* Query to bulk inseert data from a csv into patients table via patients_view */

/* If you get permissions error then right click on containing folder and on security tab
click on Edit and then Add in the next window
Search for user "SERVICE" and give them full permission 
It should resolve the issue*/

/* null values are not recognized in csv, so remove them. Replace by blank even for numerical fields.
Null values are inserted by default for blank values */

use webiz_import_stage_hi;
go

bulk insert dbo.patient_view
from 'C:\Users\envSQLadmin\Desktop\SQLscripts\patients_bulk_insert.csv'
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
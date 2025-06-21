This project was a direct outcome of transitioning from one Immunization Information system to another. Immunization Information Servers(IIS), as they are formally called, store all data related to patient immunizations. 

The process of migration involves 3 steps:
1. Extract important data from the older system using SQL scripts on legacy database
2. Process the extracted data, clean and format it to meet the specifications of the new system
3. Insert formatted data into the tables defined by the new system's schema

In project_main folder you will see python files and SQL files.
- SQL scripts in sql_scripts_source_db folder correspond to step 1 above
- Python files contain code which corresponds to step 2 above
- SQL scripts in sql_scripts_destination_db folder correspond to step 3 above

For more information, please reach out to sandeep.chintabathina at gmail dot com

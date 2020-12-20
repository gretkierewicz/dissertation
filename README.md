# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###20/12/2020

- FIX - Employees list view will now send full data with CSV format
- Added output with messages to the employees/csv_files_upload action. 
Now it displays records' Errors, Updated/Created successfully and No action (by the e_mail) 

To be done:

- Create rest of methods for Orders view set
- Implement additional models
- Implement filters, sorting or search
- Add messages/errors
- Implement validator for 'abbreviation' excluding polish marks (should be slugfield) - same for code in modules
- Supervisor validator needs update - it does not work for csv_files_upload! 
context's request url is pointing action, not the employee

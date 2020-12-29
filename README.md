# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###29/12/2020

- FIX / OrderShortSerializer minor update for better readability
- MODELS / Update of CHOICES fields - for better readability of links
- Orders / Moved query from 'retrieve' method to 'get_object' - it will be common for all detail-view methods
- URLS / Update of path for OrderViewSet, so it includes all methods

To be done:

- Create rest of methods for Orders view set
- Implement additional models
- Implement filters, sorting or search
- Add messages/errors
- Implement validator for 'abbreviation' excluding polish marks (should be slugfield) - same for code in modules
- Supervisor validator needs update - it does not work for csv_files_upload! 
context's request url is pointing action, not the employee

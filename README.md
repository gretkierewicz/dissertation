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
- MODELS / Update of 'slug' field type: employee.abbreviation and module.code
- FIX / supervisor validator for csv upload

To be done:

- Implement additional models
- Implement filters, sorting or search
- Add messages/errors

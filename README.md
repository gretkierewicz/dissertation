# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###19/12/2020

- FIX - Forgot about proper filtering of modules nested into employees view
- Update - url's routers commentary and minor update for Order's retrieve function parameter

To be done:

- Create rest of methods for Orders view set
- Implement additional models
- Implement filters, sorting or search
- Add commentary
- Add messages/errors
- Implement validator for 'abbreviation' excluding polish marks (should be slugfield) - same for code in modules

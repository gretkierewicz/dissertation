# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###17/12/2020

- Customization of Degrees list view by adding new serializer (less information in list - more in detail)
- Extending customization to Positions and Employees lists
- Correction to tests for Degrees, Positions, Employees
- Minor cleanup in urls before using nested routers

To be done:

- Create rest of methods for Orders view set
- Implement additional models
- Implement filters, sorting or search
- Add commentary
- Add messages/errors
- Implement validator for 'abbreviation' excluding polish marks
- Create sub-views i.e. employees/GBr/modules/ (https://github.com/alanjds/drf-nested-routers)

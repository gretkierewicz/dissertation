# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

For now it will be local only, with SQLite DB.

## Last changes
###17/11/2020

- Added Employees table
- Some minor customization of displayed tables
- Inserted UNIQUE property for e_mail column in Employees table
- CSV Export option

To be done:

- Validation of fields/moving some parts of code to models if needed
- Messages about statuses - edited properly and such
- Validation of UNIQUE columns -> form should pop out message about field (it does not now)
- CSV Import option
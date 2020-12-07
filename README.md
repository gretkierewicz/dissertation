# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

For now it will be local only, with SQLite DB.

## Last changes
###07/12/2020

- Minor fix for allowing empty supervisor form field
- Added EmployeeRenderer class for even better CSV export labels
- Created additional option - bulk upload - allowing sending CSV file(s) with some validation. \
    POST method for sending new values (existing entries with unique field will not be updated) \
    PUT method for updating existing entries and creating new as well \
    Validation for Employees model because of related fields
- Making example of disallowing DELETE method from view (DegreesViewSet)
- Big cleanup of not used files and entries

To be done:

- Implement TESTS!
- Implement additional models

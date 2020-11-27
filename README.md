# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

For now it will be local only, with SQLite DB.

## Last changes
###27/11/2020

- Added can_delete_records flag for each table (in views for now)
- Delete view now responds to the POST method - need to update for DELETE later 

To be done:

- Update methods that should be 'PUT' or 'DELETE'
- Validation in the online form - popping out messages for fields
- Implement TESTS!
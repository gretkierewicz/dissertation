# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

For now it will be local only, with SQLite DB.

## Last changes
###25/11/2020

- Changing import procedure - will need messages to give feedback about failed records and such
- Eliminating creation of empty string entries in the Degrees and Positions tables
- Messages about statuses - edited properly deleted and so on
- Updated import procedure for employees model - more validation of data

To be done:

- Change methods that should be 'PUT' or 'DELETE' at least to the 'POST' for now!
- Validation in the online form - popping out messages for fields
- Implement TESTS!

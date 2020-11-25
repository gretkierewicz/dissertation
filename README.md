# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

For now it will be local only, with SQLite DB.

## Last changes
###25/11/2020

- Changing import procedure - will need messages to give feedback about failed records and such
- Eliminating creation of empty string entries in the Degrees and Positions tables

To be done:

- Validation of fields/moving some parts of code to models if needed
- Messages about statuses - edited properly deleted and so on
- Validation of UNIQUE columns -> form should pop out message about field (it does not now)
- Implement TESTS!

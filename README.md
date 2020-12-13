# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###13/12/2020

- Corrections after deploying at ct8.pl
- Running app at http://gret.ct8.pl/ with use of MySQL (possible future tests with PostgreSQL/MongoDB)
- Tests for Employees model, view and serializer
- Tests for Positions model, view and serializer - 1 Fail - delete still possible
- FIX - delete not possible at Position view
- FIX - sending empty 'year_of_studies' field was causing error because of SQLite correction
- Major refactoring TESTs, after adding supervisor self relation test - bug was found

To be done:

- Implement additional models
- Implement filters, sorting or search
- Add commentary
- Add messages/errors

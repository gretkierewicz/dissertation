# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###16/12/2020

- Reshaping MySQL scheme - deleting 'Lesson Type' - will do it with choices
- Created Orders model, serializer and view (View for list, post and request one record for now)
- Some fun with nested serializers - for now only for read_only fields

To be done:

- Create rest of methods for Orders view set
- Implement additional models
- Implement filters, sorting or search
- Add commentary
- Add messages/errors
- Implement validator for 'abbreviation' excluding polish marks

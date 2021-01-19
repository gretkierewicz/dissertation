# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###19/01/2020

- 

### To be done:

- Implement additional models
- Implement filters, sorting or search
- Add messages/errors
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Create static function for try/except reuse (employees csv upload)
- Allow serialization of Modules with nested Orders JSON data (unique create/update methods: https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers)
- Move importing data from csv files to the to_internal_value methods of serializers
- Tests!
- New general view: Modules with missing plans
- Additional views with no nesting (could be problematic with a huge amount of plans or modules)
- Plan constructor view - managing available employees (pensum limit not reached) and not full classes (classes hours not exceeded)
- Unique and Validation tests

# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###17/01/2020

- Implementing the latest project version to the http://gret.ct8.pl
- Implementing Employee's nested Modules view and serializer properly
- Modules / Employee-Module Serializer - minor corrections (changed related name to supervised_modules)
- Plan model - changed methods to properties, so these can be easily used in serializers
- Employee's Plans - implemented View and Serializers (read-only)
- FIX / For Plan Serializer's validation after changing model's methods to props
- Added to Employee: pensum, limit and sum of plan_hours

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
- Validation: pensum and limits

# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###22/01/2020

- Minor updated to models
- Pensum model update - additional field for scholarship, doctoral procedure and years
- Pensum validation and model update. Lowering number of choices for year condition to minimize possibilities of covering same year ranges.
- Rearranging tests and basic objects
- Employee model update - pensum finding property
- FIX / Module csv_files_upload will now properly delete existing classes instances and read number from classes hours columns (regex implemented)
- Module ViewSet retrieve method minor update with help of get_object method (based on https://medium.com/profil-software-blog/10-things-you-need-to-know-to-effectively-use-django-rest-framework-7db7728910e0)
- Implemented nested JSON data import for Modules/Classes/Plans (no error output for now)

### To be done:

- Implement additional models
- Implement filters, sorting or search
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Allow serialization of Modules with nested Orders JSON data (unique create/update methods: https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers)
- Additional views with no nesting (could be problematic with a huge amount of plans or modules)
- Plan constructor view - managing available employees (pensum limit not reached) and not full classes (classes hours not exceeded
- New general view: Modules with missing plans
- Errors output for nested JSON data import

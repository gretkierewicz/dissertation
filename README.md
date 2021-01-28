# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###28/01/2020

- Orders / Changing classes_pk field into nested hyper-link related field for better readability
- Classes / Added students_limit_per_group field. For now manual input per classes instance.
- Orders / Changed classes FK field for OneToOneField and added unique validator to the serializer
- Orders / Added properties: groups_number and order_hours

### To be done:

- Implement additional models: Orders! - more like change Plans to Orders and than implement Plans properly
- Implement custom filters, sorting or search
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save 
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Plan constructor view - managing available employees (pensum limit not reached) and not full classes 
  (classes hours not exceeded)
- Errors output for nested JSON data import

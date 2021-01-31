# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###31/01/2020

- Added plan_sum_hours property to the Order model for future validation purposes.
  Moved plans-related serializer's fields to the nested ClassesOrderSerializer, as there is no use for them in basic one.
  Basic OrdersSerializer stands now only for creating new order from model list view or throwing back form.
  Could be changed in case of importing nested plans' data in orders JSON - needs testing.
- TESTS / Refactoring code - moving some random functions to Utils module

### To be done:

- Implement custom filters, sorting or search
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save 
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Plan constructor view - managing available employees (pensum limit not reached) and not full classes 
  (classes hours not exceeded)
- Errors output for nested JSON data import
- Creating orders only as an additional action from modules and classes views.
- Validators for plans and orders
- Tests

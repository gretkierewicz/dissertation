# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###30/01/2020

- Added action to create Orders from Module list view.
  Added a filter so form includes now only classes without order.
- Orders / deleted main URL. Creating only possible from module list view now.
  /order/ - added as an action in the Classes ViewSet, for now only with GET method.
  Utils / Created variation of NestedHyperlinkedIdentityField with prefix: AdvLookup.
  It allows passing a lookup with double underscore to point nested attributes of instance.
  Plans are now available from orders view - nested in Classes aswell.
- Orders / Added PUT PATCH and DELETE methods to the 'order' action nested in Classes Instance View.
  Small update of ClassesOrderSerializer - URL kwarg for Classes changed to 'name'.

### To be done:

- Implement custom filters, sorting or search
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save 
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Plan constructor view - managing available employees (pensum limit not reached) and not full classes 
  (classes hours not exceeded)
- Errors output for nested JSON data import
- Creating orders only as an additional action from modules and classes views.

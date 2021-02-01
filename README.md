# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###01/02/2020

- Making use of NestedViewSetMixin from rest_framework_nested!
  No longer need to override get_queryset method. 
  parent_lookup_kwargs are get from serializer to filter queryset.
- FIX / EmployeeModuleViewSet - inherits from ModelViewSet now (was ModuleViewSet before - 'typo')
- Orders / Detail view - got rid of parent's kwargs raw filtering with help of NestedViewSetMixin.

### To be done:

- Implement custom filters, sorting or search
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save 
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Plan constructor view - managing available employees (pensum limit not reached) and not full classes 
  (classes hours not exceeded)
- Errors output for nested JSON data import
- Validators for plans and orders
- Tests

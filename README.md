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
- TESTS / Refactoring code - moved some random functions to Utils module
- TESTS / Refactoring code - moved test cases to Utils tests for more clear sharing with other modules
- TESTS / Some additional changes so tests are skipped easier regarding provided data.
- TESTS / Implementing unittests' SubTest method (https://docs.python.org/3/library/unittest.html#distinguishing-test-iterations-using-subtests)
  Each dictionary case is not tested independently.
- TESTS / Changed Utils BasicAPITests not to inherit from APITestCase, so it is not considered in tests.
- Orders / Set up specific url names for order views: 
  'order-create' for nested module list view (full name: 'modules-order-create')
  'order-detail' for nested classes instance view (full name: 'classes-order-detail')
- Orders / List and Create views converted back into separated view - Orders.
  There is no need of nesting it into the modules list view set. At least for now.
  Minor changes to the OrdersSerializer - added plans' fields.
- Tests / Changed Utils BaseAPITests:
  Changed basename into list_view_name and detail_view_name to be able to split these for Order tests.
  Created additional properties: obj_parent_url_kwargs and obj_parent_get_kwargs for proper getting OneToOne relation instance.
  Created get_obj_with_parent_kwargs decorator for get_obj and get_obj_by_pk methods.

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

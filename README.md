# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###29/01/2020

- Plans / Nested Plans into Orders. 
  Added hyper-link to Orders serializer and nested plans serializer in it.
  Changed Plans serializer, url router and view to provide information regarding parent order.
  Minor change for Plans model - changed classes FK field into order FK field. 
  Classes are going to get its own nested plans soon enough.
  Changed serializer and view names to correspond relation more.

### To be done:

- Implement additional models: Orders! - more like change Plans to Orders and than implement Plans properly
- Implement custom filters, sorting or search
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save 
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Plan constructor view - managing available employees (pensum limit not reached) and not full classes 
  (classes hours not exceeded)
- Errors output for nested JSON data import

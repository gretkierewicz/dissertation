# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###23/01/2020

- Minor changes (Back to abbreviation str representation for Employee model - it caused some troubles with nested 
  auto-URL creation.
  Removed not used code anymore after ParentFromURLHiddenField update)
- Minor ParentFromURLHiddenField name (now GetParentHiddenField) and note change
- Refactoring Tests (help: https://www.b-list.org/weblog/2007/nov/04/working-models/)

### To be done:

- Implement additional models: Orders!
- Implement custom filters, sorting or search
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save 
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Additional views with no nesting (could be problematic with a huge amount of plans or modules)
- Plan constructor view - managing available employees (pensum limit not reached) and not full classes 
  (classes hours not exceeded)
- Errors output for nested JSON data import

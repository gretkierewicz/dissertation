# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###10/02/2020

- Syllabus (late update note):
  Serializers without model - need to set up fields manually.\
  If field matches the one from data - it is forwarded.\
  If there is no match or fields name should be different:
  - update data inside .to_internal_value() method in case of providing data kwarg to serializer
  - update instance's data inside .to_representation() if queryset or instance is provided to serializer

  POST'ing department and academic_year only to make reading study plans easier (no spam of links, just one redirection)\
  Slugs at syllabus are made in a way that providing department, year and slug will get only one study programme.
- Utils / update for GetParentHiddenField - now ParentsHiddenField.
  Removed kwarg: parent_lookup. There is no need of providing it as it should be pointed with field's name.
  Added condition to check if parent's instance is present in provided queryset.
- Syllabus - small update to serializers and views

### To be done:

- Implement custom filters, sorting or search
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save 
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Errors output for nested JSON data import
- Tests

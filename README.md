# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###11/01/2020

- Change Module table to be compatible with Syllabus
  big update of model, serializer and view (https://syllabuskrk.agh.edu.pl/2017-2018/magnesite/api/faculties/wimir/study_plans/stacjonarne-mechanika-i-budowa-maszyn)

Rejected:

- Due to https://www.django-rest-framework.org/api-guide/fields/ check possibility of Integer Field and min_value
  **(it is same as created validator)**

### To be done:

- Implement additional models
- Implement filters, sorting or search
- Add messages/errors
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save supervisors to it (so employees added from list could be set as supervisors for previously added employees)

# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Last changes
###15/12/2020

- Added links for back-reference fields to all serializers
- Changed lookup_field for all views to be more user friendly
- Making corrections to tests because of lookup_field change and added back-reference
- FIX to the csv_files_upload
- FIX - because of polish marks changed back degree and position lookup
- Changed supervisors 'employees' field to 'subordinates' for better readability
- Created Modules model, view and serializer (still needs csv_files_upload action)
- Deleted 'Exam type' table from MySQL scheme - converted to choices (same for semester field)

To be done:

- Rethink use of 'LessonTypes' table - should be choices instead
- Implement additional models
- Implement filters, sorting or search
- Add commentary
- Add messages/errors
- Implement validator for 'abbreviation' excluding polish marks

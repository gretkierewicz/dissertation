### 23/04/2020

- Employees / Added pensum group field. Additional field to serializer and Pensum endpoint added as well.
- Pensum / Refactoring of employee's serializer fields - much more readable
- Pensum / Moved logic from model to serializer and rearranged fields
- Pensum / FIX for factors to filter when at List view
- AGH / JSON data file with additional hours factors based on:
  https://www.cok.agh.edu.pl/fileadmin/_migrated/COK/DUSOS/pliki_pensum_akty_prawne/Regulamin_PRACY_tj..pdf
  chapters 47-54
- Employees / Additional field to be able of setting up part-time job factor
- Pensum / Moving properties back into model (will need them out of serializer too in near future)
  Including part-time factor in calculations
- AGH / Minor cleanup of additional hours' data file

### 19/04/2020

- Pensum / Remove 'employee' field from pensum instance ->
  Additional fields: employee's f_name, l_name, abb, e-mail or any other - all read-only!
- Minor cleanup
- Pensum / Implemented nested serializer to display employee's plans

### 18/04/2020

- Utils / moved constants.py to the AGH module
- Syllabus / Refactoring view + created new serializer to make import of modules easier
- Modules / Modules model changes: new classes names entries and longer name
- Modules / Moved Classes_names into AGH/data
- Cleanup / Pycharm reformatting with import optimize
- Modules / Minor change for classes' display str
- Orders / FIX: classes' list within form is now properly filtered with schedule's slug

### 12/04/2020

- Modules + Syllabus / Making Madules serializer compatible with syllabus data. Changing syllabus serializer to throw
  pure modules list
- Schedule / FIX for a terrible typo - Schedule now inherits from ModelSerializer!

### 10/04/2020

- Plans / Customization of employee's queryset with custom Field
- Utils / FIX for urls without instance + update of employee/supervisor url fields
- Plans / ScheduledEmployeesField minor correction, to use queryset param in exchange for absolute model
- Employee / Exchanging supervisor validation with custom SupervisorField that excludes employee's instance from list
- Pensum / New action for updating value and update of old one
- Module / Minor update for a name of the classes back reference
- Urls / cleanup

### 08/04/2020

- Utils / OneToOneRelationViewSet - new ViewSet to make this relation easier to setup.
- Pensum Reduction / Changed Reduction to be One-to-One relation. Refactored view, model, serializer and url patterns.
- Order - Refactored view set with new utils' class.
- Modules/Order - Moved order url link to parent.
- Modules - Removed action (useless after moving url links)
- Plans - added employee's url field

### 07/04/2020

- Pensum / Added feature to pick role/function based on AGH/AGH/PensumReduction.json file that reduces basic pensum
  value
- URLS / updated comments with generated endpoints

### 05/04/2020

- AGH / Fixed typo with a threshold.
- Employees / removed Pensum model as it has to be nested into the Schedule resource
- Plans / Fixed validation for plan_hours - filtering with schedule slug was missing.
- Pensum / Model rewritten inside Schedule. Added factors that can be manually inserted.

### 04/04/2020

- Syllabus / FIX - putting required=False for nested serializers, as some data in syllabus appear to have empty lists in
  it.
- Schedules - new app for custom schedule creation procedure
- Schedules - minor update
- Schedules - Modules and Orders are no longer independent resources. Moved into schedules as nested ones.

### 10/03/2020

- Pensum / Based
  on: https://www.cok.agh.edu.pl/fileadmin/_migrated/COK/DUSOS/pliki_pensum_akty_prawne/Regulamin_PRACY_tj..pdf
  Created an additional module with AGH data and functions. JSON data to enable easy data manipulation for users in the
  future. Functions to read that JSON data and use within the app.

### 25/02/2020

- Syllabus / requests - throwing out verify=False param. It was unnecessary after all. Wrong data display was caused by
  differences in syllabus API data provided for different years.

### 24/02/2020

- Syllabus - implemented caching for views that get data from external API

### 23/02/2020

- Docker - added empty folder 'static' so docker-compose can run properly after clone
- FIX - fixed module's list view as self.queryset was used and self.get_queryset should be
  (thx to https://www.django-rest-framework.org/api-guide/generic-views/#attributes)

### 22/02/2020

- Containerization with docker-compose and deployment with heroku cloud service for easier updates
- Started project management with Clickup (free + easy github integration)
- FIX / turning off verify for requests GET method (no SSL certificate) as it caused problems with production setup

### 17/02/2020

- settings.py update - much better approach with os.environ for setting environmental variables
- Moved project data into root folder to be more clear with folder tree
- Added basic deploy section

### 10/02/2020

- Syllabus (late update note):
  Serializers without model - need to set up fields manually.\
  If field matches the one from data - it is forwarded.\
  If there is no match or fields name should be different:
    - update data inside .to_internal_value() method in case of providing data kwarg to serializer
    - update instance's data inside .to_representation() if queryset or instance is provided to serializer

  POST'ing department and academic_year only to make reading study plans easier (no spam of links, just one
  redirection)\
  Slugs at syllabus are made in a way that providing department, year and slug will get only one study programme.
- Utils / update for GetParentHiddenField - now ParentsHiddenField. Removed kwarg: parent_lookup. There is no need of
  providing it as it should be pointed with field's name. Added condition to check if parent's instance is present in
  provided queryset.
- Syllabus - small update to serializers and views
- Utils / moved ParentHiddenRelatedField from serializers.py to relations.py

### 09/02/2020

- Minor kwarg name change for GetParentHiddenField
- Modules / added action 'new_order' to classes viewset
- Syllabus - New app and views/serializers to read study programmes
- Syllabus - Added views/serializers to read modules/classes for particular study programme

### 02/02/2020

- Tests / Minor update. Nothing important.

### 01/02/2020

- Making use of NestedViewSetMixin from rest_framework_nested!
  No longer need to override get_queryset method. parent_lookup_kwargs are get from serializer to filter queryset.
- FIX / EmployeeModuleViewSet - inherits from ModelViewSet now (was ModuleViewSet before - 'typo')
- Orders / Detail view - got rid of parent's kwargs raw filtering with help of NestedViewSetMixin.
- Cleanup / Minor cleanup of the code. Nothing important here.
- FIX / Moved modified NestedHyperlinkedIdentityField to utils.relations Updated its code to allow lookup_field=None,
  only passing parent_lookup_kwargs. It simplifies creation of hyper-links for OneToOne relation instances.
- URLS / Minor update. Url patterns for Order detail will now look much better.

### 31/01/2020

- Added plan_sum_hours property to the Order model for future validation purposes. Moved plans-related serializer's
  fields to the nested ClassesOrderSerializer, as there is no use for them in basic one. Basic OrdersSerializer stands
  now only for creating new order from model list view or throwing back form. Could be changed in case of importing
  nested plans' data in orders JSON - needs testing.
- TESTS / Refactoring code - moved some random functions to Utils module
- TESTS / Refactoring code - moved test cases to Utils tests for more clear sharing with other modules
- TESTS / Some additional changes so tests are skipped easier regarding provided data.
- TESTS / Implementing unittests' SubTest
  method (https://docs.python.org/3/library/unittest.html#distinguishing-test-iterations-using-subtests)
  Each dictionary case is not tested independently.
- TESTS / Changed Utils BasicAPITests not to inherit from APITestCase, so it is not considered in tests.
- Orders / Set up specific url names for order views:
  'order-create' for nested module list view (full name: 'modules-order-create')
  'order-detail' for nested classes instance view (full name: 'classes-order-detail')
- Orders / List and Create views converted back into separated view - Orders. There is no need of nesting it into the
  modules list view set. At least for now. Minor changes to the OrdersSerializer - added plans' fields.
- Tests / Changed Utils BaseAPITests:
  Changed basename into list_view_name and detail_view_name to be able to split these for Order tests. Created
  additional properties: obj_parent_url_kwargs and obj_parent_get_kwargs for proper getting OneToOne relation instance.
  Created get_obj_with_parent_kwargs decorator for get_obj and get_obj_by_pk methods.
- Updated decorator to be able to get object's parent after posting order data. Fixed some issues after messing with
  last tests upps. All tests for employees and modules pass now.
- Tests / Basic setup for Orders
- Orders / Created ViewSet for detail view and removed action from modules list view. Changed URL patterns. Order's
  details can be now properly displayed, updated and deleted. Converted basic Order view set into two view sets:
  OrdersList and OrderDetail
- Tests / Minor tests corrections
- Plans / plan_hours validation - preventing setting more hours than order's calculated value
- Orders / Updated PUT method - It will now create or update record from Classes' nested detail view.

### 30/01/2020

- Added action to create Orders from Module list view. Added a filter so form includes now only classes without order.
- Orders / deleted main URL. Creating only possible from module list view now. /order/ - added as an action in the
  Classes ViewSet, for now only with GET method. Utils / Created variation of NestedHyperlinkedIdentityField with
  prefix: AdvLookup. It allows passing a lookup with double underscore to point nested attributes of instance. Plans are
  now available from orders view - nested in Classes aswell.
- Orders / Added PUT PATCH and DELETE methods to the 'order' action nested in Classes Instance View. Small update of
  ClassesOrderSerializer - URL kwarg for Classes changed to 'name'.

### 29/01/2020

- Plans / Nested Plans into Orders. Added hyper-link to Orders serializer and nested plans serializer in it. Changed
  Plans serializer, url router and view to provide information regarding parent order. Minor change for Plans model -
  changed classes FK field into order FK field. Classes are going to get its own nested plans soon enough. Changed
  serializer and view names to correspond relation more.
- Orders / Nested orders into Classes. Converted most of the Orders main serializer hyper-links into nested form.
  Created Orders serializer for nesting into Classes (derivative of main Orders serializer). Added url routes nested in
  classes ones.

### 28/01/2020

- Orders / Changing classes_pk field into nested hyper-link related field for better readability
- Classes / Added students_limit_per_group field. For now manual input per classes instance.
- Orders / Changed classes FK field for OneToOneField and added unique validator to the serializer
- Orders / Added properties: groups_number and order_hours
- Plans / Created basic Plans model, view and serializer

### 27/01/2020

- Plans / deleting model for now - will be moved to new app wiGth future Orders model
- Orders - new app for orders and setting employee-plan setups
- Orders / Implementing simple Orders model, view and serializer (changed Classes model str representation and ordering
  for better readability in Orders' forms)

### 26/01/2020

- Tests / Pensum tests corrections; EmpFields class added for later use in Modules tests
- Tests / Basic tests for Modules view
- FIX / Pensum tests fixed (100% passing now)

### 25/01/2020

- Refactoring Tests
- Urls / minor namespace changes
- Tests / additional kwargs in test for future scenarios tests
- FIX / Employee serializier Supervisor validation for PATCH method
- Tests / Basic tests for Pensum View
- FIX / Pensum limit and value validators

### 24/01/2020

- Refactoring Tests

### 23/01/2020

- Minor changes (Back to abbreviation str representation for Employee model - it caused some troubles with nested
  auto-URL creation. Removed not used code anymore after ParentFromURLHiddenField update)
- Minor ParentFromURLHiddenField name (now GetParentHiddenField) and note change
- Refactoring Tests (help: https://www.b-list.org/weblog/2007/nov/04/working-models/)

### 22/01/2020

- Minor updated to models
- Pensum model update - additional field for scholarship, doctoral procedure and years
- Pensum validation and model update. Lowering number of choices for year condition to minimize possibilities of
  covering same year ranges.
- Rearranging tests and basic objects
- Employee model update - pensum finding property
- FIX / Module csv_files_upload will now properly delete existing classes instances and read number from classes hours
  columns (regex implemented)
- Module ViewSet retrieve method minor update with help of get_object method (based
  on https://medium.com/profil-software-blog/10-things-you-need-to-know-to-effectively-use-django-rest-framework-7db7728910e0)
- Implemented nested JSON data import for Modules/Classes/Plans (no error output for now)
- FIX / Employees __str__ method - had to get back for simple version (wrong url auto-creation for
  modules/classes/plans)

### 21/01/2020

- Employee / Additional booleans for pensum thresholds
- Classes / Additional boolean for filling all classes' hours
- Minor naming and field configuration changes
- Module Serializers minor changes to fields
- CSV rendering only for chosen Views: Employees, Degrees, Positions, Modules(with classes)
- Created new Module model properties for CSV rendering and Flat Serializer
- Created Module View action: csv_files_upload that reads rendered CSV format

### 20/01/2020

- FIX / Plans Serializer validation for employee's pensum limit will now work with PATCH method correctly
- Utils / Exchanged conv_pk_to_str function for SlugRelatedField
- FIX / Employee Renderer - after using SlugRelatedField update
- Employee csv_upload_files action rewritten
- Creating new utility - read_csv_files, and using it with Employees, Degrees and Positions ViewSets
- TESTS / update

### 19/01/2020

- TESTS / Modules basic tests
- TESTS / Classes basic tests + some minor update
- TESTS / Plans basic tests

### 18/01/2020

- Correction to value validation - removed custom validator, min value set with extra_kwargs
- Small fix for pensum validation (still needs correction for PATCH method)
- TESTS / employees app test re-written (all pass for now)
- TESTS / Pensum basic tests
- FIX / Pensum validation of unique degrees and positions entries
- FIX / Pensum validation of value < limit
- TESTS / Minor update - permanently delete resource request should return HTTP 204

### 17/01/2020

- Implementing the latest project version to the http://gret.ct8.pl
- Implementing Employee's nested Modules view and serializer properly
- Modules / Employee-Module Serializer - minor corrections (changed related name to supervised_modules)
- Plan model - changed methods to properties, so these can be easily used in serializers
- Employee's Plans - implemented View and Serializers (read-only)
- FIX / For Plan Serializer's validation after changing model's methods to props
- Added to Employee: pensum, limit and sum of plan_hours
- Validation for plan's hours checking if employee's pensum limit would be exceeded
- FIX / Plan ViewSet - get_object method uses get_object_or_404 now
- Validator for pensum limit - should be always greater than pensum value
- Minor update - ordering in models, changing filter method to get_object_or_404 function

### 15/01/2020

- Cleanup - minor changes in serializers/views
- Created conv_pk_to_str function for easy to_representation config
- Validation on the Pensum serializer - don't allow double match-ups of degree and position
- Model changes - employee's degree and position cannot be null; Pensum.pensum changed to Pensum.value
- Serializers (employee and pensum) update - ordering and field name
- Created validator for plan's hours field - value > 0 and sum of all plans cannot exceed classes hours
- Classes serializer - new field: hours_to_set
- New methods in Classes model. Update for Plan's validator and Classes field

### 14/01/2020

- Update on the ct8 server
- Implementing Plans model, view and serializer - nested view in Classes (and Classes is a nested view in Modules)
- Code cleanup
- Creating new app: Modules - moved modules related elements into
- FIX / test's failure fix: employees degree and position hyperlinks custom config
- Minor view name change for better readability

### 12/01/2020

- Classes / Serializer - validation of the unique_together option with new type of HiddenField
- FIX / validation of positive values
- Pensum - creating basic model, view and serializer
- Pensum - adding limit field + some corrections
- Serializers - cleanup
- ParentFromURLHiddenField - changing how lookup kwarg is acquired

### 11/01/2020

- Change Module table to be compatible with Syllabus big update of model, serializer and
  view (https://syllabuskrk.agh.edu.pl/2017-2018/magnesite/api/faculties/wimir/study_plans/stacjonarne-mechanika-i-budowa-maszyn)
- Changed '\_\_all__' to list in the serializers Meta fields for better control over API views
  (control over sequence of fields - Module serializer for now)
- Order serializer - changed back-ref name in Module model to 'form_of_classes'
- Module serializer/view - simplified: only one serializer with full data and orders' list
- Orders model - altering names of fields: 'lesson_type' and 'hours' to 'name' and 'classes_hours' respectively Need of
  manual corrections to migration file. Changed to:
  > migrations.RenameField(\
  > model_name='orders',\
  > old_name='lesson_type',\
  > new_name='name',\
  > ),
- Orders serializers/view update - now properly reached from Module's nested serializer
  (allows use of /modules/{module_code}/classes/{order_name})
- Renaming 'Orders' model to 'Classes' and cleaning comments
- FIX - Getting back supervisor field for Module model
- Changed Employees to API url part
- Update for the MODEL workbench
- Classes / minor change for url (/class/ -> /classes/)
- Classes big update - now accessed only from Module view

Rejected:

- Due to https://www.django-rest-framework.org/api-guide/fields/ check possibility of Integer Field and min_value
  **(it is same as created validator)**

### 29/12/2020

- FIX / OrderShortSerializer minor update for better readability
- MODELS / Update of CHOICES fields - for better readability of links
- Orders / Moved query from 'retrieve' method to 'get_object' - it will be common for all detail-view methods
- URLS / Update of path for OrderViewSet, so it includes all methods
- MODELS / Update of 'slug' field type: employee.abbreviation and module.code
- FIX / supervisor validator for csv upload

### 28/12/2020

- Employees / Orders list - using short serializer now, added order_by
- FIX / order_by() and filter() do not need all() method to be used first

### 20/12/2020

- FIX - Employees list view will now send full data with CSV format
- Added output with messages to the employees/csv_files_upload action. Now it displays records' Errors, Updated/Created
  successfully and No action (by the e_mail)

### 19/12/2020

- FIX - Forgot about proper filtering of modules nested into employees view
- Update - url's routers commentary and minor update for Order's retrieve function parameter
- Deleted OrderHyperlink class - not used
- Created some comments for serializers and views
- Changed Module list view to simple one

### 17/12/2020

- Customization of Degrees list view by adding new serializer (less information in list - more in detail)
- Extending customization to Positions and Employees lists
- Correction to tests for Degrees, Positions, Employees
- Minor cleanup in urls before using nested routers
- Changing naming of some serializer for better readability
- Creating first nested hyperlink employee-modules (yet no link for nested module instance, but possible to view it)
- Moving ordering to list methods for proper display

### 16/12/2020

- Reshaping MySQL scheme - deleting 'Lesson Type' - will do it with choices
- Created Orders model, serializer and view (View for list, post and request one record for now)
- Some fun with nested serializers - for now only for read_only fields

### 15/12/2020

- Added links for back-reference fields to all serializers
- Changed lookup_field for all views to be more user friendly
- Making corrections to tests because of lookup_field change and added back-reference
- FIX to the csv_files_upload
- FIX - because of polish marks changed back degree and position lookup
- Changed supervisors 'employees' field to 'subordinates' for better readability
- Created Modules model, view and serializer (still needs csv_files_upload action)
- Deleted 'Exam type' table from MySQL scheme - converted to choices (same for semester field)

### 13/12/2020

- Corrections after deploying at ct8.pl
- Running app at http://gret.ct8.pl/ with use of MySQL (possible future tests with PostgreSQL/MongoDB)
- Tests for Employees model, view and serializer
- Tests for Positions model, view and serializer - 1 Fail - delete still possible
- FIX - delete not possible at Position view
- FIX - sending empty 'year_of_studies' field was causing error because of SQLite correction
- Major refactoring TESTs, after adding supervisor self relation test - bug was found
- FIX - employee cannot be it's supervisor anymore - it would be better to exclude employee's abbreviation from form's
  list too

### 10/12/2020

- Writing first unit test - DegreeSerializer / list all
- Writing tests for all methods (https://restfulapi.net/http-methods/)

### 09/12/2020

- Supervisor validation - FIX

### 08/12/2020

- Changed naming from bulk_upload to csv_files_upload because function should only accept files in such format
- Correction for employees/csv_files_upload - PUT will only update existing entries and ignore new
- Created validator for year_of_studies - serializer did not recognize field type properly

### 07/12/2020

- Minor fix for allowing empty supervisor form field
- Added EmployeeRenderer class for even better CSV export labels
- Created additional option - bulk upload - allowing sending CSV file(s) with some validation. \
  POST method for sending new values (existing entries with unique field will not be updated) \
  PUT method for updating existing entries and creating new as well \
  Validation for Employees model because of related fields
- Making example of disallowing DELETE method from view (DegreesViewSet)
- Big cleanup of not used files and entries

### 06/12/2020

- Adding repr fields for
  EmployeeSerializer (https://blog.ridmik.com/a-cleaner-alternative-to-serializermethodfield-in-django/)
- Allowing GET method with format set to CSV - globally
- Manipulation of csv fields with get_renderer_context method overwrite - for better readability of file

### 04/12/2020

- Added custom validator for Supervisor field - no more self referencing!
- pip install djangorestframework-csv

### 03/12/2020

- Going for pure REST Api, cleaning most of the unused code
- Minor customization of the Form's fields

### 29/11/2020

- First steps in the Django REST framework with help
  of https://medium.com/swlh/build-your-first-rest-api-with-django-rest-framework-e394e39a482c
- Creating basic serializers and views for REST API - all tables included now

### 27/11/2020

- Added can_delete_records flag for each table (in views for now)
- Delete view now responds to the POST method - need to update for DELETE later ###26/11/2020

- Renamed 'columns' to column_headers for better readability

### 25/11/2020

- Changing import procedure - will need messages to give feedback about failed records and such
- Eliminating creation of empty string entries in the Degrees and Positions tables
- Messages about statuses - edited properly deleted and so on
- Updated import procedure for employees model - more validation of data###18/11/2020

- Creating new file-importing-form and view for managing the file
- Managing importing data on model level

### 17/11/2020

- Added Employees table
- Some minor customization of displayed tables
- Inserted UNIQUE property for e_mail column in Employees table
- CSV Export option

### 16/11/2020

- Building basic views and forms for show/create new/edit/delete functions
- Refactoring code for better usability when working with many tables
- Building universal views for any kind of a table
- More corrections to the code, so any table can be handled

### 14/11/2020

- Changed how data is displayed. Preparation for including forms.

### 12/11/2020

- Changed name of app "Employees_Management" into "employees"
- Made basic employees' Models: Degrees and Positions
- Prepared migrations, checking SQL format and migrating models to the DB
  > python manage.py makemigrations\
  python manage.py sqlmigrate employees 0001 python manage.py migrate
- Checked tables with python shell
  > python manage.py shell
- Added some records with help of the shell
  > from employees.models import Degrees, Positions\
  d = Degrees(name='prof.')\
  d.save()\
  p = Positions(name='adiunkt')\
  p.save()\
  quit()
- Changed index.html for now to display full list of records

### 11/11/2020

- Added Subcontracts table - forget about it in the first version of the MySQL Workbench model
- Created Salaries table from money related column in the Employees table.
- Installation of Django module (Django v3.1.3)
  > python -m pip install Django
- Creating requirements file
  > python -m pip freeze > requirements.txt
- Creating main Django project
  > django-admin startproject Load_Planning_Project
- Checked created project with running local server and going to http://127.0.0.1:8000/
  > python Load_Planning_Project/manage.py runserver
- Created new Django app - Employees_Management
  > cd Load_Planning_Project\
  python manage.py startapp Employees_Management
- Created some basic view for the main project (division for menu and 'body' sections)
- Created basic view for Employees_Management app and added link for it in base page

### 08/11/2020

- Moved DB model to the MySQL Workbench (Because of trail restrictions of app.dbdesigner.net)
- Major changes to the model - actually that one was in about 50% made from scratch.
- Inserted One-To-One table: Fees. Inserted Many-To-Many tables: Orders, Plans.
- Divided model into 3 areas: Employees related tables, Plans related tables and Institutions related tables.

**Detailed description:**

1. Sheet "Konfiguracja"

- Columns A-E divided into tables:
    - Degrees - Unique Name column, ID is a FK for Employees table -> 2.
    - Limits - Unique Name column
    - Fees - One-To-One relation with Degrees table
- Columns G-J put into Overtimes table:
    - Overtimes - Unique Reason column

2. Sheet "Pracownicy"

- Rows 2-7 moved to the Subcontracts table (Many-To-Many Structures table in Institution section -> 4.)
- Rows 9+ moved to the Employees table.
    - Column F (Stanowisko) moved into seperated table: Positions
    - After normalization - get money related columns out of this table

3. Sheet "Moduły"

- Columns B-F + N moved to the Modules table. The rest - some moved to the Orders table (4.) plus some minor tables.
    - Modules - main table that keeps only module related data
    - LessonTypes table - keeps division to Lab/Lecture/Project and so on
    - ExamTypes table - keeps division to none/Oral/Written
    - Used FK from Structures table -> 4. as it seems that Structures are connected to the modules, not orders

4. Sheet "Zlecenia"

- Created Many-To-Many table Orders, put data from some columns in separated tables
    - Orders - main table that keeps only order related data
      (Number of hours moved from 3. here = automatic creation of "pre-defined" Orders in case of new Module coming out|
      Number_of_groups is calculated from Number_of_students and some Limits, but for now it is possible to put some
      other value here as well)
    - OrderCodes - keeps track of Order Codes from H column (Nr zlecenia)
    - Institution section created: tables StructureTypes, Structures -> 3.

5. Sheet "Prowadzący-Plan"

- Plans - Many-To-Many table with 3 FKs: Employee_ID, Module_ID and LessonType_ID.
    - Only with additional columns: Number_of_hours and Editor_ID
    - K column from sheet not relevant as it is defined in Modules table

### 20/11/2020

- Creating basic model of the DB https://app.dbdesigner.net/designer/schema/364137
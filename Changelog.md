###13/12/2020

- Corrections after deploying at ct8.pl
- Running app at http://gret.ct8.pl/ with use of MySQL (possible future tests with PostgreSQL/MongoDB)
- Tests for Employees model, view and serializer
- Tests for Positions model, view and serializer - 1 Fail - delete still possible
- FIX - delete not possible at Position view
- FIX - sending empty 'year_of_studies' field was causing error because of SQLite correction
- Major refactoring TESTs, after adding supervisor self relation test - bug was found
- FIX - employee cannot be it's supervisor anymore - it would be better to exclude employee's abbreviation from form's list too

###10/12/2020

- Writing first unit test - DegreeSerializer / list all
- Writing tests for all methods (https://restfulapi.net/http-methods/)

###09/12/2020

- Supervisor validation - FIX 

###08/12/2020

- Changed naming from bulk_upload to csv_files_upload because function should only accept files in such format
- Correction for employees/csv_files_upload - PUT will only update existing entries and ignore new
- Created validator for year_of_studies - serializer did not recognize field type properly

###07/12/2020

- Minor fix for allowing empty supervisor form field
- Added EmployeeRenderer class for even better CSV export labels
- Created additional option - bulk upload - allowing sending CSV file(s) with some validation. \
    POST method for sending new values (existing entries with unique field will not be updated) \
    PUT method for updating existing entries and creating new as well \
    Validation for Employees model because of related fields
- Making example of disallowing DELETE method from view (DegreesViewSet)
- Big cleanup of not used files and entries

###06/12/2020

- Adding repr fields for EmployeeSerializer (https://blog.ridmik.com/a-cleaner-alternative-to-serializermethodfield-in-django/)
- Allowing GET method with format set to CSV - globally
- Manipulation of csv fields with get_renderer_context method overwrite - for better readability of file

###04/12/2020

- Added custom validator for Supervisor field - no more self referencing!
- pip install djangorestframework-csv

###03/12/2020

- Going for pure REST Api, cleaning most of the unused code
- Minor customization of the Form's fields

###29/11/2020

- First steps in the Django REST framework with help of https://medium.com/swlh/build-your-first-rest-api-with-django-rest-framework-e394e39a482c
- Creating basic serializers and views for REST API - all tables included now

###27/11/2020

- Added can_delete_records flag for each table (in views for now)
- Delete view now responds to the POST method - need to update for DELETE later ###26/11/2020

- Renamed 'columns' to column_headers for better readability

###25/11/2020

- Changing import procedure - will need messages to give feedback about failed records and such
- Eliminating creation of empty string entries in the Degrees and Positions tables
- Messages about statuses - edited properly deleted and so on
- Updated import procedure for employees model - more validation of data###18/11/2020

- Creating new file-importing-form and view for managing the file
- Managing importing data on model level

###17/11/2020

- Added Employees table
- Some minor customization of displayed tables
- Inserted UNIQUE property for e_mail column in Employees table
- CSV Export option

###16/11/2020

- Building basic views and forms for show/create new/edit/delete functions
- Refactoring code for better usability when working with many tables
- Building universal views for any kind of a table
- More corrections to the code, so any table can be handled 

###14/11/2020

- Changed how data is displayed. Preparation for including forms.

###12/11/2020

- Changed name of app "Employees_Management" into "employees"
- Made basic employees' Models: Degrees and Positions
- Prepared migrations, checking SQL format and migrating models to the DB
    > python manage.py makemigrations\
    python manage.py sqlmigrate employees 0001
    python manage.py migrate
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

###11/11/2020

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

###08/11/2020

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
    Number_of_groups is calculated from Number_of_students and some Limits, 
    but for now it is possible to put some other value here as well)
    - OrderCodes - keeps track of Order Codes from H column (Nr zlecenia)
    - Institution section created: tables StructureTypes, Structures -> 3.

5. Sheet "Prowadzący-Plan"
 - Plans - Many-To-Many table with 3 FKs: Employee_ID, Module_ID and LessonType_ID.
    - Only with additional columns: Number_of_hours and Editor_ID
    - K column from sheet not relevant as it is defined in Modules table 

###20/11/2020
- Creating basic model of the DB https://app.dbdesigner.net/designer/schema/364137
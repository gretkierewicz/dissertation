# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

For now it will be local only, with SQLite DB.

## Last changes
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

**ToDo List:**
- In Employees table - is Position_ID related to the Degree_ID and not to the Employee_ID (3NF possibly violated)?
- Is future salary table dependant on the Position/Degree or is it unique for each Employee?



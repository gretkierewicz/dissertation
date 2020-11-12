# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

For now it will be local only, with SQLite DB.

## Last changes
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

# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

For now it will be local only, with SQLite DB.

## Last changes
###12/11/2020

- Making basic Models: Degrees and Positions
- Preparing migrations, checking SQL format and migrating models to the DB
    > python manage.py makemigrations\
    python manage.py sqlmigrate Employees_Management 0001
    python manage.py migrate
    - Output for the SQL: 
        > CREATE TABLE "Employees_Management_degrees" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(45) NOT NULL);\
        CREATE TABLE "Employees_Management_positions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(45) NOT NULL);\


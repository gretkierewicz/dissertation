# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

Heroku deploy: http://shielded-ocean-48265.herokuapp.com (PostgreSQL)

~~http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB~~

## Deployment

```bash
# create folder for project
mkdir root_folder
cd root_folder

# get copy of the application's files
git clone https://github.com/gretkierewicz/dissertation.git .

# build app with docker-compose
docker-compose build

# login with heroku and create app for deployment
heroku login
heroku create
# login to container
heroku container:login

# create postgresql DB (this creates DATABASE_URL env variable as well)
heroku addons:create heroku-postgresql:hobby-dev

# push and release container
heroku container:push web
heroku container:release web

# create DB tables for cars app
heroku run python manage.py migrate

# start app in web-browser
heroku open
```

## Last changes

### 25/04/2020

- Pensum / Property name change from pensum_hours_from_plan to pensum_contact_hours
- Pensum / Added property pensum_additional_hours
- Modules / Removing csv import as it is much more convenient to import data with JSON files (easily nested data)
- Employees / Refactor of csv import actions descriptions
- AGH / Added custom entry for additional hours to the JSON data file + migration
- Pensum / Added nested Exams Additional Hours model, serializer and view
- Exams Additional Hours / Added validation for portion field (0-1 range)
- Exams Additional Hours / Added fields corresponding to model's fields
- Exams Additional Hours / Excluding modules to pick with no order set
- Exams Additional Hours / Added field with student's number (to check for proper value for calculating additional hours)

### To be done:

Major
- Calculating exams within additional hours
- Setting up limits, pensum value and filters for employees possible to choose for plans/etc

Minor
- Implement custom filters, sorting or search
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Errors output for nested JSON data import
- Tests

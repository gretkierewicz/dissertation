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

### 24/04/2020

- Syllabus / Added language to data provided with Study Programme Import View
- Modules / Added language field
- Pensum / Minor refactor of plan's hours property
- Pensum Additional Hours Factors / Added basic model, view and serializer - need to correct name of basic factors asap
- Pensum Factors renamed to Pensum Basic Threshold Factors
- Pensum Basic Factors / FIX in recalculating threshold value
- Pensum / Serializer's fields rearrangement
- Pensum Additional Hours Factors / Added validation for value per unit and amount
- Cleanup

### To be done:

Major
- Calculating additional and non-contact hours
- Setting up limits, pensum value and filters for employees possible to choose for plans/etc

Minor
- Implement custom filters, sorting or search
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Errors output for nested JSON data import
- Tests

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

## Project management

https://share.clickup.com/b/h/4-8723336-2/4c4ffb879de82e8

## Last changes
###23/02/2020

- Docker - added empty folder 'static' so docker-compose can run properly after clone
- FIX - fixed module's list view as self.queryset was used and self.get_queryset should be 
  (thx to https://www.django-rest-framework.org/api-guide/generic-views/#attributes)

### To be done:

- Implement custom filters, sorting or search
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save 
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Errors output for nested JSON data import
- Tests

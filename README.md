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

### 23/04/2020

- Employees / Added pensum group field. Additional field to serializer and Pensum endpoint added as well.
- Pensum / Refactoring of employee's serializer fields - much more readable
- Pensum / Moved logic from model to serializer and rearranged fields
- Pensum / FIX for factors to filter when at List view
- AGH / JSON data file with additional hours factors based on: 
  https://www.cok.agh.edu.pl/fileadmin/_migrated/COK/DUSOS/pliki_pensum_akty_prawne/Regulamin_PRACY_tj..pdf
  chapters 47-54
- Employees / Additional field to be able of setting up part-time job factor

### To be done:

Major
- Calculating additional and non-contact hours
- Getting language of each module for modifying hours factor before adding into pensum
- Setting up limits and pensum value and filters for employees possible to choose for plans/etc

Minor
- Implement custom filters, sorting or search
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Errors output for nested JSON data import
- Tests

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

### 05/05/2020

- Cleanup in additional hours factors JSON file
- Update for model schema
- New flag for § 54 ust. 13 - additional hours not counted into limits ("Do maksymalnego dopuszczalnego wymiaru godzin 
  ponadwymiarowych, o którym mowa w zdaniu pierwszym, nie uwzględnia się godzin, o których mowa w 
  § 52 ust. 2 pkt 1 lit. a (tj. z tytułu opieki nad pracą dyplomową)")
  Update for AdditionalHoursFactorData class
- PensumAdditionalHoursFactorsSerializer / refactoring methods
- Pensum model / new property - pensum_additional_horus_not_counted_into_limit + serializer update
- README and minor additional hours factors JSON file update

### To be done:

Major
- Implement factors: deficits for contact hours and job-time hours limits
- Filters for employees possible to choose for plans/etc

Minor
- Implement custom filters, sorting or search
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Errors output for nested JSON data import
- Tests

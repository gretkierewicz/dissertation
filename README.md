# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project developed with **Python v3.8.6** (changed from Python v3.6.7)

## Test-site

http://gret.ct8.pl/ with MySQL DB\
Local with SQLite DB

## Deploy

```bash
# create folder for project
mkdir root_folder
cd root_folder

# get copy of the application's files
git clone https://github.com/gretkierewicz/dissertation.git .

# install dependencies
python -m pip install -r requirements.txt

# create all migrations files
python manage.py makemigrations
# run migrations
python manage.py migrate

# collect statics for apps
python manage.py collectstatic

# run project (for local/test)
python manage.py runserver
```

## Last changes
###17/02/2020

- settings.py update - much better approach with os.environ for setting environmental variables
- Moved project data into root folder to be more clear with folder tree
- Added basic deploy section

### To be done:

- Implement custom filters, sorting or search
- Custom query-sets for forms (if possible)
- Change upload CSV files method for employees - it should first create employees without supervisors, and then save 
  supervisors to it (so employees added from list could be set as supervisors for previously added employees)
- Errors output for nested JSON data import
- Tests

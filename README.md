# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.\
Project created with **Python v3.6.7**

## Test-site

For now it will be local only, with SQLite DB.

## Last changes
###06/12/2020

- Adding repr fields for EmployeeSerializer (https://blog.ridmik.com/a-cleaner-alternative-to-serializermethodfield-in-django/)
- Allowing GET method with format set to CSV - globally
- Manipulation of csv fields with get_renderer_context method overwrite - for better readability of file

To be done:

- Implement CSV import
- Implement TESTS!
- Implement additional models

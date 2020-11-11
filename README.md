# Dissertation work

The use of the Django framework for the purpose of supporting the KRIM teaching load planning.

## Test-site

For now local only, with SQLite DB.

## Changelog

* **11/11/2020**

**To check:** 

In Employees table - is Position_ID related to the Degree_ID and not to the Employee_ID (3NF possibly violated)

Is future salary table dependant on the Position/Degree or is unique for each Employee?


* **08/11/2020**

Moved DB model to the MySQL Workbench (Because of trail restrictions of app.dbdesigner.net)

Major changes to the model - actually that one was in about 50% made from scratch.

Inserted One-To-One table: Fees. Inserted Many-To-Many tables: Orders, Plans.

Divided model into 3 areas: Employees related tables, Plans related tables and Institutions related tables.

**ToDo List:**

Extract data about money from Employees table - that will allow for the better access division in the future.

Check the tables for (at least) 3NF.

Theoretically (byt the provided excel file) Editor_ID in Plans table depends on the Employee and the Order number, but not on the Lesson Type.
To be checked if that is correct. 

**Detailed description:**

* **20/11/2020**

Creating basic model of the DB https://app.dbdesigner.net/designer/schema/364137


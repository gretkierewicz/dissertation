##08/11/2020

- Moved DB model to the MySQL Workbench (Because of trail restrictions of app.dbdesigner.net)
- Major changes to the model - actually that one was in about 50% made from scratch.
- Inserted One-To-One table: Fees. Inserted Many-To-Many tables: Orders, Plans.
- Divided model into 3 areas: Employees related tables, Plans related tables and Institutions related tables.

**Detailed description:**

1. Sheet "Konfiguracja"
 - Columns A-E divided into tables: 
    - Degrees - Unique Name column, ID is a FK for Employees table -> 2.
    - Limits - Unique Name column
    - Fees - One-To-One relation with Degrees table
 - Columns G-J put into Overtimes table:
    - Overtimes - Unique Reason column
    
2. Sheet "Pracownicy"
 - Rows 2-7 moved to the Subcontracts table (Many-To-Many Structures table in Institution section -> 4.)
 - Rows 9+ moved to the Employees table. 
    - Column F (Stanowisko) moved into seperated table: Positions
    - After normalization - get money related columns out of this table

3. Sheet "Moduły"
 - Columns B-F + N moved to the Modules table. The rest - some moved to the Orders table (4.) plus some minor tables.
    - Modules - main table that keeps only module related data
    - LessonTypes table - keeps division to Lab/Lecture/Project and so on
    - ExamTypes table - keeps division to none/Oral/Written
    - Used FK from Structures table -> 4. as it seems that Structures are connected to the modules, not orders

4. Sheet "Zlecenia"
 - Created Many-To-Many table Orders, put data from some columns in separated tables
    - Orders - main table that keeps only order related data 
    (Number of hours moved from 3. here = automatic creation of "pre-defined" Orders in case of new Module coming out| 
    Number_of_groups is calculated from Number_of_students and some Limits, 
    but for now it is possible to put some other value here as well)
    - OrderCodes - keeps track of Order Codes from H column (Nr zlecenia)
    - Institution section created: tables StructureTypes, Structures -> 3.

5. Sheet "Prowadzący-Plan"
 - Plans - Many-To-Many table with 3 FKs: Employee_ID, Module_ID and LessonType_ID.
    - Only with additional columns: Number_of_hours and Editor_ID
    - K column from sheet not relevant as it is defined in Modules table 

**ToDo List:**
- Extract data about money from Employees table - that will allow for the better access division in the future.
- Check the tables for (at least) 3NF.
- Theoretically (by the provided excel file) Editor_ID in Plans table depends on the Employee and the Order number, but not on the Lesson Type.
To be checked if that is correct. 

##20/11/2020
- Creating basic model of the DB https://app.dbdesigner.net/designer/schema/364137
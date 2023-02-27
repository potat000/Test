# customer enrollment using generated sql code
## Adding the tool:
---
### 1. copy contents of `enroll_db.sh`
refer to `enroll_db.sh` in this same folder

### 2. create new file
paste into `enroll_db` inside `tools` directory
```shell
$ mkdir $HOME/tools
$ nano $HOME/tools/enroll_db # opens nano, paste in nano
```
### 3. change permissions
```shell
$ chmod u+x $HOME/tools/enroll_db
```

#### 3.1 add to path (optional)
```shell
$ export PATH="$HOME/tools:$PATH" # temporary
$ echo 'export PATH="$HOME/tools:$PATH"' >> ~/.bashrc # permanent
```

# using `enroll_db` script
```shell
$ $HOME/tools/enroll_db -n CUSTOMERNAME -p p4ssw0rd123 # for temporary
$ enroll_db -n CUSTOMERNAME -p p4ssw0rd123 # for permanent
```

## output enroll.sql file:
```sql
CREATE DATABASE CUSTOMERNAME_db;

CREATE USER 'CUSTOMERNAME_admin'@'localhost' IDENTIFIED BY 'p4ssw0rd123';
CREATE USER 'CUSTOMERNAME_admin'@'%' IDENTIFIED BY 'p4ssw0rd123';

GRANT ALL PRIVILEGES ON CUSTOMERNAME_db.* TO 'CUSTOMERNAME_admin'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON CUSTOMERNAME_db.* TO 'CUSTOMERNAME_admin'@'%' WITH GRANT OPTION;


FLUSH PRIVILEGES;
```
# Run sql script
### this will create a database, and grant privileges of the user on that database (and test database if specified)
```shell
$ mysql -u mysqladmin -p -h evcoprodmysql01.mysql.database.azure.com --ssl-mode=REQUIRED < enroll.sql
```
# thats it!
you've enrolled a customer and created a db for them. remember to migrate before starting the django application service.


# optional: using `enroll_db` <b>with '-t' flag:</b>
when `python manage.py testall` runs tests, the application will try to create an exact replica of the database with `test_` appended to the front of the db. Therefore for staging/testing where we run `python manage.py test*` functions, we'll need extra permissions from the MySQL server.

```shell
$ $HOME/tools/enroll_db -n CUSTOMERNAME -p p4ssw0rd123 -t # for temporary
$ enroll_db -n CUSTOMERNAME -p p4ssw0rd123 -t # for permanent
```
```sql
CREATE DATABASE CUSTOMERNAME_db;

CREATE USER 'CUSTOMERNAME_admin'@'localhost' IDENTIFIED BY 'p4ssw0rd123';
CREATE USER 'CUSTOMERNAME_admin'@'%' IDENTIFIED BY 'p4ssw0rd123';

GRANT ALL PRIVILEGES ON CUSTOMERNAME_db.* TO 'CUSTOMERNAME_admin'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON CUSTOMERNAME_db.* TO 'CUSTOMERNAME_admin'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON test_CUSTOMERNAME_db.* TO 'CUSTOMERNAME_admin'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON test_CUSTOMERNAME_db.* TO 'CUSTOMERNAME_admin'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;
```
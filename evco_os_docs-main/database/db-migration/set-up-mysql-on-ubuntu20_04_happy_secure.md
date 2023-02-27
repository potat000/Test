# setting up mysql server on linux (WSL ubuntu 20.04)

## 1. install
```console
~/evco_os$ sudo apt-get install mysql-server
~/evco_os$ sudo apt-get install libmysqlclient-dev
```

## 2. configure (if needed, usually not)
if you're getting the following error when using `mysql` command:
```console
ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock' (13)
```
[try this solution](https://stackoverflow.com/a/66949451/18024965):

run this bash command to edit the file (sudo because read-only):
```console
~/evco_os$ sudo nano /etc/mysql/my.cnf
```

enter the following to the end of file:
```text
[mysqld]
bind-address = 0.0.0.0 # can be anything
user = root
pid-file = /var/run/mysqld/mysqld.pid
socket = /var/run/mysqld/mysqld.sock
port = 3306

[client]
port = 3306
socket = /var/run/mysqld/mysqld.sock
```

## 3. create prod+uat database and remote user
in mysql shell:
```sql
CREATE DATABASE YOURCLIENT_db;
CREATE DATABASE YOURCLIENT_uat_db;

CREATE USER 'YOURCLIENT_admin'@'localhost' IDENTIFIED BY 'YOURCLIENT_PASSWORD';
CREATE USER 'YOURCLIENT_admin'@'%' IDENTIFIED BY 'YOURCLIENT_PASSWORD';

GRANT ALL PRIVILEGES ON `YOURCLIENT_db`.* TO 'YOURCLIENT_admin'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `YOURCLIENT_db`.* TO 'YOURCLIENT_admin'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `YOURCLIENT_uat_db`.* TO 'YOURCLIENT_admin'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `YOURCLIENT_uat_db`.* TO 'YOURCLIENT_admin'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;
```

## 4. connect to django application

to check port:
in mysql shell:
```sql
SHOW GLOBAL VARIABLES LIKE 'PORT';

-- output
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| port          | 3306  |
+---------------+-------+
```


settings.py:
```python
DATABASES = { # active
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'YOURCLIENT_uat_db',
        'USER': 'YOURCLIENT_admin',
        'PASSWORD': 'YOURCLIENT_PASSWORD',
        'HOST': 'evcoprodmysql01.mysql.database.azure.com', # server ip address
        'PORT': 3306, # port
    }
}
```
# Load Data
## 1. migrate
```console
~/evco_os$ python manage.py migrate
~/evco_os$ python manage.py loaddata "datadump_to_load.json"
```

## 2. check
enter the database and check whether the tables are created and data is loaded
```console
mysql -u YOURCLIENT_admin --database=YOURCLIENT_db -p -h evcoprodmysql01.mysql.database.azure.com --ssl-mode=REQUIRED
```


# references
1. [create new user and grant permissions in mysql](https://www.digitalocean.com/community/tutorials/how-to-create-a-new-user-and-grant-permissions-in-mysql)
2. add user for remote access
   - [add user for remote access](https://stackoverflow.com/questions/16287559/mysql-adding-user-for-remote-access)
   - [problems logging in](https://stackoverflow.com/a/13981864/18024965)
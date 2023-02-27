# db backup
log into server
```console
mysql -u mysqladmin -p -h evcoprodmysql01.mysql.database.azure.com --ssl-mode=REQUIRED
```

create backup db
```sql
-- drop if there is existing backup db
drop database <companyname>_db_backup;

-- create backup
create database <companyname>_db_backup;
```

[pipe](https://stackoverflow.com/a/675299/18024965) db into backup db
```
mysqldump <companyname>_db -u mysqladmin -p -h <hostname> --ssl-mode=REQUIRED | mysql <companyname>_db_backup -u mysqladmin -p -h <hostname> --ssl-mode=REQUIRED
```
#### working
<!-- mysqldump cbm_db -u mysqladmin -p -h evcoprodmysql01.mysql.database.azure.com --ssl-mode=REQUIRED | mysql cbm_backup_20230215 -u mysqladmin -p -h evcoprodmysql01.mysql.database.azure.com --ssl-mode=REQUIRED -->
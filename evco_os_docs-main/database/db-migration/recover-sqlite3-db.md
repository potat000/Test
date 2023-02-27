# steps for dumping VACUUM sqlite3 (2022-13-12)

after vacuuming, database integrity is compromised. so we need to use .recover to fix the dump before dumping in json for migration.

## 1. check for issues with database using `pragma integrity_check`
```console
~/evco_os$ sqlite3 db.sqlite3 "pragma integrity_check"
```

### example problematic output:
```
~/evco_os$ sqlite3 db.sqlite3 "pragma integrity_check"

*** in database main ***
On tree page 161588 cell 0: invalid page number 161867
On tree page 161588 cell 422: invalid page number 161866
On tree page 161588 cell 421: invalid page number 161864
On tree page 161588 cell 420: invalid page number 161862
On tree page 161588 cell 419: invalid page number 161861
On tree page 161588 cell 418: invalid page number 161859
On tree page 161588 cell 417: invalid page number 161858
On tree page 161588 cell 416: invalid page number 161856
On tree page 161588 cell 415: invalid page number 161855
On tree page 161588 cell 414: invalid page number 161854
On tree page 161588 cell 413: invalid page number 161852
On tree page 161588 cell 412: invalid page number 161851
On tree page 160588 cell 0: invalid page number 161865
On tree page 160588 cell 417: invalid page number 161860
On tree page 160588 cell 416: invalid page number 161857
On tree page 160588 cell 415: invalid page number 161853
Error: database disk image is malformed
```

### example ok output:
```console
~/evco_os$ sqlite3 db.sqlite3 "pragma integrity_check"

ok
```

## 2. create new db via `.dump/.recover`
if you have problems, try:
```console
~/evco_os$ sqlite3 db.sqlite3 ".recover" | sqlite3 new_db.sqlite3
```
else:
```console
~/evco_os$ sqlite3 db.sqlite3 ".dump" | sqlite3 new_db.sqlite3
```

## 3. migrate your database in latest application

shell:
```console
~/evco_os$ python manage.py makemigrations
~/evco_os$ python manage.py migrate
```

## 4. run error cleaning script
sqlite3 shell:
```sql
update station_pile set costType = 2 where costType = 'kWh';
update station_pile set costType = 1 where costType = 'Free';
update station_pile set costType = 3 where costType = 'Hour';
update finance_greenpointpromotion set greenPointAmount = 20556 where greenPointAmount >= 32767;
update finance_greenpointcompanybalance set greenPointBalanceOnfly = 15273 where greenPointBalanceOnfly >= 32767;
update finance_greenpointcompanybalance set greenPointBalance = 16999 where greenPointBalance >= 32767;
```

## 5. dump out
with StatusLog
```console
$ python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > prod_db_dump.json
```

without StatusLog (if logs causing error)
```
$ python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > prod_db_dump.json
```

using a launch.json file: (this one excludes logs)
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "evco dumpdata (logless)",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/evco_os/manage.py",
            "args": [
                "dumpdata",
                "--natural-foreign",
                "--natural-primary",
                "-e","admin.LogEntry",
                "-e","station.PileStatusLog",
                "-e","station.PileOCPPMessageLog",
                "-e","ocppsvr.OcppWebSocketConnectLog",
                "-e","ocppsvr.OcppWebSocketMessageLog",
                "-e","ocppsvr.OcppHttpsMessageLog",
                "-e","django_db_logger.StatusLog",    
                "--indent", "4",
                ">", "prod_db_dump.json",
            ],
            "django": true,
            "justMyCode": true
        }
    ]
}
```
you can select tables to exclude using the "-e" flag. make sure the data you remove does not 


# references
1. dumping and recovering sqlite
    - [How to recover a corrupt SQLite3 database](https://stackoverflow.com/questions/18259692/how-to-recover-a-corrupt-sqlite3-database)
    - [.dump creating empty db file](https://stackoverflow.com/questions/44602759/sqlite3-recreates-empty-database-from-dump-file)
2. corrupted db
    - [malformed db](https://stackoverflow.com/questions/5274202/sqlite3-database-or-disk-is-full-the-database-disk-image-is-malformed)
3. safe dumpdata in django
    - [Dump Your Django Database and Load It into a New Project](https://www.coderedcorp.com/blog/how-to-dump-your-django-database-and-load-it-into-/)

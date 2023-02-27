
# prelim error cleaning script
sqlite3 shell:
```sql
update station_pile set costType = 2 where costType = 'kWh';
update station_pile set costType = 1 where costType = 'Free';
update station_pile set costType = 3 where costType = 'Hour';
update finance_greenpointpromotion set greenPointAmount = 20556 where greenPointAmount >= 32767;
update finance_greenpointcompanybalance set greenPointBalanceOnfly = 15273 where greenPointBalanceOnfly >= 32767;
update finance_greenpointcompanybalance set greenPointBalance = 16999 where greenPointBalance >= 32767;
```
*2022-12-13: finance data format will change and thus was not loaded*

# FAQ: Errors when loading.
script to fix can be found in recover-sqlite3-db

**problem:**

## 1.
    UnicodeDecodeError: 'utf8' codec can't decode byte 0xff in position __: invalid start byte

**solution:**

[save as utf-8 format:](https://stackoverflow.com/a/59857138/18024965)
1. use sublime text to load the `dumpdata.json` file
2. File > Save with Encoding > **UTF-8**
3. IMPORTANT: don't save as **UTF-8 with BOM**

## 2.
    django.core.serializers.base.DeserializationError: Problem installing fixture '/home/marcu/evco/projects/evco-os/backup_dbs/prod/2022-12-12/prod_db_dump.json': ['“kWh” value must be an integer.']: (station.pile:pk=763) field_value was 'kWh'

**solution:**

changed old `costType` values on station_pile from string to integer (choice field)

sqlite3 shell:
```sql
update station_pile set costType = 2 where costType = 'kWh';
update station_pile set costType = 1 where costType = 'Free';
update station_pile set costType = 3 where costType = 'Hour';
```

## 3. 
    django.db.utils.DataError: Problem installing fixture '/home/marcu/evco/projects/evco-os/evco_os/prod_db_dump.json': Could not load finance.GreenPointPromotion(pk=2): (1264, "Out of range value for column 'greenPointAmount' at row 1")

**problem**

integer value out of range for smallint field

**solution**

sqlite3 shell:
```sql
update finance_greenpointpromotion set greenPointAmount = 20556 where greenPointAmount >= 32767;
```

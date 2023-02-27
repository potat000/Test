# common mysql errors when installing

## install mysql
follow [this link](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04) for install


## error 1
---
occurs when trying to start mysql shell, after mysqld has started:
```
ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock' (2)
```
reason:
no read/access permissisons on mysqld.sock

fix:
```
sudo chmod 755 /var/lib/mysql/mysql
sudo chmod 755 /var/run/mysqld/
```

## error 2
---
occurs when starting service: `sudo service mysql start`
```
su: warning: cannot change directory to /nonexistent: No such file or directory
```
reason:

[fix](https://stackoverflow.com/a/63040661):
stop server, and change home directory
```
sudo service mysql stop
sudo usermod -d /var/lib/mysql/ mysql
sudo service mysql start
```


## error 3
---
occurs when 
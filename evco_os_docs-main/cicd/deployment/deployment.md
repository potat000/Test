# current deployment to server

## Step 1: clone `evco_os_deploy`
---
```shell
$ cd /opt
$ sudo git clone https://gitlab.com/e3854/evco_os_deploy.git # deployment dir
```

## Step 2: pull `evco_os`
---
```shell
$ cd evco_os_deploy # change dir to deployment folder
$ sudo git clone -b feature https://gitlab.com/e3854/evco_os.git # source code dir, could be other branches
```

## Step 3: configure docker-compose.yml
---
We try to organise the configs such that one only has to change the `.env` file. 

Currently, we create specialised <b>"deployment directories"</b> for each company's `.env` and `docker-compose.yml` files because multitenancy is still in development.

For example, for customer `testcompany`:
```shell
$ sudo cp default testcompany
```
configure `container_name` and `ports` (optional) in `docker-compose.yml`

rename from:
```yml
container_name: default-evcoos # rename 'default' to customer
...
ports:
  - "9001:9001" # hostPort:containerPort
```
to:
```yml
container_name: testcompany-evcoos
...
ports:
  - "9000:9001" # can be any port, just make sure to map in nginx
```
## (OPTIONAL) Edit bind mount path
---
this will be useful if:
1. customers with different versions need specific/exclusive static assets
2. different versions have app-breaking asset changes


change:
```yml
...
    volumes:
      - /opt/evco_os_static/static:/build/static_shared # for nginx to serve static files
...
```
to (if for customer):
```yml
...
    volumes:
      - /opt/evco_os_static/testcompany/static:/build/static_shared # for nginx to serve static
...
```
<b>Take note that you will have to specify the `/static/` location for the corresponding site's config in `/etc/nginx/sites-available`. </b>

Read on to understand more about nginx


## Step 4: [configure environment variables in `.env` according to server mode](https://gitlab.com/e3854/evco_os_deploy/-/blob/main/template.env)
Databse url reference: https://github.com/kennethreitz/dj-database-url

Remember to set DEBUG=False in production!


## Step 5: Configure the nginx service
### Step 5.1: create new config filled in with customer name for new customer domain. 
---
we will create our first server block config file by creating a new file with replaced values
```shell
$ sed 's/DefaultPlaceholder/testcompany/g' /etc/nginx/sites-available/evco-default > /etc/nginx/sites-available/testcompany.evco.global
```

this step replaces 'DefaultPlaceholder' with 'testcompany' in the following:
```conf
upstream DefaultPlaceholder-backend { # 1: testcompany-backend
    server localhost:9001; 
}
...
server {
    # SSL configuration
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name DefaultPlaceholder.evco.global; # 2: testcompany.evco.global
    ssl_certificate /opt/ssl/evcoos.pem; #/opt/ssl/evcoos.crt;
    ssl_certificate_key /opt/ssl/evcoos.rsa;
...
    location / {

        proxy_pass http://DefaultPlaceholder-backend; # 3: http://testcompany-backend
   ...
    }

    location /static/ {
        root /opt/evco_os_static;
        try_files /DefaultPlaceholder/$uri /$uri =404; # 4: try_files /testcompany/$uri /$uri =404
    }

}
```
### note that if you set a specific bind mount path for static (step 3), the previous step sets this for you.
The nginx server will therfore look in `/opt/evco_os_static/testcompany/static/<filename>` for static files. 

Else, if you didnt set the bind mount, nginx server looks in the shared static directory: `/opt/evco_os_static/static/<filename>`. <b>MAKE SURE YOU CREATED THIS DIRECTORY!</b>
### For example:
#### testcompany.evco.global (nginx conf):
```conf
    location /static/ {
        root /opt/evco_os_static;
        try_files /testcompany/$uri /$uri =404;
    }
```
#### docker-compose.yml:
```yml
    volumes:
      - /opt/evco_os_static/testcompany/static:/build/static_shared 
```
### Step 5.2: edit the upstream channel port
---
```shell
```

change:
```conf
# !! port has to match service's specified port in docker-compose !!
upstream testcompany-backend {
    server localhost:9001; 
}
...
```
to:
```conf
upstream testcompany-backend {
    server localhost:9000; # make sure same as specified in docker compose
}
```


### Step 5.3: creating symbolic links (symlinks)
---
We have to create symlinks between `sites-available` and `sites-enabled`.

<b>NOTE: always configure sites-available first. Think of it as the actual configuration, while sites-enabled only serves to indicate which are literally `enabled`. Nginx reads from `/sites-enabled` during startup.</b>

To create the symlink:
```shell
$ sudo ln -s /etc/nginx/sites-available/testcompany.evco.global /etc/nginx/sites-enabled/
```
After creating symlink, your `sites-available` and `sites-enabled` dirs should look something like this, for example:
```shell
$ ls /etc/nginx/sites-available/
default  default-evco  testcompany.evco.global
```
```shell
$ ls /etc/nginx/sites-enabled/ # created symlinks are shown here
testcompany.evco.global
```
### Step 5.4: check for syntax errors in your conf
---
```shell
$ sudo nginx -t
```

### Step 5.5: restart the service
---
```shell
$ sudo service nginx restart
```

## Step 6: docker compose up
---
```shell
$ cd /opt/testcompany
$ sudo docker compose up -d --build
```
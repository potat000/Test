# updating source code and redeploy
### todo: add correct output

## Step 1: git pull `evco_os`
---
```shell
$ cd /opt/evco_os_deploy/evco_os # change dir to source code directory
$ git status # optional
$ git branch # check whether you're on the right branch
$ sudo git pull
```
## Step 2: rebuild container
---
```shell
$ cd /opt/evco_os_deploy/testcompany # change dir to specific company's deployment directory
$ sudo docker compose up -d --build
```

## Step 3: check status
after container is rebuilt, more `manage.py` will be run (see `evco_os/entrypoint.sh`). You might want to check the status and logs
---
```shell
$ sudo docker ps
$ sudo docker logs testcompany-evcoos -f #-f gives you the log stream instead of just a snapshot of the file
```
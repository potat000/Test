#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: models.py 1527 2023-02-15 12:59:40Z How $
#
# Copyright (c) 2021 Nuwa Information Co., Ltd, All Rights Reserved.
#
# Licensed under the Proprietary License,
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at our web site.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# $Author: How $
# $Date: 2023-02-15 20:59:40 +0800 (週三, 15 二月 2023) $
# $Revision: 1527 $

import os
import time
import threading
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.db import models, OperationalError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger('django')

class Key(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        verbose_name="User",
        on_delete=models.CASCADE,
    )
    keyName = models.CharField("Key name", max_length=255)
   
    def __str__(self):
        return "%s: %s" % (self.user, self.keyName)

class Server(models.Model):
    domain = models.CharField("Domain", max_length=255, unique=True)
    
    def __str__(self):
        return self.domain
    
class Manager(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        verbose_name="User",
        on_delete=models.CASCADE,
    )
    server = models.ForeignKey(
        Server,
        verbose_name="Server",
        on_delete=models.CASCADE,
    )
    key = models.ForeignKey(
        Key,
        verbose_name="Key",
        on_delete=models.CASCADE,
    )
    
    canBuild = models.BooleanField('Can build', default=True)
    canDeploy = models.BooleanField('Can deploy', default=True)
    canRemove = models.BooleanField('Can remove', default=True)
    canCreateDB = models.BooleanField('Can create DB', default=True)
    canResetDB = models.BooleanField('Can reset DB', default=True)
    
    class Meta:
        unique_together = ['user', 'server']
    
    def __str__(self):
        return "%s: %s" % (self.server, self.user)

# file writing lock        
lock = threading.Lock()
            
class App(models.Model):
    name = models.CharField("Name", max_length=255, unique=True)
    
    buildScript = models.TextField("Build script")
    
    productionSettings = models.TextField("Production settings", null=True, blank=True)
    stageSettings = models.TextField("Stage settings", null=True, blank=True)
    developmentSettings = models.TextField("Development settings", null=True, blank=True)
    
    testScript = models.FileField(
        "Test script", default=None, null=True, blank=True, upload_to='uploads/')
    
    deleted = models.BooleanField('Deleted', default=False)
    externalModification = models.BooleanField('External modification', default=False)
    conflictMsg = models.TextField("Conflict Message", null=True, blank=True)
    
    server = models.ForeignKey(
        'main.Server',
        verbose_name="Server which you want to deploy",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    ifttt = models.CharField("Project manager ifttt", max_length=255, null=True, blank=True)
    hchkProjectAPIKey = models.CharField("Healthchecks API key", max_length=255, null=True, blank=True)
    sentryDSN = models.CharField("Sentry DSN", max_length=255, null=True, blank=True)
    
    LOCKS = {} # 給 FileSystemEventHandler 判斷是否是 API 更改的，而非外部
    
    @property
    def lock(self):
        if not self.id in self.LOCKS:
            self.LOCKS[self.id] = threading.Lock()
        lock = self.LOCKS[self.id]
        return lock
               
    @property
    def path(self):
        return os.path.join(settings.PANDORA_APPS_DIR, self.name) 
    
    @property
    def buildScriptPath(self):
        return os.path.join(self.path, 'Build.sh')
        
    @property
    def productionSettingsPath(self):
        return os.path.join(self.path, 'PRODUCTION_Settings.ini')
        
    @property
    def stageSettingsPath(self):
        return os.path.join(self.path, 'STAGE_Settings.ini')
        
    @property
    def developmentSettingsPath(self):
        return os.path.join(self.path, 'DEVELOPMENT_Settings.ini')
    
    def saveApp(self): 
        lock.acquire()
        try:
            if not self.deleted:
                if not os.path.exists(self.path):
                    os.mkdir(self.path)
                
                fileData = [
                    (self.buildScriptPath, self.buildScript),
                    (self.productionSettingsPath, self.productionSettings),
                    (self.stageSettingsPath, self.stageSettings),
                    (self.developmentSettingsPath, self.developmentSettings),
                ]
                
                for p, d in fileData:
                    if d:
                        with open(p, 'r', encoding='utf-8') as f:
                            data = f.read()
                            
                        if not d == data:
                            # 檔案與 db 不同
                            with open(p, 'wb') as f:
                                f.write(d.encode()) 
        except Exception as e:
            logger.error(str(e))
        finally:
            lock.release()
                
    def readApp(self, update=True):
        fileData = [
            (self.buildScriptPath, 'buildScript'),
            (self.productionSettingsPath, 'productionSettings'),
            (self.stageSettingsPath, 'stageSettings'),
            (self.developmentSettingsPath, 'developmentSettings'),
        ]
        
        change = False
        
        for p, field in fileData:
            origin = getattr(self, field, '')
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    data = f.read()
                setattr(self, field, data)
            else:
                setattr(self, field, '')
                
            if not origin == getattr(self, field, ''):
                change = True   
                
        if update and change:
            self.save(saveApp=False) 
            
        return change
    
    def save(self, saveApp=True, **kwargs):
        if self.id and saveApp:
            self.saveApp()
        
        try:
            rt = super(App, self).save(**kwargs)
        except OperationalError as e:
            logger.error(str(e))
            time.sleep(1)
            rt = super(App, self).save(**kwargs)
        
        return rt
    
    def __str__(self):
        return self.name
        
class AppHandler(FileSystemEventHandler):

    def on_modified(self, event):
        if event.src_path.endswith(".ini") or event.src_path.endswith(".sh"):
            appName = os.path.dirname(event.src_path).replace(settings.PANDORA_APPS_DIR, '').strip("\\").strip("/")
            if App.objects.filter(name=appName).exists():
                app = App.objects.get(name=appName)
                #print(event.src_path, lock.locked())
                if not lock.locked(): # 表示是 API 改的，不是外部改的
                    app.externalModification = True
                    app.deleted = False
                    app.readApp()
                
    def on_deleted(self, event):
        if not event.src_path.endswith(".ini") and not event.src_path.endswith(".sh"): # 單純過濾刪除 sh 與 ini 時的狀況
            # 只有刪除資料夾才會對到 app name
            appName = event.src_path.replace(settings.PANDORA_APPS_DIR, '').strip("\\").strip("/")
            if App.objects.filter(name=appName).exists():
                app = App.objects.get(name=appName)
                app.externalModification = True
                app.deleted = True
                app.save(saveApp=False)
 
observer = Observer()
observer.schedule(AppHandler(), path=settings.PANDORA_APPS_DIR, recursive=True)
observer.start()

class Mode(object):
    PRODUCTION = 'PRODUCTION'
    STAGE = 'STAGE'
    DEVELOPMENT = 'DEVELOPMENT'   
    
    CHOICES = [
        (PRODUCTION, 'Production'),
        (STAGE, 'Stage'),
        (DEVELOPMENT, 'Development'),
    ]
    
    TEXTS = {
        PRODUCTION: 'Production',
        STAGE: 'Stage',
        DEVELOPMENT: 'Development',
    }

class Status(object):
    PROCESSING = 'PROCESSING'
    ERROR = 'ERROR'
    ERROR_DEPLOY = "ERROR_DEPLOY"
    ERROR_REMOVE = "ERROR_REMOVE"
    SUCCESS = 'SUCCESS'
    TESTING = 'TESTING'
    REMOVED = "REMOVED"
    SUCCESSFULLY_DEPLOY = "SUCCESSFULLY_DEPLOY"
    SUCCESSFULLY_RELEASE = "SUCCESSFULLY_RELEASE"
    
    CHOICES = [
        (PROCESSING, 'Processing'),
        (ERROR, 'Error'),
        (SUCCESS, 'Success'),
        (REMOVED, 'Removed'),
        (SUCCESSFULLY_DEPLOY, 'Successfully deploy'),
        (ERROR_DEPLOY, 'Error deploy'),
        (ERROR_REMOVE, 'Error remove'),
        (TESTING, 'Testing'),
        (SUCCESSFULLY_RELEASE, 'Successfully release'),
    ]

    TEXTS = {
        PROCESSING: 'Processing',
        ERROR: 'Error',
        SUCCESS: 'Success',
        REMOVED: 'Removed',
        SUCCESSFULLY_DEPLOY: 'Successfully deploy',
        ERROR_DEPLOY: 'Error deploy',
        ERROR_REMOVE: 'Error remove',
        TESTING: 'Testing',
        SUCCESSFULLY_RELEASE: 'Successfully release',
    }
    
    
class Log(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        verbose_name="User",
        on_delete=models.CASCADE,
    )
    server = models.ForeignKey(
        Server,
        verbose_name="Server",
        on_delete=models.CASCADE,
    )
    app = models.ForeignKey(
        App,
        verbose_name="App",
        on_delete=models.CASCADE,
    )
    createdTime = models.DateTimeField("Created time", auto_now_add=True)
    logFile = models.CharField("Log file", max_length=255)
    status = models.CharField("Status", max_length=255, choices=Status.CHOICES)
    
    class Meta:
        abstract = True
    
class Build(Log):
    image = models.CharField("Image ID", max_length=255, null=True)
    name = models.CharField("Image name", max_length=255, null=True)
    version = models.CharField("Image version", max_length=255, null=True)
    
    def __str__(self):
        return "%s: %s(%s)" % (self.app, self.image, self.createdTime)

class Deploy(Log):
    mode = models.CharField("Mode", max_length=255, choices=Mode.CHOICES)
    container = models.CharField("Container ID", max_length=255, null=True)
    
    def __str__(self):
        return "%s: %s(%s)" % (self.app, self.container, self.createdTime)
        
class CommandLog(models.Model):
    ip = models.CharField("IP", max_length=255, null=True)
    platformSystem = models.CharField("Platform system", max_length=255, null=True)
    platformVersion = models.CharField("Platform version", max_length=255, null=True)
    username = models.CharField("Usernae", max_length=255, null=True, db_index=True)
    fullCommand = models.CharField("Full command", max_length=255, null=True, db_index=True)
    server = models.CharField("server", max_length=255, null=True, db_index=True)
    serverIp = models.CharField("server IP", max_length=255, null=True)
    revision = models.CharField("Revision", max_length=255, null=True)
    command = models.CharField("Command", max_length=255, null=True, db_index=True)
    options = models.CharField("Options", max_length=255, null=True)
    output = models.BinaryField("Output", null=True)
    stdout = models.BinaryField("Stdout", null=True)
    stderr = models.BinaryField("Stderr", null=True)
    
    createdTime = models.DateTimeField("Created time", auto_now_add=True)
    
    def __str__(self):
        return "Deploy.py log:%s" % (self.createdTime,)
        
class GUILog(models.Model):
    logType = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    logId = models.PositiveIntegerField()
    log = GenericForeignKey('logType', 'logId')
    
    user = models.ForeignKey(
        get_user_model(),
        verbose_name="User",
        on_delete=models.CASCADE,
        null=True
    )
    server = models.ForeignKey(
        Server,
        verbose_name="Server",
        on_delete=models.CASCADE,
        null=True
    )
    app = models.ForeignKey(
        App,
        verbose_name="App",
        on_delete=models.CASCADE,
        null=True
    )
    
    # app
    
    createdTime = models.DateTimeField("Created time", auto_now_add=True)
    
    def __str__(self):
        return "Deploy.py log:%s" % (self.id,)
        
    class Meta:
        verbose_name = 'GUI log'
        verbose_name_plural = 'GUI logs'

@receiver(post_save, sender=Key)
@receiver(post_save, sender=Build)      
@receiver(post_save, sender=Deploy)
def addGUILog(sender, instance, created, **kwargs):
    if created:
        log = GUILog.objects.create(log=instance)
        if hasattr(instance, 'user'):
            log.user = instance.user
        if hasattr(instance, 'server'):
            log.server = instance.server
        if hasattr(instance, 'app'):
            log.app = instance.app
        log.save()
        
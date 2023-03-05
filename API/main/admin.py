#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: admin.py 1564 2023-02-28 16:59:24Z Jolin $
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
# $Author: Jolin $
# $Date: 2023-03-01 00:59:24 +0800 (週三, 01 三月 2023) $
# $Revision: 1564 $

import json
import logging
import os

import django
import requests
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import AllValuesFieldListFilter, DateFieldListFilter
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from Pandora import isVirtualMachine

from Deploy import _decompress
from main.models import (App, CommandLog, GUILog, Key, Manager, Mode, Server,
                         Status)

logger = logging.getLogger('django')

User = get_user_model()


def isLocalhost(request):
    if (
        request.META['HTTP_HOST'].startswith("192.168") or request.META['HTTP_HOST'].startswith("127.0.0.1") or
        request.META['HTTP_HOST'].startswith("localhost")
    ):
        return True
    return False


def canExecuteCommand(request, mode, server):
    if isLocalhost(request) and mode == Mode.PRODUCTION and not isVirtualMachine(server.domain):
        # 是 localhost，mode = PRODUCTION，且使用對象非 VM
        return False
    return True


def postAPI(request, url, data):
    headers = {'X-CSRFToken': get_token(request)}
    cookies = {
        'csrftoken': request.COOKIES.get('csrftoken'),
        'sessionid': request.COOKIES.get('sessionid'),
    }

    res = requests.post(url, data=data, headers=headers, cookies=cookies)
    return res


def recordLog(logFile, msg):
    with open(logFile, 'a+', encoding='utf8') as log:
        log.write(str(msg))


def searchAppsAtLogin(sender, user, request, **kwargs):
    if user.is_superuser:
        for appName in os.listdir(settings.PANDORA_APPS_DIR):
            app, created = App.objects.get_or_create(name=appName)
            app.readApp()


user_logged_in.connect(searchAppsAtLogin)


class KeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'keyName', 'keyUrl']
    search_fields = ['user', 'keyName']

    # readonly_fields = ('user', 'keyName',)

    def keyUrl(self, obj):
        url = "%s?name=%s" % (reverse("getKey"), obj.keyName)
        return format_html("<a href='%s'>Download key</a>" % url)

    keyUrl.short_description = 'Key URL'
    keyUrl.allow_tags = True

    def createKey(self, request, key):
        postData = {
            "keyName": key.keyName,
        }
        url = "%s%s" % (settings.PANDORA_API_URL, "/key/create/")
        res = postAPI(request, url, postData)
        data = json.loads(res.text)

        status = data.get("status", None)
        if status == 'success':
            return
        else:
            raise RuntimeError("Key create error: %s" % data.get("error"))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        try:
            return super().change_view(
                request,
                object_id,
                form_url,
                extra_context=extra_context,
            )
        except Exception as e:
            messages.error(request, str(e))
            return redirect("admin:main_key_changelist")

    def add_view(self, request, form_url='', extra_context=None):
        try:
            return super().add_view(
                request,
                form_url,
                extra_context=extra_context,
            )
        except Exception as e:
            messages.error(request, str(e))
            return redirect("admin:main_key_changelist")

    def save_model(self, request, obj, form, change):
        self.createKey(request, obj)
        super(KeyAdmin, self).save_model(request, obj, form, change)


admin.site.register(Key, KeyAdmin)


class ManagerInline(admin.TabularInline):
    model = Manager
    extra = 0
    list_display = [
        'user', 'canBuild', 'canDeploy',
        'canRemove', 'canCreateDB', 'canResetDB', 'privateKey']


class ServerAdmin(admin.ModelAdmin):
    list_display = ['domain', ]
    inlines = [ManagerInline, ]
    search_fields = ['domain', ]

    def addKey(self, request, manager):
        if manager.id:
            originManager = Manager.objects.get(id=manager.id)

            if originManager.key == manager.key:
                return
            self.removeKey(manager)

        postData = {
            "server": manager.server.domain,
            "keyName": manager.key.keyName,
        }
        url = "%s%s" % (settings.PANDORA_API_URL, "/key/add/")
        res = postAPI(request, url, postData)
        data = json.loads(res.text)
        status = data.get("status", None)

        if status in ('success', 'existed'):
            return
        else:
            if "not found key" in data.get("error"):
                # Key 不存在了，所以刪除
                manager.key.delete()
            else:
                raise RuntimeError("Key add error: %s" % data.get("error"))

    def removeKey(self, request, manager):
        postData = {
            "server": manager.server.domain,
            "keyName": manager.key.keyName,
        }
        url = "%s%s" % (settings.PANDORA_API_URL, "/key/remove/")
        res = postAPI(request, url, postData)
        data = json.loads(res.text)
        status = data.get("status", None)

        if status in ('success', 'existed'):
            return
        else:
            if "not found key" in data.get("error"):
                # Key 不存在了，所以刪除
                manager.key.delete()
            else:
                raise RuntimeError("Key remove error: %s" % data.get("error"))

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        # remove key
        for obj in formset.deleted_objects:
            try:
                self.removeKey(request, obj)
                obj.delete()
            except Exception as e:
                messages.error(request, str(e))

        # add key
        for instance in instances:
            try:
                self.addKey(request, instance)
                instance.save()
            except Exception as e:
                messages.error(request, str(e))

        formset.save_m2m()


admin.site.register(Server, ServerAdmin)

class CommandLogAdmin(admin.ModelAdmin):
    list_display = [
        'showCreatedTime', 'ip', 'platformSystem', 'platformVersion', 'username', 'server', 'serverIp', 'fullCommand',
        'command', 'options', 'revision'
    ]
    search_fields = [
        'username',
        'fullCommand',
    ]
    readonly_fields = [
        'showCreatedTime', 'ip', 'platformSystem', 'platformVersion', 'username', 'serverIp', 'revision', 'fullCommand',
        'server', 'command', 'options', 'showOutput', 'showStdout', 'showStderr'
    ]
    list_filter = [
        ('createdTime', DateFieldListFilter),
        ('username', AllValuesFieldListFilter),
        ('server', AllValuesFieldListFilter),
        ('command', AllValuesFieldListFilter),
    ]

    def showCreatedTime(self, obj):
        return obj.createdTime.strftime("%Y-%m-%d %H:%M:%S")

    showCreatedTime.short_description = 'Created time'
    showCreatedTime.allow_tags = True

    def showOutput(self, obj):
        return mark_safe("<pre>%s</pre>" % _decompress(obj.output, encode=False))

    showOutput.short_description = 'Output'
    showOutput.allow_tags = True

    def showStdout(self, obj):
        return mark_safe("<pre>%s</pre>" % _decompress(obj.stdout, encode=False))

    showStdout.short_description = 'Stdout'
    showStdout.allow_tags = True

    def showStderr(self, obj):
        return mark_safe("<pre>%s</pre>" % _decompress(obj.stderr, encode=False))

    showStderr.short_description = 'Stderr'
    showStderr.allow_tags = True


admin.site.register(CommandLog, CommandLogAdmin)


class GUILogAdmin(admin.ModelAdmin):
    list_display = [
        'showCreatedTime', 'showLogType', 'user', 'server', 'app', 'showStatus', 'showImage', 'showContainer',
        'showNote', 'logFileLink'
    ]


    list_filter = [
        ('createdTime', DateFieldListFilter),
        ('user__username', AllValuesFieldListFilter),
        ('server__domain', AllValuesFieldListFilter),
        ('app__name', AllValuesFieldListFilter),
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def showCreatedTime(self, obj):
        return obj.createdTime.strftime("%Y-%m-%d %H:%M:%S")

    showCreatedTime.short_description = 'Created time'
    showCreatedTime.allow_tags = True

    def logFileLink(self, obj):
        if hasattr(obj.log, 'logFile'):
            logURL = "%s?log=%s" % (reverse('log'), obj.log.logFile)
            link = "<a class='button' href=\"%s\" target=\"_blank\">View</a> " % logURL
            download = "<a class='button' href=\"\\%s\" download>Download</a>" % obj.log.logFile
            return mark_safe(link + download)
        return 0

    logFileLink.short_description = 'Log file'
    logFileLink.allow_tags = True

    def showLogType(self, obj):
        return obj.logType.name.capitalize()

    showLogType.short_description = 'Log type'
    showLogType.allow_tags = True

    def showStatus(self, obj):
        if hasattr(obj.log, 'status'):
            return Status.TEXTS[obj.log.status]
        return 0

    showStatus.short_description = 'Status'
    showStatus.allow_tags = True

    def showImage(self, obj):
        if hasattr(obj.log, 'image'):
            return "%s" % (obj.log.image,)
        return 0

    showImage.short_description = 'Image'
    showImage.allow_tags = True

    def showContainer(self, obj):
        if hasattr(obj.log, 'container') and hasattr(obj.log, 'mode'):
            return "%s" % (obj.log.container,)
        return 0

    showContainer.short_description = 'Container'
    showContainer.allow_tags = True

    def showNote(self, obj):
        if hasattr(obj.log, 'image'):
            return "%s:%s" % (obj.log.name, obj.log.version)
        if hasattr(obj.log, 'mode'):
            return Mode.TEXTS[obj.log.mode]
        if hasattr(obj.log, 'keyName'):
            return obj.log.keyName
        return 0

    showNote.short_description = 'Note'
    showNote.allow_tags = True


admin.site.register(GUILog, GUILogAdmin)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: views.py 1578 2023-03-04 17:58:54Z Jolin $
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
# $Date: 2023-03-05 01:58:54 +0800 (週日, 05 三月 2023) $
# $Revision: 1578 $

import abc
import datetime
import logging
import os
import sys
import threading

import requests
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         JsonResponse)
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from Pandora import (DEFAULT_MARIADB_PASSOWRD, DEPLOY_TEST_SERVER_USER,
                     getConnectKwargs, getOrCreateKey)
from Pandora.CloudServices import HealthchecksService, SentryService

import Deploy
from Deploy import _getAppName, createDbSql, mode, quite, registry, vm
from fabric import connection
from Iuno.member.AbstractViews import TracLoginView
from main.models import Key
from main.serializers import (AddRemoveKeyOperationSerializer,
                              BaseOperationSerializer,
                              DatabaseOperationSerializer,
                              KeyOperationSerializer)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from termcolor import cprint

logger = logging.getLogger(__file__)


# DEPLOY_GUI_LOG_RECORD_URL = "http://127.0.0.1:8000/record/?type=gui"

class LoginView(TracLoginView):
    ACCOUNT_SERVICES = [
        HealthchecksService(),
        SentryService(),
    ]

    def afterPost(self, request, user):
        if not user.user_permissions.all():
            # first create
            user.is_staff = True

            # add permission
            contenttypeIds = ContentType.objects.filter(app_label="main"
                                                       ).exclude(model__in=["server", "manager", "key"]).values_list(
                                                           "id",
                                                       )
            permissions = Permission.objects.filter(content_type_id__in=contenttypeIds,)
            for p in permissions:
                user.user_permissions.add(p)
            user.save()

            # create services account
            for service in self.ACCOUNT_SERVICES:
                service.createAccount(user.email, request.POST.get('password'))

# patch
def configureDjango(*args, **kws):
    # 在 django 專案如果再 setup 一次會讓 django 設定出錯，因此 pass
    pass


Deploy.configureDjango = configureDjango


class KeyCreateView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = KeyOperationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                data = serializer.validated_data
                keyName = data['keyName']

                publicKey, privateKey, publicKeyPath, privateKeyPath = \
                    getOrCreateKey(keyName, keyPath=settings.PANDORA_KEYS_DIR)

                responseData = {
                    'status': 'success',
                }
                return Response(responseData)
            except Exception as e: # pylint: disable=W0703
                responseData = {
                    'error': str(e),
                }
                return Response(responseData)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KeyAddView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddRemoveKeyOperationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                data = serializer.validated_data

                keyName = data['keyName']
                userKeyPath = os.path.join(settings.PANDORA_KEYS_DIR, keyName)
                if not os.path.exists(userKeyPath):
                    responseData = {
                        'error': 'not found key: %s' % keyName,
                    }
                    return Response(responseData, status=status.HTTP_400_BAD_REQUEST)

                publicKey, privateKey, publicKeyPath, privateKeyPath = \
                    getOrCreateKey(keyName, keyPath=settings.PANDORA_KEYS_DIR)

                with connection.Connection(
                    data.get('server'), user="devops", connect_kwargs=settings.PANDORA_KEYS_MANAGER_LOGIN_KEYWORD
                ) as c:

                    authorizedKey = "%s nuwa@%s" % (publicKey, c.host)

                    result = c.run("sudo bin/modify_nuwa_keys.sh \"%s\" \"%s\"" % (authorizedKey, keyName))

                    if "success" in result.stdout:
                        msg = "success"
                    elif "existed" in result.stdout:
                        msg = "existed"
                    else:
                        msg = "error"

                responseData = {
                    'status': msg,
                }
                return Response(responseData)
            except Exception as e: # pylint: disable=W0703
                responseData = {
                    'error': str(e),
                }
                return Response(responseData)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KeyRemoveView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddRemoveKeyOperationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                data = serializer.validated_data

                keyName = data['keyName']

                userKeyPath = os.path.join(settings.PANDORA_KEYS_DIR, keyName)
                if not os.path.exists(userKeyPath):
                    responseData = {
                        'error': 'not found key: %s' % keyName,
                    }
                    return Response(responseData, status=status.HTTP_400_BAD_REQUEST)

                publicKey, privateKey, publicKeyPath, privateKeyPath = \
                    getOrCreateKey(keyName, keyPath=settings.PANDORA_KEYS_DIR)

                with connection.Connection(
                    data.get('server'), user="devops", connect_kwargs=settings.PANDORA_KEYS_MANAGER_LOGIN_KEYWORD
                ) as c:

                    authorizedKey = "%s nuwa@%s" % (publicKey, c.host)

                    result = c.run("sudo bin/modify_nuwa_keys.sh -r \"%s\" \"%s\"" % (authorizedKey, keyName))

                    if "success" in result.stdout:
                        msg = "success"
                    elif "not existed" in result.stdout:
                        msg = "not existed"
                    else:
                        msg = "error"

                responseData = {
                    'status': msg,
                }
                return Response(responseData)
            except Exception as e: # pylint: disable=W0703
                responseData = {
                    'error': str(e),
                }
                return Response(responseData)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BaseOperationSerializer

    @abc.abstractmethod
    def run(self, c, name, appName, data):
        return

    def callback(self, data, postData):
        try:
            callbackUrl = data.get('callback', None)
            if callbackUrl:
                headers = {'X-CSRFToken': get_token(self.request)}
                cookies = {
                    'csrftoken': self.request.COOKIES.get('csrftoken'),
                    'sessionid': self.request.COOKIES.get('sessionid'),
                }
                r = requests.post(callbackUrl, data=postData, headers=headers, cookies=cookies)
                logger.info(r.text)
        except Exception as e: # pylint: disable=W0703
            logger.error(e)

    def getPostData(self):
        data = {
            'status': 'success',
        }
        return data

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                data = serializer.validated_data

                connectKwargs = None
                if data.get('password', None):
                    connectKwargs = getConnectKwargs(password=data.get('password', None))
                if data.get('keyName', None):
                    keyName = data.get('keyName', None)
                    key = Key.objects.get(keyName=keyName)
                    if not key.user == request.user:
                        responseData = {
                            'error': "This key not belong to %s" % request.user,
                        }
                        return Response(responseData)
                    key = os.path.join(settings.PANDORA_KEYS_DIR, keyName, "PrivateKey.key")
                    if not os.path.exists(key):
                        responseData = {
                            'error': 'not found key: %s' % keyName,
                        }
                        return Response(responseData, status=status.HTTP_400_BAD_REQUEST)
                    connectKwargs = getConnectKwargs(key=key)
                if not connectKwargs:
                    responseData = {
                        'error': 'not login data',
                    }
                    return Response(responseData, status=status.HTTP_400_BAD_REQUEST)

                logFileName = "%s.log" % str(datetime.datetime.now()).replace(":", "-").replace(" ", "_")
                logFilePath = data.get('logFile', os.path.join("static", "Logs", logFileName))

                openFileMode = 'w'
                if data.get('logFile'):
                    if os.path.exists(data.get('logFile')):
                        openFileMode = 'a'

                def startConnect():
                    try:
                        with connection.Connection(
                            data.get('server'), user=DEPLOY_TEST_SERVER_USER, connect_kwargs=connectKwargs
                        ) as c:

                            with open(logFilePath, openFileMode, encoding='utf8') as log:
                                sys.stdout = log
                                sys.stderr = log

                                # record call API POST data and URL
                                cprint(
                                    "API Processing: %s" % (request.path,),
                                    "blue",
                                    "on_white",
                                    attrs=["bold", "underline"],
                                )
                                cprint(
                                    "API POST DATA: %s" % (dict(request.POST),),
                                    "blue",
                                    "on_white",
                                    attrs=["bold", "underline"],
                                )

                                # base cmd
                                name = data.get('appName')
                                mode(c, data.get('mode'))

                                if data.get('registry'):
                                    registry(
                                        c,
                                        settings.PANDORA_API_REGISTRY,
                                        auth=(
                                            settings.PANDORA_API_REGISTRY_USERNAME,
                                            settings.PANDORA_API_REGISTRY_PASSWORD
                                        )
                                    )
                                if data.get('isVM'):
                                    vm(c)

                                quite(c)

                                appName = _getAppName(data.get('appName'))
                                if not appName:
                                    appName = name.lower()

                                # extra cmd
                                self.run(c, name, appName, data)
                                cprint(
                                    "Disconnect: %s" % data.get('server'),
                                    "blue",
                                    "on_white",
                                    attrs=["bold", "underline"],
                                )
                                cprint(
                                    "Process End",
                                    "blue",
                                    "on_white",
                                    attrs=["bold", "underline"],
                                )
                            sys.stdout = sys.__stdout__
                            sys.stderr = sys.__stderr__

                        postData = self.getPostData()
                        self.callback(data, postData)
                    except Exception as e: # pylint: disable=W0703
                        postData = {
                            'status': 'error',
                            'msg': str(e),
                        }
                        self.callback(data, postData)

                t = threading.Thread(target=startConnect)
                t.start()

                responseData = {
                    'status': 'success',
                    'logFile': logFilePath,
                }
                return Response(responseData)
            except Exception as e: # pylint: disable=W0703
                responseData = {
                    'error': str(e),
                }

                return Response(responseData)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def createDb(c, name, appName, data):
    # base data
    # mariadbName = _getContainerName(c, 'mariadb')	 	
    # create Db
    createDbSqlCmdList = createDbSql(c, appName, data.get('dbPassword', DEFAULT_MARIADB_PASSOWRD), show=False)
    for cmd in createDbSqlCmdList:
        r = c.run("sudo ~/bin/execute_mysql.sh -e %s " % cmd.replace("mysql ", ""))

class CreateDbView(BaseView):
    """
    Create Db
    """

    serializer_class = DatabaseOperationSerializer

    def run(self, c, name, appName, data):
        createDb(c, name, appName, data)
        return

def getKeyView(request):
    keyName = request.GET.get('name')
    if keyName:
        key = Key.objects.get(keyName=keyName)
        if key.user == request.user:
            publicKey, privateKey, publicKeyPath, privateKeyPath = \
                getOrCreateKey(keyName, keyPath=settings.PANDORA_KEYS_DIR)
            response = HttpResponse(privateKey, content_type='text/plain')
            response['Content-Disposition'] = \
                'attachment; filename=PrivateKey.key'
            return response
        else:
            return HttpResponseForbidden()

    raise Http404('Key not found.')

def getLogView(request):
    logFileName = request.GET.get('log')
    with open(logFileName, "r", encoding='utf8') as logFile:
        log = logFile.read()

    # 如果不在這裡 import，Ajax 一陣子會使得發生 server 狀況:
    # A server error occurred.  Please contact the administrator.
    # 原因未知
    from main.models import Build, Deploy, Status # pylint: disable=C0415

    if Build.objects.filter(logFile=logFileName).exists():
        model = Build
    elif Deploy.objects.filter(logFile=logFileName).exists():
        model = Deploy
    else:
        raise Http404('Log not found.')

    m = model.objects.get(logFile=logFileName)

    logs = [l.replace(" ", ";nbsp;") for l in log.split("\n") if l]
    lines = len(logs)
    end = False
    if lines > 0:
        if m.status in [
            Status.ERROR, Status.SUCCESS, Status.ERROR_DEPLOY, Status.SUCCESSFULLY_DEPLOY, Status.ERROR_REMOVE,
            Status.REMOVED, Status.SUCCESSFULLY_RELEASE
        ]:
            end = True

    ctx = {
        'logFileName': logFileName.replace("\\", "\\\\"), # 因為寫在 JS 內是用 "" 包起來的，因此 \ 要跳脫
        'log': logs,
        'end': end,
    }
    if request.is_ajax():
        return JsonResponse(ctx)
    return render(request, 'main/Log.html', ctx)

@method_decorator(csrf_exempt, name='dispatch')
class DeployPyRecordView(View):

    def post(self, request):
        typeOfRecord = request.GET.get("type", "command")
        if typeOfRecord == "command":
            from main.models import CommandLog # pylint: disable=C0415

            data = dict(request.POST.items())

            data['output'] = data.get('output', '').encode()
            data['stdout'] = data.get('stdout', '').encode()
            data['stderr'] = data.get('stderr', '').encode()

            CommandLog.objects.create(**data)

            return HttpResponse("0")
        elif typeOfRecord == "gui":
            from main.models import GUILog # pylint: disable=C0415

            data = dict(request.POST.items())

            data['output'] = data.get('output', '').encode()

            GUILog.objects.create(**data)

            return HttpResponse("0")
        else:
            return HttpResponse("1")

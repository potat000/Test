#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: urls.py 1569 2023-03-01 04:53:06Z Jolin $
#
# Copyright (c) 2019 Nuwa Information Co., Ltd, All Rights Reserved.
#
# Licensed under the Proprietary License,
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at our web site.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# $Author: Jolin $
# $Date: 2023-03-01 12:53:06 +0800 (週三, 01 三月 2023) $
# $Revision: 1569 $ 

from django.conf.urls import include, url

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from main import views
from rest_framework import permissions

schemaView = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^$', views.LoginView.as_view(), name="login"),

    # ajax app and log and status
    url(r'^log/$', views.getLogView, name="log"),
    url(r'^record/$', views.DeployPyRecordView.as_view(), name="record"),   
    # api
    url(r'^database/create/$', views.CreateDbView.as_view(), name="createDb"),
    # key
    url(r'^key/create/$', views.KeyCreateView.as_view(), name="keyCreate"),
    url(r'^key/add/$', views.KeyAddView.as_view(), name="keyAdd"),
    url(r'^key/remove/$', views.KeyRemoveView.as_view(), name="keyRemove"),
    url(r'^key/get/$', views.getKeyView, name='getKey'),
    # rest_framework
    url(r'^api/', include('rest_framework.urls')),
    # swagger
    url(r'^swagger(?P<format>\.json|\.yaml)$', schemaView.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

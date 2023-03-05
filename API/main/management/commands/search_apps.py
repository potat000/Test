#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: search_apps.py 1010 2021-04-08 13:15:49Z Lavender $
#
# Copyright (c) 2017 Nuwa Information Co., Ltd, All Rights Reserved.
#
# Licensed under the Proprietary License,
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at our web site.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# $Author: Lavender $
# $Date: 2021-04-08 21:15:49 +0800 (週四, 08 四月 2021) $
# $Revision: 1010 $

import os

from django.core.management.base import BaseCommand
from django.conf import settings

from main.models import App

class Command(BaseCommand):

    def handle(self, *args, **options):
        for appName in os.listdir(settings.PANDORA_APPS_DIR):
            app, created = App.objects.get_or_create(name=appName)
            app.readApp()
        

        
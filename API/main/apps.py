#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: apps.py 1277 2021-12-24 04:53:04Z Mint $
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
# $Author: Mint $
# $Date $
# $Revision $
import os

from django.apps import AppConfig
from django.conf import settings

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'main'
    
    def ready(self):
        try:
            from main.models import Key
            
            for key in Key.objects.all():
                userKeyPath = os.path.join(settings.PANDORA_KEYS_DIR, key.keyName)
                if not os.path.exists(userKeyPath):
                    key.delete()
        except Exception: #pylint: disable=W0703
            pass
            
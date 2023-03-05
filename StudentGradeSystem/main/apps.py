#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: apps.py 2694 2022-12-11 13:30:50Z Jolin $
#
# Copyright (c) 2022 Nuwa Information Co., Ltd, All Rights Reserved.
#
# Licensed under the Proprietary License,
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at our web site.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# $Author: Jolin $
# $Date: 2022-12-11 21:30:50 +0800 (週日, 11 十二月 2022) $
# $Revision: 2694 $

from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

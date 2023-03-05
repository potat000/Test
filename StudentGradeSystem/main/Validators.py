#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: Validators.py 2776 2023-01-08 13:23:31Z Jolin $
#
# Copyright (c) 2023 Nuwa Information Co., Ltd, All Rights Reserved.
#
# Licensed under the Proprietary License,
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at our web site.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# $Author: Jolin $
# $Date: 2023-01-08 21:23:31 +0800 (週日, 08 一月 2023) $
# $Revision: 2776 $

import re

from django.core.exceptions import ValidationError


def validatePhoneNumber(phoneNumber):
    pattern = r'09\d{8}$'
    if not re.match(pattern, phoneNumber):
        raise ValidationError(message="手機號碼須以 09 開頭並為 10 位數字！")

def validateEnrolledYear(enrolledYear):
    if enrolledYear < 0:
        raise ValidationError(message="入學年分不得為負數！")

def validateClassNumber(number):
    if number < 0:
        raise ValidationError(message="班級不得為負數！")

def validateScore(score):
    if score < 0 or score > 0:
        raise ValidationError(message="分數不得小於 0 或大於 100！")\

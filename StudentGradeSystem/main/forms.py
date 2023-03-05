#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: forms.py 2754 2023-01-01 13:40:13Z Jolin $
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
# $Date: 2023-01-01 21:40:13 +0800 (週日, 01 一月 2023) $
# $Revision: 2754 $

from django import forms

from .models import Clazz, Test, User


class ClazzForm(forms.ModelForm):
    class Meta:
        model = Clazz
        fields = "__all__"

class CreateTeacherForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "password", "name", "phoneNumber", "clazz"]

class UpdateTeacherForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "name", "phoneNumber", "clazz"]

class CreateStudentForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "password", "name", "phoneNumber", "clazz"]

class UpdateStudentForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "name", "phoneNumber", "clazz"]

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        exclude = ["subject", "clazz", "semester"]
        widgets = {
            "percentage": forms.TextInput(attrs={"placeholder": "請輸入0~100"}),
        }

"""
class StudentIdentityForm(forms.Form):
    CHOICES = [
        ("國文小老師", 3),
        ("英文小老師", 4),
        ("數學小老師", 5),
        ("學生", 6),
    ]
    identity = forms.CharField(choices=CHOICES)
"""

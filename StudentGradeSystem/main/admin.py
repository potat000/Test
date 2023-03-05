#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: admin.py 2754 2023-01-01 13:40:13Z Jolin $
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

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Clazz, Grade, Semester, Test, User


class ClazzAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "number", "enrolledYear")
    list_filter = ("enrolledYear",)
    search_fields = ("name",)

class GradeAdmin(admin.ModelAdmin):
    list_display = ("id", "test", "semester", "user", "score")
    list_filter = (
        "test__name",
        "semester",
    )
    search_fields = ("user__name",)

class SemesterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "isCurrent")
    list_filter = ("isCurrent",)

class TestAdmin(admin.ModelAdmin):
    list_display = ("id", "clazz", "semester", "subject", "name", "type", "percentageWithSymbol")
    list_filter = (
        "clazz",
        "semester",
        "subject",
        "type",
    )
    search_fields = ("name",)

    def percentageWithSymbol(self, obj):
        return f"{obj.percentage} %"

class UserInfoAdmin(UserAdmin):
    list_display = ("id", "clazz", "name", "phoneNumber", "username")
    list_filter = ("clazz",)
    search_fields = ("name",)

admin.site.register(User, UserInfoAdmin)
admin.site.register(Clazz, ClazzAdmin)
admin.site.register(Grade, GradeAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Test, TestAdmin)

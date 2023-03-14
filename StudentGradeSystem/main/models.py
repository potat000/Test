#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: models.py 2775 2023-01-08 13:12:55Z Jolin $
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
# $Date: 2023-01-08 21:12:55 +0800 (週日, 08 一月 2023) $
# $Revision: 2775 $

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Q

from .Validators import (validateClassNumber, validateEnrolledYear,
                         validatePhoneNumber, validateScore)

DIRECTOR = 1
TEACHER = 2
CHINESE_ASSISTANT = 3
ENGLISH_ASSISTANT = 4
MATH_ASSISTANT = 5
STUDENT = 6

class TeacherManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(groups=TEACHER)

class StudentManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(groups=CHINESE_ASSISTANT) | Q(groups=ENGLISH_ASSISTANT) | Q(groups=MATH_ASSISTANT) | Q(groups=STUDENT)
        )

class Clazz(models.Model):
    name = models.CharField(max_length=10)
    number = models.IntegerField(validators=[validateClassNumber])
    enrolledYear = models.IntegerField(validators=[validateEnrolledYear])

    def __str__(self):
        return self.name

class User(AbstractUser):
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=10)
    phoneNumber = models.CharField(max_length=10, validators=[validatePhoneNumber])
    status = models.CharField(max_length=10)

    objects = UserManager()
    teachers = TeacherManager()
    students = StudentManager()

    class Meta:
        permissions = (
            ("readSelf", "readSelf"),
            ("editSelf", "editSelf"),

            ("readTeacher", "readTeacher"),
            ("createTeacher", "createTeacher"),
            ("updateTeacher", "updateTeacher"),
            ("deleteTeacehr", "deleteTeacher"),

            ("readStudent", "readStudent"),
            ("createStudent", "createStudent"),
            ("updateStudent", "updateStudent"),
            ("deleteStudent", "deleteStudent"),
        )

    DIRECTOR = 1
    TEACHER = 2
    CHINESE_ASSISTANT = 3
    ENGLISH_ASSISTANT = 4
    MATH_ASSISTANT = 5
    STUDENT = 6

class Semester(models.Model):
    name = models.CharField(max_length=10)
    isCurrent = models.BooleanField()

    def __str__(self):
        return self.name

class Test(models.Model):
    clazz = models.ForeignKey(Clazz, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=10)
    name = models.CharField(max_length=10)
    type = models.IntegerField(choices=((1, "段考"), (2, "小考")), default="段考")
    percentage = models.IntegerField()

    def __str__(self):
        return self.name

class Grade(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    score = models.FloatField(validators=[validateScore])

class TestC(models.Model):
    c = models.CharField(max_length=10)
    d = models.IntegerField()
    
class TestA(models.Model):
    a = models.CharField(max_length=10)

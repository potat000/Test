#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: create_student.py 2776 2023-01-08 13:23:31Z Jolin $
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
# $Date: 2023-01-08 21:23:31 +0800 (週日, 08 一月 2023) $
# $Revision: 2776 $

import random
from random import randint

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Clazz, Grade, Semester, Test, User


class Command(BaseCommand):

    help = "新增學生"

    def add_arguments(self, parser):
        parser.add_argument("studentNum", nargs='+', type=int, help='Indicates the number of users to be created')

    @transaction.atomic
    def handle(self, *args, **options):
        studentNum = options["studentNum"][0]
        clazzList = Clazz.objects.all()
        for i in range(studentNum):
            newStu = User.students.create(
                username=f"newStuAC{i}",
                password=make_password(f"newStuPW{i}"),
                name=f"newStu{i}",
                phoneNumber="0900000000",
                clazz=random.choice(clazzList)
            )
            print(f"成功建立 {newStu.id}, 班級為 {newStu.clazz}！")

            newStu.groups.add(User.STUDENT)
            print(f"{newStu.id}成功新增群組！")

            currentSemester = Semester.objects.get(isCurrent=True)
            clazzTest = Test.objects.filter(clazz=newStu.clazz, semester=currentSemester)
            for i, test in enumerate(clazzTest):
                newGrade = Grade.objects.create(score=randint(0, 100), semester=currentSemester, test=test, user=newStu)
                print(f"成功建立 {newStu.id} 的成績 {newGrade.id}！")

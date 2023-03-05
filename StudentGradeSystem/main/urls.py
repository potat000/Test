#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: urls.py 2803 2023-01-14 15:28:08Z Jolin $
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
# $Date: 2023-01-14 23:28:08 +0800 (週六, 14 一月 2023) $
# $Revision: 2803 $

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.logout, name='logout'),

    path('user/<int:userID>/edit', views.editSelfView.as_view(), name='editSelf'),
    path('user/<int:userID>/password/edit', views.editPasswordView.as_view(), name='editPassword'),

    path('classes', views.ClassInfoView.as_view(), name='classInfo'),
    path('classes/names', views.autocompleteClassName, name='searchClass'),
    path('class/create', views.CreateClassView.as_view(), name='createClass'),
    path('class/<int:classID>/edit', views.UpdateClassView.as_view(), name='editClass'),
    path('class/<int:classID>/delete', views.DeleteClassView.as_view(), name='deleteClass'),

    path('semesters', views.getSemesterInfo, name='semesterInfo'),
    path('semester/create', views.createSemester, name='createSemester'),
    path('semester/<int:semesterID>/set', views.setCurrentSemester, name='setCurrentSemester'),
    path('semester/<int:semesterID>/delete', views.deleteSemester, name='deleteSemester'),

    path('teachers', views.TeacherInfoView.as_view(), name='teacherInfo'),
    path('teachers/names', views.autocompleteTeacherName, name='searchTeacher'),
    path('teacher/create', views.CreateTeacherView.as_view(), name='createTeacher'),
    path('teacher/<int:teacherID>/edit', views.UpdateTeacherView.as_view(), name='editTeacher'),
    path('teacher/<int:teacherID>/delete', views.deleteTeacher, name='deleteTeacher'),

    path('students', views.StudentInfoView.as_view(), name='studentInfo'),
    path('students/names', views.autocompleteStudentName, name='searchStudent'),
    path('student/create', views.CreateStudentView.as_view(), name='createStudent'),
    path('student/<int:studentID>/edit', views.UpdateStudentView.as_view(), name='editStudent'),
    path('student/<int:studentID>/delete', views.DeleteStudentView.as_view(), name='deleteStudent'),
    path('students/scrollloading', views.getStudentScrollLoadingTable, name='studentScrollLoading'),
    #scrollloading --> ?page=~

    path('<str:subject>/tests', views.TestInfoView.as_view(), name='testInfo'),
    path('<str:subject>/test/create', views.CreateTestView.as_view(), name='createTest'),
    path('<str:subject>/test/<int:testID>/edit', views.UpdateTestView.as_view(), name='editTest'),
    path('<str:subject>/test/<int:testID>/delete', views.DeleteTestView.as_view(), name='deleteTest'),

    path('students/grades', views.getStudentGrade, name='studentGrade'),
    path('students/grades/chinese/sort', views.sortByChineseGrade, name='sortByChineseGrade'),
    path('classes/grades', views.getClassGrade, name='classGrade'),

    path('exams/grades', views.getExamGradeOfTeacher, name='examGradeOfTeacher'),
    path('subjects/grades', views.getSubjectGrade, name='subjectGrade'),

    path('exams/grade', views.getExamGradeOfStudent, name='examGradeOfStudent'),
    path('semesters/grades', views.getSemesterGrade, name='semesterGrade'),

    path('<str:subject>/grades', views.keyGrade, name='keyGrade'),

    path('users/create/username', views.checkUserIfExited, name='checkUserIfExited'),
    path('users/edit/username', views.checkUserIfExitedOfEditing, name='checkUserIfExitedOfEditing'),
]

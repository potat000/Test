#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: views.py 2803 2023-01-14 15:28:08Z Jolin $
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

from django.contrib import auth, messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.core.paginator import Paginator
from django.db import connection, transaction
from django.db.models import Avg, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .forms import (ClazzForm, CreateStudentForm, CreateTeacherForm, TestForm,
                    UpdateStudentForm, UpdateTeacherForm)
from .models import Clazz, Grade, Semester, Test, User

TEST = {"段考": 1, "小考": 2}

def index(request):
    return render(request, "IndexPage.html")

@login_required()
def home(request):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    return render(request, "HomePage.html", locals())

class LoginView(View):
    def get(self, request):
        return render(request, "LoginPage.html")

    def post(self, request):
        accountName = request.POST.get("accountName")
        password = request.POST.get("password")
        user = authenticate(username=accountName, password=password)

        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return redirect(home)
            else:
                return redirect(index)
        else:
            errorMessage = "登入失敗，請再試一次！"
            return render(request, "LoginErrorPage.html", {"errorMessage": errorMessage})

def logout(request):
    auth.logout(request)
    messages.add_message(request, 20, '成功登出')
    return redirect(index)

class editSelfView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "main.editSelf"

    def get(self, request, userID):
        user = User.objects.get(id=userID)
        return render(request, "EditSelfInfoPage.html", {"user": user})

    def post(self, request, userID):
        u = User.objects.get(id=userID)
        if request.POST.get("action") == "修改密碼":
            return redirect(reverse("editPassword", kwargs={"userID": userID}))
        else:
            u.username = request.POST.get("accountName")
            u.name = request.POST.get("name")
            u.phoneNumber = request.POST.get("phoneNumber")
            u.save()
            messages.info(request, "已成功修改個人資料！")
            return redirect(reverse("editSelf", kwargs={"userID": userID}))


class editPasswordView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "main.editSelf"

    def get(self, request, userID):
        user = User.objects.get(id=userID)
        return render(request, "EditPasswordPage.html", {"user": user})

    def post(self, request, userID):
        user = User.objects.get(id=userID)
        newPassword = request.POST.get("newPassword")
        confirmedPassword = request.POST.get("confirmedPassword")
        if newPassword != confirmedPassword:
            errorMessage = "新密碼及確認密碼比對不合，兩者必須相同，請再試一次！"
            return render(request, "MessagePage.html", {"errorMessage": errorMessage})
        else:
            user.set_password(newPassword)
            user.save()
            auth.update_session_auth_hash(request, user)
            messages.info(request, "已成功修改密碼！")
            return redirect(reverse("editSelf", kwargs={"userID": userID}))

class ClassInfoView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "main.view_clazz"

    def get(self, request):
        searchName = request.GET.get("name")

        query = """
                SELECT c.id, c.enrolledYear, c.number, c.name, u.name
                FROM main_user u, main_user_groups ug, main_clazz c
                WHERE u.id = ug.user_id AND ug.group_id = 2 AND u.clazz_id = c.id [search]

                UNION

                SELECT c.id, c.enrolledYear, c.number, c.name, u.name
                FROM main_user u
                RIGHT OUTER JOIN main_clazz c
                ON u.clazz_id = c.id
                WHERE c.name
                NOT IN
                (SELECT DISTINCT c.name
                FROM main_user u, main_user_groups ug, main_clazz c
                WHERE u.id = ug.user_id AND ug.group_id = 2 AND u.clazz_id = c.id) [search]
            """
        searchCondition = f"AND c.name LIKE '%{searchName}%'"

        with connection.cursor() as cursor:
            if searchName:
                query = query.replace("[search]", searchCondition)
                cursor.execute(query)

            query = query.replace("[search]", "")
            cursor.execute(query)

            classList = cursor.fetchall()
        return render(request, "ClassInfoPage.html", {"classList": classList})

def autocompleteClassName(request):
    q = request.GET.get("term").capitalize()
    qs = Clazz.objects.filter(name__contains=q)
    result = []
    for clazz in qs:
        result.append(clazz.name)
    return JsonResponse(result, safe=False)

class CreateClassView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "main.add_clazz"
    template_name = "CreateClassPage.html"

    form = ClazzForm()
    def get(self, request):
        teacherList = User.teachers.all()
        return render(request, self.template_name, {"form": self.form, "teacherList": teacherList})

    def post(self, request):
        form = ClazzForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, "已成功新增班級！")

            teacher = request.POST.get("teacher")
            if teacher != "":
                chosenTeacher = User.teachers.get(id=request.POST.get("teacher"))
                if chosenTeacher.clazz == None:
                    chosenTeacher.clazz = form.instance
                    chosenTeacher.save()
                else:
                    messages.error(request, "該老師已有所屬班級，請於確認後修改！")
        else:
            errorList = []
            for field in form:
                for error in field.errors:
                    errorList.append(error)
            for e in errorList:
                messages.error(request, e)
        return redirect(reverse("classInfo"))

class UpdateClassView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "main.change_clazz"
    template_name = "EditClassPage.html"

    def get(self, request, classID):
        clazz = Clazz.objects.get(id=classID)
        originalTeacher = User.teachers.filter(clazz=classID)
        teacherList = User.teachers.all()
        form = ClazzForm(instance=clazz)

        contexts = {"classID": classID, "form": form, "originalTeacher": originalTeacher, "teacherList": teacherList}
        return render(request, self.template_name, contexts)

    def post(self, request, classID):
        clazz = Clazz.objects.get(id=classID)
        originalTeacher = User.teachers.filter(clazz=classID)
        form = ClazzForm(request.POST, instance=clazz)
        if form.is_valid():
            form.save()

            teacher = request.POST.get("teacher")
            if originalTeacher:
                if teacher == originalTeacher[0].id:
                    messages.info(request, "已成功編輯班級！")
                elif teacher == "":
                    originalTeacher[0].clazz = None
                    originalTeacher[0].save()
                else:
                    chosenTeacher = User.teachers.get(id=teacher)
                    if chosenTeacher.clazz == None:
                        chosenTeacher.clazz_id = classID
                        chosenTeacher.save()
                    else:
                        messages.error(request, "該老師已有所屬班級，請於確認後修改！")
            else:
                chosenTeacher = User.teachers.get(id=teacher)
                if chosenTeacher.clazz == None:
                    chosenTeacher.clazz_id = classID
                    chosenTeacher.save()
                else:
                    messages.error(request, "該老師已有所屬班級，請於確認後修改！")
        else:
            errorList = []
            for field in form:
                for error in field.errors:
                    errorList.append(error)
            for e in errorList:
                messages.error(request, e)
        return redirect(reverse("classInfo"))

class DeleteClassView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "main.delete_clazz"
    template_name = "DeleteClassPage.html"

    def get(self, request, classID):
        clazz = Clazz.objects.get(id=classID)
        teacher = User.teachers.filter(clazz=classID)
        return render(request, self.template_name, {"clazz": clazz, "teacher": teacher})

    def post(self, request, classID):
        clazz = Clazz.objects.get(id=classID)
        clazz.delete()
        messages.info(request, "已成功刪除班級！")
        return redirect(reverse("classInfo"))

@login_required()
@permission_required("main.view_semester")
def getSemesterInfo(request):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    semesterList = Semester.objects.all()
    return render(request, "SemesterInfoPage.html", locals())

@login_required()
@permission_required("main.add_semester")
def createSemester(request):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    originalSemester = Semester.objects.filter(isCurrent=True)
    if request.method == "POST":
        if originalSemester:
            originalSemester.update(isCurrent=False)

        name = request.POST.get("name")
        isCurrent = request.POST.get("isCurrent")
        Semester.objects.create(name=name, isCurrent=isCurrent)
        messages.info(request, "已成功新增學期！")
        return redirect(getSemesterInfo)
    return render(request, "CreateSemesterPage.html", locals())

@login_required()
@permission_required("main.change_semester")
def setCurrentSemester(request, semesterID):
    Semester.objects.filter(isCurrent=True).update(isCurrent=False)
    Semester.objects.filter(id=semesterID).update(isCurrent=True)
    messages.info(request, "已成功設定目前學期！")
    return redirect(getSemesterInfo)

@login_required()
@permission_required("main.delete_semester")
def deleteSemester(request, semesterID):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    semester = Semester.objects.get(id=semesterID)
    if request.method == "GET":
        return render(request, "DeleteSemesterPage.html", locals())
    elif request.method == "POST":
        semester.delete()
        messages.info(request, "已成功刪除學期！")
        return redirect(getSemesterInfo)
    else:
        return False

class TeacherInfoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "main.readTeacher"

    model = User
    template_name = "TeacherInfoPage.html"
    def get_queryset(self):
        searchName = self.request.GET.get("name")
        if searchName:
            queryset = User.teachers.filter(name__contains=searchName)
        else:
            queryset = User.teachers.all()
        return queryset

def autocompleteTeacherName(request):
    #if 'term' in request.GET:
    q = request.GET.get('term').capitalize()
    qs = User.teachers.filter(name__contains=q)
    result = []
    for teacher in qs:
        result.append(teacher.name)
    return JsonResponse(result, safe=False)

class CreateTeacherView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "main.createTeacher"
    template_name = "CreateTeacherPage.html"
    form_class = CreateTeacherForm

    def post(self, request):
        form = CreateTeacherForm(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.password = make_password(f.password)
            f.save()
            messages.info(request, "已成功新增老師！")

            user = User.objects.get(username=request.POST.get("username"))
            user.groups.add(User.TEACHER)
        else:
            errorList = []
            for field in form:
                for error in field.errors:
                    errorList.append(error)
            for e in errorList:
                messages.error(request, e)
        return redirect(reverse("teacherInfo"))

class UpdateTeacherView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "main.updateTeacher"
    template_name = "EditTeacherPage.html"

    def get(self, request, teacherID):
        teacher = User.teachers.get(id=teacherID)
        form = UpdateTeacherForm(instance=teacher)

        contexts = {"teacherID": teacherID, "form": form}
        return render(request, self.template_name, contexts)

    def post(self, request, teacherID):
        teacher = User.teachers.get(id=teacherID)
        form = UpdateTeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.info(request, "已成功編輯老師！")
        else:
            errorList = []
            for field in form:
                for error in field.errors:
                    errorList.append(error)
            for e in errorList:
                messages.error(request, e)
        return redirect(reverse("teacherInfo"))

"""
class DeleteTecherView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "main.deleteTeacher"
    template_name = "DeleteTeacherPage.html"

    def get(self, request, teacherID):
        teacher = User.teachers.get(id=teacherID)
        return render(request, self.template_name, {"teacher": teacher})

    def post(self, request, teacherID):
        teacher = User.teachers.get(id=teacherID)
        teacher.delete()
        messages.info(request, "已成功刪除老師！")
        return redirect(reverse("teacherInfo"))
"""

def deleteTeacher(request, teacherID):
    teacher = User.teachers.get(id=teacherID)
    teacher.delete()
    messages.info(request, "已成功刪除老師！")
    return redirect(reverse("teacherInfo"))

class StudentInfoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "main.readStudent"

    model = User
    template_name = "StudentInfoPage.html"
    paginate_by = 5

    def get_queryset(self):
        userGroup = self.request.user.groups.values_list('name', flat=True).first()
        searchName = self.request.GET.get("name")
        if searchName:
            if userGroup == "主任":
                queryset = User.students.filter(name__contains=searchName)
            elif userGroup == "老師":
                queryset = User.students.filter(Q(name__contains=searchName) & Q(clazz_id=self.request.user.clazz_id))
        else:
            if userGroup == "主任":
                queryset = User.students.all()
            elif userGroup == "老師":
                queryset = User.students.filter(clazz_id=self.request.user.clazz_id)
        return queryset

def getStudentScrollLoadingTable(request):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    searchName = request.GET.get("name")
    if searchName:
        if userGroup == "主任":
            students = User.students.filter(name__contains=searchName)
        elif userGroup == "老師":
            students = User.students.filter(Q(name__contains=searchName) & Q(clazz_id=request.user.clazz_id))
    else:
        if userGroup == "主任":
            students = User.students.all()
        elif userGroup == "老師":
            students = User.students.filter(clazz_id=request.user.clazz_id)
    #students = User.students.all()
    paginator = Paginator(students, 5)
    pageNumber = int(request.GET.get("page"))
    if pageNumber != 0:
        if pageNumber <= paginator.num_pages:
            studentList = paginator.get_page(pageNumber)
            html = render(request, "StudentScrollLoadingTable.html", {"studentList": studentList}).content
            html = html.decode("UTF-8")
        else:
            html = None
    else:
        html = None
    return JsonResponse({
        "html": html,
        "end_pagination": True if pageNumber >= paginator.num_pages else False,
    })

def autocompleteStudentName(request):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    q = request.GET.get("term").capitalize()
    if userGroup == "主任":
        qs = User.students.filter(name__contains=q)
    elif userGroup == "老師":
        qs = User.students.filter(name__contains=q, clazz_id=request.user.clazz_id)

    result = []
    for stu in qs:
        result.append(stu.name)
    return JsonResponse(result, safe=False)

class CreateStudentView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "main.createStudent"
    template_name = "CreateStudentPage.html"
    form_class = CreateStudentForm

    def post(self, request):
        userGroup = request.user.groups.values_list('id', flat=True).first()

        form = CreateStudentForm(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.password = make_password(f.password)

            if userGroup == User.DIRECTOR:
                f.save()
                User.objects.get(username=form.cleaned_data["username"]).groups.add(User.STUDENT)
            elif userGroup == User.TEACHER:
                f.clazz = request.user.clazz
                f.save()
                User.objects.get(username=form.cleaned_data["username"]).groups.add(request.POST.get("identity"))

            user = User.objects.get(username=form.cleaned_data["username"])
            currentSemester = Semester.objects.get(isCurrent=True)
            clazzTest = Test.objects.filter(clazz=user.clazz, semester=currentSemester)
            for i, test in enumerate(clazzTest):
                Grade.objects.create(score=0, semester=currentSemester, test=test, user=user)

            messages.info(request, "已成功新增學生！")
        else:
            errorList = []
            for field in form:
                for error in field.errors:
                    errorList.append(error)
            for e in errorList:
                messages.error(request, e)

        return redirect(reverse("studentInfo"))

class UpdateStudentView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "main.updateStudent"
    template_name = "EditStudentPage.html"

    def get(self, request, studentID):
        student = User.students.get(id=studentID)
        form = UpdateStudentForm(instance=student)

        contexts = {"studentID": studentID, "form": form}
        return render(request, self.template_name, contexts)

    def post(self, request, studentID):
        userGroup = request.user.groups.values_list('id', flat=True).first()

        student = User.students.get(id=studentID)
        form = UpdateStudentForm(request.POST, instance=student)
        if form.is_valid():
            if userGroup == User.DIRECTOR:
                form.save()
            elif userGroup == User.TEACHER:
                f = form.save(commit=False)
                f.clazz = request.user.clazz
                f.save()

                student.groups.clear()
                student.groups.add(request.POST.get("identity"))
                student.save()

            messages.info(request, "已成功編輯學生！")
        else:
            errorList = []
            for field in form:
                for error in field.errors:
                    errorList.append(error)
            for e in errorList:
                messages.error(request, e)
        return redirect(reverse("studentInfo"))

class DeleteStudentView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "main.deleteStudent"
    template_name = "DeleteStudentPage.html"

    def get(self, request, studentID):
        student = User.objects.get(id=studentID)
        return render(request, self.template_name, {"student": student})

    def post(self, request, studentID):
        student = User.objects.get(id=studentID)
        student.delete()
        messages.info(request, "已成功刪除學生！")
        return redirect(reverse("studentInfo"))

@login_required()
@permission_required("main.view_grade")
def getStudentGrade(request):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    yearList = Clazz.objects.order_by("enrolledYear").values_list("enrolledYear", flat=True).distinct()
    semesterList = Semester.objects.all()
    examList = Test.objects.filter(type=TEST["段考"]).values("name").distinct()
    contexts = {"userGroup": userGroup, "yearList": yearList, "semesterList": semesterList, "examList": examList}

    enrolledYear = request.GET.get("enrolledYear")
    semester = request.GET.get("semester")
    exam = request.GET.get("exam")

    if enrolledYear and semester and exam:
        studentList = User.students.filter(clazz__enrolledYear=int(enrolledYear))
        chineseGradeList = []
        englishGradeList = []
        mathGradeList = []
        for stu in studentList:
            try:
                c = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam) & Q(test__subject="chinese") & Q(user=stu)
                )
                chineseGradeList.append(c.score)
            except Grade.DoesNotExist:
                chineseGradeList.append(0)

            try:
                e = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam) & Q(test__subject="english") & Q(user=stu)
                )
                englishGradeList.append(e.score)
            except Grade.DoesNotExist:
                englishGradeList.append(0)

            try:
                m = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam) & Q(test__subject="math") & Q(user=stu)
                )
                mathGradeList.append(m.score)
            except Grade.DoesNotExist:
                mathGradeList.append(0)

        studentGradeList = []
        for i, data in enumerate(studentList):
            studentGradeList.append([
                studentList[i].name, studentList[i].clazz, chineseGradeList[i], englishGradeList[i], mathGradeList[i],
                round((chineseGradeList[i] + englishGradeList[i] + mathGradeList[i]) / 3, 2)
            ])
        rankedStudent = sorted(studentGradeList, key=lambda x: x[5], reverse=True)
        for j, data in enumerate(rankedStudent):
            rankedStudent[j].insert(0, j + 1)

        subject = ["chinese", "english", "math"]
        subjectAvgList = [
            Grade.objects.filter(
                test__clazz__enrolledYear=enrolledYear, semester__name=semester, test__name=exam, test__subject=i
            ).aggregate(avg=Avg("score")) for i in subject
        ]
        if rankedStudent:
            totalAvg = sum([i[6] for i in rankedStudent]) / len(rankedStudent)
        else:
            totalAvg = 0

        contexts = {
            "userGroup": userGroup,
            "yearList": yearList,
            "semesterList": semesterList,
            "examList": examList,
            "studentGradeList": rankedStudent,
            "averageList": subjectAvgList,
            "totalAvg": totalAvg
        }
    #    studentGradeList = Grade.objects.filter(Q(semester__name=semester) & Q(test__name=exam) & Q(user__clazz__enrolledYear=int(year))).order_by("-score")
    return render(request, "StudentGradePage.html", contexts)

@login_required()
@permission_required("main.view_grade")
def getClassGrade(request):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    yearList = Clazz.objects.order_by("enrolledYear").values_list("enrolledYear", flat=True).distinct()
    semesterList = Semester.objects.all()
    examList = Test.objects.filter(type=TEST["段考"]).values("name").distinct()
    contexts = {"userGroup": userGroup, "yearList": yearList, "semesterList": semesterList, "examList": examList}

    year = request.GET.get("enrolledYear")
    semester = request.GET.get("semester")
    exam = request.GET.get("exam")

    if year and semester and exam:
        clazzList = Clazz.objects.filter(enrolledYear=int(year))

        clazzGradeList = []
        subject = ["chinese", "english", "math"]
        for clazz in clazzList:
            clazzGradeList.append([
                Grade.objects.filter(test__subject=i, test__name=exam, user__clazz=clazz,
                                     semester__name=semester).aggregate(avg=Avg("score")) for i in subject
            ])

        gradeList = [[] for i in clazzList]
        for i, subject in enumerate(clazzGradeList):
            for grade in subject:
                if grade["avg"] == None:
                    gradeList[i].append(0)
                else:
                    gradeList[i].append(grade["avg"])
        avg = [sum(g) / len(g) for g in gradeList]
        for i, data in enumerate(avg): #append class's average
            clazzGradeList[i].append(data)

        for i, data in enumerate(clazzList): #insert class name
            clazzGradeList[i].insert(0, data)

        rankedClazz = sorted(clazzGradeList, key=lambda x: x[4], reverse=True)
        for j, data in enumerate(rankedClazz): #insert rank
            rankedClazz[j].insert(0, j + 1)

        subject = ["chinese", "english", "math"]
        subjectAvgList = [
            Grade.objects.filter(
                test__clazz__enrolledYear=year, semester__name=semester, test__name=exam, test__subject=i
            ).aggregate(avg=Avg("score")) for i in subject
        ]
        totalAvg = sum([i[5] for i in rankedClazz]) / len(rankedClazz)

        contexts = {
            "userGroup": userGroup,
            "yearList": yearList,
            "semesterList": semesterList,
            "examList": examList,
            "classGradeList": rankedClazz,
            "averageList": subjectAvgList,
            "totalAvg": totalAvg
        }
    return render(request, "ClassGradePage.html", contexts)

@login_required()
@permission_required("main.view_grade")
def getExamGradeOfTeacher(request):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    userClazz = request.user.clazz
    semesterList = Semester.objects.all()
    examList = Test.objects.filter(type=TEST["段考"], clazz=userClazz).values("name").distinct()
    contexts = {"userGroup": userGroup, "semesterList": semesterList, "examList": examList}

    semester = request.GET.get("semester")
    exam = request.GET.get("exam")

    if semester and exam:
        studentList = User.students.filter(clazz=userClazz)
        chineseGradeList = []
        englishGradeList = []
        mathGradeList = []
        for stu in studentList:
            try:
                c = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam) & Q(test__subject="chinese") & Q(user=stu)
                )
                chineseGradeList.append(c.score)
            except Grade.DoesNotExist:
                chineseGradeList.append(0)

            try:
                e = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam) & Q(test__subject="english") & Q(user=stu)
                )
                englishGradeList.append(e.score)
            except Grade.DoesNotExist:
                englishGradeList.append(0)

            try:
                m = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam) & Q(test__subject="math") & Q(user=stu)
                )
                mathGradeList.append(m.score)
            except Grade.DoesNotExist:
                mathGradeList.append(0)

        studentGradeList = []
        for i, data in enumerate(studentList):
            studentGradeList.append([
                studentList[i].name, chineseGradeList[i], englishGradeList[i], mathGradeList[i],
                round((chineseGradeList[i] + englishGradeList[i] + mathGradeList[i]) / 3, 2)
            ])
        rankedStudent = sorted(studentGradeList, key=lambda x: x[4], reverse=True)
        for j, data in enumerate(rankedStudent):
            rankedStudent[j].insert(0, j + 1)

        subject = ["chinese", "english", "math"]
        subjectAvgList = [
            Grade.objects.filter(semester__name=semester, test__subject=i, test__name=exam,
                                 user__clazz=userClazz).aggregate(avg=Avg("score")) for i in subject
        ]
        totalAvg = sum([i[5] for i in rankedStudent]) / len(rankedStudent)

        contexts = {
            "userGroup": userGroup,
            "semesterList": semesterList,
            "examList": examList,
            "studentGradeList": rankedStudent,
            "averageList": subjectAvgList,
            "totalAvg": totalAvg
        }

    return render(request, "ExamGradePageOfTeacher.html", contexts)

@login_required()
@permission_required("main.view_grade")
def getSubjectGrade(request):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    userClazz = request.user.clazz
    semesterList = Semester.objects.all()
    contexts = {"userGroup": userGroup, "semesterList": semesterList}

    semester = request.GET.get("semester")
    subject = request.GET.get("subject")

    if semester and subject:
        testList = Test.objects.filter(subject=subject, clazz=userClazz, semester__name=semester)
        studentList = User.students.filter(clazz_id=request.user.clazz_id)
        gradeList = [Grade.objects.filter(user=i, test__subject=subject) for i in studentList]
        studentAvgList = [i.aggregate(avg=Sum(F("score") * F("test__percentage") / 100)) for i in gradeList]

        zippedList = zip(studentList, gradeList, studentAvgList)
        rankedStudent = sorted(list(zippedList), key=lambda x: x[-1]["avg"], reverse=True)
        for j, data in enumerate(rankedStudent):
            rankedStudent[j] = (j + 1,) + rankedStudent[j]

        testAvgList = [Grade.objects.filter(test=i).aggregate(testAvg=Avg("score")) for i in testList]
        totalAvg = sum([i[-1]["avg"] for i in rankedStudent]) / len(rankedStudent)

        contexts = {
            "userGroup": userGroup,
            "semesterList": semesterList,
            "testList": testList,
            "list": rankedStudent,
            "allAvgList": testAvgList,
            "totalAvg": totalAvg
        }
    return render(request, "SubjectGradePage.html", contexts)

@login_required()
@permission_required("main.view_grade")
def getExamGradeOfStudent(request):
    user = request.user
    userGroup = user.groups.values_list('name', flat=True).first()
    semesterList = Semester.objects.all()
    examList = Test.objects.filter(type=TEST["段考"], clazz=user.clazz).values("name").distinct()
    contexts = {"userGroup": userGroup, "semesterList": semesterList, "examList": examList}

    semester = request.GET.get("semester")

    if semester:
        chineseGradeList = []
        englishGradeList = []
        mathGradeList = []
        for exam in examList:
            try:
                c = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam["name"]) & Q(test__subject="chinese") & Q(user=user)
                )
                chineseGradeList.append(c.score)
            except Grade.DoesNotExist:
                chineseGradeList.append(0.00)

            try:
                e = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam["name"]) & Q(test__subject="english") & Q(user=user)
                )
                englishGradeList.append(e.score)
            except Grade.DoesNotExist:
                englishGradeList.append(0.00)

            try:
                m = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam["name"]) & Q(test__subject="math") & Q(user=user)
                )
                mathGradeList.append(m.score)
            except Grade.DoesNotExist:
                mathGradeList.append(0.00)

        chineseGradeList.insert(0, "國文")
        englishGradeList.insert(0, "英文")
        mathGradeList.insert(0, "數學")
        studentGradeList = [chineseGradeList, englishGradeList, mathGradeList]

        examAvgList = [
            Grade.objects.filter(semester__name=semester, test__name=exam["name"],
                                 user=user).aggregate(avg=Avg("score")) for exam in examList
        ]

        contexts = {
            "userGroup": userGroup,
            "semesterList": semesterList,
            "examList": examList,
            "studentGradeList": studentGradeList,
            "examAvgList": examAvgList
        }

    return render(request, "ExamGradePageOfStudent.html", contexts)

@login_required()
@permission_required("main.view_grade")
def getSemesterGrade(request):
    user = request.user
    userGroup = user.groups.values_list('name', flat=True).first()
    semesterList = Semester.objects.all()
    contexts = {"userGroup": userGroup, "semesterList": semesterList}

    semester = request.GET.get("semester")
    subject = request.GET.get("subject")

    if semester and subject:
        gradeList = Grade.objects.filter(semester__name=semester, test__subject=subject, user=user)
        total = gradeList.aggregate(avg=Sum(F("score") * F("test__percentage") / 100))

        SUBJECT2CHINESE = {"chinese": "國文", "english": "英文", "math": "數學"}
        contexts = {
            "userGroup": userGroup,
            "subject": SUBJECT2CHINESE[subject],
            "semesterList": semesterList,
            "gradeList": gradeList,
            "total": total
        }

    return render(request, "SemesterGradePage.html", contexts)

class TestInfoView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "main.view_test"

    def get(self, request, subject):
        currentSemester = Semester.objects.get(isCurrent=True)
        testList = Test.objects.filter(clazz_id=request.user.clazz_id, semester_id=currentSemester, subject=subject)
        return render(request, "TestInfoPage.html", {"testList": testList, "subject": subject})

class CreateTestView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "main.add_test"
    template_name = "CreateTestPage.html"

    def get(self, request, subject):
        currentSemester = Semester.objects.get(isCurrent=True)
        totalPercentage = Test.objects.filter(clazz=request.user.clazz, semester=currentSemester,
                                              subject=subject).aggregate(t=Sum("percentage"))
        if totalPercentage["t"] != None and totalPercentage["t"] >= 100:
            messages.error(request, "考試占比總和已為 100%，，無法再新增考試！")
            return redirect(reverse("testInfo", kwargs={"subject": subject}))
        else:
            form = TestForm()
            return render(request, self.template_name, {"form": form, "subject": subject})

    def post(self, request, subject):
        form = TestForm(request.POST)
        if form.is_valid():
            currentSemester = Semester.objects.get(isCurrent=True)
            totalPercentage = Test.objects.filter(clazz=request.user.clazz, semester=currentSemester,
                                                  subject=subject).aggregate(t=Sum("percentage"))
            if totalPercentage["t"] + form.cleaned_data["percentage"] > 100:
                messages.error(request, "新增此考試後將超過 100%，無法新增此考試！")
            else:
                f = form.save(commit=False)
                f.subject = subject
                f.clazz_id = request.user.clazz_id
                f.semester_id = Semester.objects.get(isCurrent=True).id
                f.save()

                userList = User.students.filter(clazz_id=request.user.clazz_id)
                for user in userList:
                    Grade.objects.create(
                        score=0, semester=Semester.objects.get(isCurrent=True), test=form.instance, user_id=user.id
                    )

                messages.info(request, "已成功新增考試！")
        else:
            errorList = []
            for field in form:
                for error in field.errors:
                    errorList.append(error)
            for e in errorList:
                messages.error(request, e)
        return redirect(reverse("testInfo", kwargs={"subject": subject}))

class UpdateTestView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "main.change_test"
    template_name = "EditTestPage.html"

    def get(self, request, subject, testID):
        test = Test.objects.get(id=testID)
        form = TestForm(instance=test)
        return render(request, self.template_name, {"subject": subject, "testID": testID, "form": form})

    def post(self, request, subject, testID):
        test = Test.objects.get(id=testID)
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            currentSemester = Semester.objects.get(isCurrent=True)
            totalPercentage = Test.objects.filter(clazz=request.user.clazz, semester=currentSemester,
                                                  subject=subject).aggregate(t=Sum("percentage"))
            if totalPercentage["t"] - test.percentage + form.cleaned_data["percentage"] > 100:
                messages.error(request, "修改此考試占比後將超過 100%，無法修改此考試！")
            else:
                form.save()
                messages.info(request, "已成功編輯考試！")
        else:
            errorList = []
            for field in form:
                for error in field.errors:
                    errorList.append(error)
            for e in errorList:
                messages.error(request, e)
        return redirect(reverse("testInfo", kwargs={"subject": subject}))

class DeleteTestView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "main.delete_test"
    template_name = "DeleteTestPage.html"

    def get(self, request, subject, testID):
        test = Test.objects.get(id=testID)
        return render(request, "DeleteTestPage.html", {"subject": subject, "test": test})

    def post(self, request, subject, testID):
        test = Test.objects.get(id=testID)
        test.delete()
        messages.info(request, "已成功刪除考試！")
        return redirect(reverse("testInfo", kwargs={"subject": subject}))

@login_required()
@permission_required("main.change_grade")
@transaction.atomic
def keyGrade(request, subject):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    if request.method == "GET":
        currentSemester = Semester.objects.get(isCurrent=True)
        testList = Test.objects.filter(clazz_id=request.user.clazz_id, semester_id=currentSemester, subject=subject)
        studentList = User.students.filter(clazz_id=request.user.clazz_id)
        gradeList = [Grade.objects.filter(user=i, test__subject=subject, semester=currentSemester) for i in studentList]
        studentAvgList = [i.aggregate(avg=Sum(F("score") * F("test__percentage") / 100)) for i in gradeList]
        testAvgList = [Grade.objects.filter(test=i).aggregate(testAvg=Avg("score")) for i in testList]
        totalAvg = sum([i["avg"] for i in studentAvgList]) / len(studentAvgList)

        contexts = {
            "userGroup": userGroup,
            "currentSemester": currentSemester,
            "testList": testList,
            "subject": subject,
            "list": zip(studentList, gradeList, studentAvgList),
            "allAvgList": testAvgList,
            "totalAvg": totalAvg
        }
        return render(request, "GradeTablePage.html", contexts)
    elif request.method == "POST":
        scoreList = request.POST.getlist("score[]")
        gradeIDList = request.POST.getlist("gradeID[]")

        zippedList = list(zip(gradeIDList, scoreList))
        for data in zippedList:
            if float(data[1]) > 100 or float(data[1]) < 0:
                messages.info(request, "分數不得小於 0 或大於 100！")
            else:
                #Grade.objects.get(id=data[0]).update(score=data[1])
                g = Grade.objects.get(id=data[0])
                g.score = data[1]
                g.save()
        messages.info(request, "已成功編輯成績！")
        return redirect(keyGrade, subject)
    else:
        return False

def checkUserIfExited(request):
    username = request.GET.get("username")
    user = User.objects.filter(username=username)
    if user:
        data = ["True"]
    else:
        data = ["False"]
    return JsonResponse(data, safe=False)

def checkUserIfExitedOfEditing(request):
    username = request.GET.get("username")
    phoneNumber = request.GET.get("phoneNumber")
    user = User.objects.filter(username=username)
    if user and user[0].phoneNumber != phoneNumber:
        data = ["True"]
    elif user and user[0].phoneNumber == phoneNumber:
        data = ["Pass"]
    else:
        data = ["False"]
    return JsonResponse(data, safe=False)

def sortByChineseGrade(request):
    userGroup = request.user.groups.values_list('name', flat=True).first()
    yearList = Clazz.objects.order_by("enrolledYear").values_list("enrolledYear", flat=True).distinct()
    semesterList = Semester.objects.all()
    examList = Test.objects.filter(type=TEST["段考"]).values("name").distinct()
    contexts = {"userGroup": userGroup, "yearList": yearList, "semesterList": semesterList, "examList": examList}

    enrolledYear = request.GET.get("enrolledYear")
    semester = request.GET.get("semester")
    exam = request.GET.get("exam")

    if enrolledYear and semester and exam:
        studentList = User.students.filter(clazz__enrolledYear=int(enrolledYear))
        chineseGradeList = []
        englishGradeList = []
        mathGradeList = []
        for stu in studentList:
            try:
                c = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam) & Q(test__subject="chinese") & Q(user=stu)
                )
                chineseGradeList.append(c.score)
            except Grade.DoesNotExist:
                chineseGradeList.append(0)

            try:
                e = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam) & Q(test__subject="english") & Q(user=stu)
                )
                englishGradeList.append(e.score)
            except Grade.DoesNotExist:
                englishGradeList.append(0)

            try:
                m = Grade.objects.get(
                    Q(semester__name=semester) & Q(test__name=exam) & Q(test__subject="math") & Q(user=stu)
                )
                mathGradeList.append(m.score)
            except Grade.DoesNotExist:
                mathGradeList.append(0)

        studentGradeList = []
        for i, data in enumerate(studentList):
            studentGradeList.append([
                studentList[i].name, studentList[i].clazz, chineseGradeList[i], englishGradeList[i], mathGradeList[i],
                round((chineseGradeList[i] + englishGradeList[i] + mathGradeList[i]) / 3, 2)
            ])
        rankedStudent = sorted(studentGradeList, key=lambda x: x[5], reverse=True)
        for j, data in enumerate(rankedStudent):
            rankedStudent[j].insert(0, j + 1)
        rankedStudent = sorted(studentGradeList, key=lambda x: x[3], reverse=True) # add

        subject = ["chinese", "english", "math"]
        subjectAvgList = [
            Grade.objects.filter(
                test__clazz__enrolledYear=enrolledYear, semester__name=semester, test__name=exam, test__subject=i
            ).aggregate(avg=Avg("score")) for i in subject
        ]
        if rankedStudent:
            totalAvg = sum([i[6] for i in rankedStudent]) / len(rankedStudent)
        else:
            totalAvg = 0

        contexts = {
            "userGroup": userGroup,
            "yearList": yearList,
            "semesterList": semesterList,
            "examList": examList,
            "studentGradeList": rankedStudent,
            "averageList": subjectAvgList,
            "totalAvg": totalAvg
        }
    html = render(request, "StudentGradeSortingPage.html", contexts).content
    html = html.decode("UTF-8")
    return JsonResponse([html], safe=False)

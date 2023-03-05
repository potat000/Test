#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: forms.py 1333 2022-05-02 09:31:24Z Jacky $
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
# $Author: Jacky $
# $Date: 2022-05-02 17:31:24 +0800 (週一, 02 五月 2022) $
# $Revision: 1333 $

from django import forms

from main.models import Server, Mode, App

from Deploy import checkRequirementsExisted, findSettings, grepData, getRepository, validateDomainFormat

PYTHON_VERSION_CHOICES = [
    ('3.8', '3.8'),
    ('3.7', '3.7'),
    ('3.6', '3.6'),
    ('2.7', '2.7'),
]

AP_SERVER_CHOICES = [
    ('gunicorn', 'gunicorn'),
    ('apache', 'apache'),
]

class AppForm(forms.ModelForm):
    companyName = forms.CharField(label='Company Name')
    projectName = forms.CharField(label='Project Name')
    projectPath = forms.CharField(label='Local Source Path')
    domain = forms.CharField()
    #server = forms.ModelChoiceField(label='Server which you want to deploy', queryset=Server.objects.all())
    pythonVersion = forms.ChoiceField(label='Python Version', choices=PYTHON_VERSION_CHOICES, initial='3.8')
    appIuppiter = forms.BooleanField(label='App Iuppiter', required=False, initial=False)
    appHaystack = forms.BooleanField(label='App Haystack', required=False, initial=False)
    apServer = forms.ChoiceField(label='Ap Server', choices=AP_SERVER_CHOICES, initial='gunicorn')
    ssl = forms.BooleanField(label='SSL', required=False, initial=True)

    def clean_companyName(self):
        companyName = self.cleaned_data['companyName']
        if not companyName[0].isupper():
            raise forms.ValidationError("First word of company name must be capitalized.")
        return companyName

    def clean_projectName(self):
        projectName = self.cleaned_data['projectName']
        if not projectName[0].isupper():
            raise forms.ValidationError("First word of project name must be capitalized.")
        return projectName

    def clean_projectPath(self):
        projectPath = self.cleaned_data['projectPath']

        # Check if 'requirements.txt' or 'REQUIEMENTS.txt' exists.
        requirementsExist = checkRequirementsExisted(projectPath)
        if not requirementsExist:
            raise forms.ValidationError(
                "The directory doesn't have 'requirements.txt' or 'REQUIREMENTS.txt': %s." % projectPath
            )

        # Find 'settings.py'.
        settingsPath = findSettings(projectPath)
        if not settingsPath:
            raise forms.ValidationError("The project doesn't have settings.py: %s." % projectPath)

        # Get 'APP_NAME'.
        appName = grepData(settingsPath, 'APP_NAME = ')
        if not appName:
            raise forms.ValidationError("Can't find settings.py, use '%s' as APP_NAME." % appName)

        # Get repository URL.
        repository = getRepository(projectPath)
        if not repository:
            raise forms.ValidationError("The project doesn't have repository URL: %s." % projectPath)

        return projectPath
    
    def clean_domain(self):
        domain = self.cleaned_data['domain']
        domainIsValidFormat = validateDomainFormat(domain)
        if not domainIsValidFormat:
            raise forms.ValidationError("The domain name is not in valid format: %s" % domain)

    class Meta:
        model = App
        fields = []

class BuildForm(forms.Form):

    server = forms.ModelChoiceField(queryset=Server.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeployForm(forms.Form):

    mode = forms.ChoiceField(choices=Mode.CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: serializers.py 1010 2021-04-08 13:15:49Z Lavender $
#
# Copyright (c) 2019 Nuwa Information Co., Ltd, All Rights Reserved.
#
# Licensed under the Proprietary License, 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at our web site.
#
# See the License for the specific language governing permissions and 
# limitations under the License.
#
# $Author: Lavender $
# $Date: 2019-04-24 11:34:18

from rest_framework import serializers

class BaseOperationSerializer(serializers.Serializer):
    server = serializers.CharField(max_length=120)
    user = serializers.CharField(max_length=120, required=False)
    password = serializers.CharField(max_length=120, required=False)
    keyName = serializers.CharField(max_length=120, required=False)
    mode = serializers.CharField(
        max_length=120, required=False, default='PRODUCTION')
    isVM = serializers.BooleanField(default=False, required=False)
    
    appName = serializers.CharField(max_length=120)
    callback = serializers.CharField(max_length=120, required=False)
    
    logFile = serializers.CharField(max_length=120, required=False)
    
class RegistryOperationSerializer(BaseOperationSerializer):
    registry = serializers.BooleanField(default=True, required=False)

class DatabaseOperationSerializer(BaseOperationSerializer):
    dbPassword = serializers.CharField(max_length=120, required=False)
    
class KeyOperationSerializer(serializers.Serializer):
    keyName = serializers.CharField(max_length=120, required=False)
    
class AddRemoveKeyOperationSerializer(serializers.Serializer):
    server = serializers.CharField(max_length=120)
    keyName = serializers.CharField(max_length=120, required=False)
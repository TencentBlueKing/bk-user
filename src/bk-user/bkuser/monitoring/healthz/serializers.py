# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from rest_framework import serializers


class IssueSerializer(serializers.Serializer):
    fatal = serializers.BooleanField(help_text="是否致命", default=False)
    description = serializers.CharField(help_text="问题描述", default="")


class DianosisSerializer(serializers.Serializer):
    system_name = serializers.CharField(help_text="探测的系统名称")
    alive = serializers.BooleanField(help_text="探测的系统是否存活", default=True)
    issues = IssueSerializer(help_text="检查到的问题", many=True)

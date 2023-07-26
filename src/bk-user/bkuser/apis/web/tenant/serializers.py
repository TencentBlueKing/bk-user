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

from bkuser.biz.validators import validate_tenant_id


class TenantManagersCreateInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="管理员用户名")
    email = serializers.EmailField(help_text="管理员邮箱")
    telephone = serializers.CharField(help_text="管理员手机号")
    display_name = serializers.CharField(help_text="管理员全名")


class DataSourcePasswordInitInputSLZ(serializers.Serializer):
    init_password = serializers.CharField(help_text="初始化密码")
    init_password_method = serializers.CharField(help_text="初始化密码方式")
    init_notify_method = serializers.ListField(child=serializers.CharField(), help_text="账号初始化通知方式")
    init_mail_config = serializers.JSONField(help_text="账号初始化通知邮件模板")
    init_sms_config = serializers.JSONField(help_text="账号初始化通知短信模板")


class TenantCreateInputSlZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户ID", validators=[validate_tenant_id])
    name = serializers.CharField(help_text="租户名称")
    enabled_user_count_display = serializers.BooleanField(help_text="人数展示使能状态")
    logo = serializers.CharField(required=False, help_text="租户logo")
    password_settings = DataSourcePasswordInitInputSLZ()
    managers = serializers.ListSerializer(
        child=TenantManagersCreateInputSLZ(help_text="管理人设置"),
        help_text="管理人列表",
        allow_empty=False
    )


class TenantCreateOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户ID")


class TenantUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.CharField(required=False, help_text="租户名称")
    enabled_user_count_display = serializers.BooleanField(help_text="人数展示使能状态")
    manager_ids = serializers.ListField(
        child=serializers.CharField(),
        help_text="租户用户ID列表",
        allow_empty=False
    )


class TenantUpdateOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户ID")

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
from bkuser.biz.tenant_admin import (
    get_data_sources_info_by_tenant_id,
    get_managers_info_by_tenant_id,
    get_user_info_by_tenant_user_id,
)
from bkuser.biz.validators import validate_tenant_id

from django.conf import settings
from rest_framework import serializers


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


class TenantSearchSLZ(serializers.Serializer):
    name = serializers.CharField(required=False, help_text="租户名", allow_blank=True)


class TenantOutputSLZ(serializers.Serializer):
    create_time = serializers.CharField(required=False, help_text="创建时间")
    id = serializers.CharField(required=False, help_text="租户ID")
    name = serializers.CharField(required=False, help_text="租户名")
    enabled_user_count_display = serializers.BooleanField(required=False, help_text="是否展示租户下人员数目")
    managers = serializers.SerializerMethodField(required=False, help_text="租户管理员")
    data_sources = serializers.SerializerMethodField(required=False, help_text="租户数据源")
    logo = serializers.SerializerMethodField(required=False, help_text="租户名")

    def get_managers(self, obj):
        managers_info = get_managers_info_by_tenant_id(tenant_id=obj.id)
        managers = [
            {
                "id": m["id"],
                "username": m["username"],
                "display_name": m["display_name"],
                "email": get_user_info_by_tenant_user_id(tenant_user_id=m["id"], user_field="email"),
                "telephone": get_user_info_by_tenant_user_id(tenant_user_id=m["id"], user_field="telephone"),
            }
            for m in managers_info
        ]
        return managers

    def get_data_sources(self, obj):
        data_sources_info = get_data_sources_info_by_tenant_id(tenant_id=obj.id)

        data_sources = [{"id": d["id"], "name": d["name"]} for d in data_sources_info]
        return data_sources

    def get_logo(self, obj):
        logo = obj.logo
        if not logo:
            return settings.DEFAULT_LOGO_DATA
        return logo


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


class TenantDetailSLZ(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    enabled_user_count_display = serializers.BooleanField()
    managers = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField(required=False)

    def get_managers(self, obj):
        managers_info = get_managers_info_by_tenant_id(tenant_id=obj.id)
        managers = [
            {
                "id": m["id"],
                "username": m["username"],
                "display_name": m["display_name"],
                "email": get_user_info_by_tenant_user_id(tenant_user_id=m["id"], user_field="email"),
                "telephone": get_user_info_by_tenant_user_id(tenant_user_id=m["id"], user_field="telephone"),
            }
            for m in managers_info
        ]
        return managers

    def get_logo(self, obj):
        logo = obj.logo
        if not logo:
            return settings.DEFAULT_LOGO_DATA
        return logo


class TenantUsersSLZ(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField()
    logo = serializers.SerializerMethodField(required=False)

    def get_logo(self, obj):
        logo = obj.logo
        if not logo:
            return settings.DEFAULT_LOGO_DATA
        return logo

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
from typing import Dict, List

from django.conf import settings
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.biz.tenant import TenantUserHandler


class TenantDepartmentOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户部门ID")
    name = serializers.CharField(help_text="部门名称")
    has_children = serializers.BooleanField(help_text="是否有子部门")


class TenantUserDepartmentOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户用户ID")
    name = serializers.CharField(help_text="租户部门名称")


class TenantUserLeaderOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户用户ID")
    username = serializers.CharField(help_text="租户用户名")
    full_name = serializers.CharField(help_text="租户名称")


class TenantUserSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False)


class TenantDepartmentUserSearchInputSLZ(TenantUserSearchInputSLZ):
    recursive = serializers.BooleanField(help_text="包含子部门的人员", default=False)


class TenantUserInfoOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户ID")
    username = serializers.CharField(help_text="租户用户名", required=False)
    full_name = serializers.CharField(help_text="用户姓名", required=False)
    email = serializers.EmailField(help_text="用户邮箱", required=False)
    phone = serializers.CharField(help_text="用户手机号", required=False)
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )
    account_expired_at = serializers.SerializerMethodField(help_text="账号过期时间")
    departments = serializers.SerializerMethodField(help_text="用户所属部门")

    def get_account_expired_at(self, instance: TenantUser) -> str:
        return instance.account_expired_at_display


class TenantUserListOutputSLZ(TenantUserInfoOutputSLZ):
    @swagger_serializer_method(serializer_or_field=TenantUserDepartmentOutputSLZ(many=True))
    def get_departments(self, instance: TenantUser) -> List[Dict]:
        departments = self.context["tenant_user_departments"].get(instance.id) or []
        return [{"id": i.id, "name": i.name} for i in departments]

    def to_representation(self, instance: TenantUser) -> Dict:
        data = super().to_representation(instance)
        user_info = self.context["tenant_users_info"].get(instance.id)
        if user_info is not None:
            user = user_info.data_source_user
            data.update(
                {
                    "full_name": user.full_name,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "phone_country_code": user.phone_country_code,
                    "logo": user.logo or settings.DEFAULT_DATA_SOURCE_USER_LOGO,
                }
            )
        return data


class TenantUserRetrieveOutputSLZ(TenantUserInfoOutputSLZ):
    leaders = serializers.SerializerMethodField(help_text="用户上级")

    @swagger_serializer_method(serializer_or_field=TenantUserDepartmentOutputSLZ(many=True))
    def get_departments(self, instance: TenantUser) -> List[Dict]:
        tenant_user_departments = TenantUserHandler.get_tenant_user_departments_map_by_id([instance.id])
        departments = tenant_user_departments.get(instance.id) or []
        return [{"id": i.id, "name": i.name} for i in departments]

    @swagger_serializer_method(serializer_or_field=TenantUserLeaderOutputSLZ(many=True))
    def get_leaders(self, instance: TenantUser) -> List[Dict]:
        leaders = TenantUserHandler.get_tenant_user_leaders_map_by_id([instance.id]).get(instance.id) or []
        return [
            {
                "id": i.id,
                "username": i.username,
                "full_name": i.full_name,
            }
            for i in leaders
        ]

    def to_representation(self, instance: TenantUser) -> Dict:
        data = super().to_representation(instance)
        user = instance.data_source_user
        if user is not None:
            data.update(
                {
                    "full_name": user.full_name,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "phone_country_code": user.phone_country_code,
                    "logo": user.logo or settings.DEFAULT_DATA_SOURCE_USER_LOGO,
                }
            )
        return data


class TenantListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户ID")
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")
    departments = serializers.SerializerMethodField(help_text="租户下每个数据源的根组织")

    def get_logo(self, instance: Tenant) -> str:
        return instance.logo or settings.DEFAULT_TENANT_LOGO

    @swagger_serializer_method(serializer_or_field=TenantDepartmentOutputSLZ(many=True))
    def get_departments(self, instance: Tenant):
        departments = self.context["tenant_root_departments_map"].get(instance.id) or []
        return [item.model_dump(include={"id", "name", "has_children"}) for item in departments]


class TenantDepartmentChildrenListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户部门ID")
    name = serializers.CharField(help_text="部门名称")
    has_children = serializers.BooleanField(help_text="是否有子部门")

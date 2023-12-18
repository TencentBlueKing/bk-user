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
    id = serializers.IntegerField(help_text="租户部门ID")
    name = serializers.CharField(help_text="租户部门名称")


class TenantUserLeaderOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户ID")
    username = serializers.CharField(help_text="租户用户名")
    full_name = serializers.CharField(help_text="租户用户名称")


class TenantUserSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False)


class TenantDepartmentUserSearchInputSLZ(TenantUserSearchInputSLZ):
    recursive = serializers.BooleanField(help_text="包含子部门的人员", default=False)


class TenantUserInfoOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户ID")
    username = serializers.CharField(help_text="租户用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    email = serializers.EmailField(help_text="用户邮箱", source="data_source_user.email")
    phone = serializers.CharField(help_text="用户手机号", source="data_source_user.phone")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号",
        source="data_source_user.phone_country_code",
        default=settings.DEFAULT_PHONE_COUNTRY_CODE,
    )
    account_expired_at = serializers.SerializerMethodField(help_text="账号过期时间")
    departments = serializers.SerializerMethodField(help_text="用户所属部门")
    extras = serializers.JSONField(help_text="自定义字段", source="data_source_user.extras")

    def get_account_expired_at(self, obj: TenantUser) -> str:
        return obj.account_expired_at_display


class TenantUserListOutputSLZ(TenantUserInfoOutputSLZ):
    @swagger_serializer_method(serializer_or_field=TenantUserDepartmentOutputSLZ(many=True))
    def get_departments(self, obj: TenantUser) -> List[Dict]:
        departments = self.context["tenant_user_depts_map"].get(obj.id) or []
        return TenantUserDepartmentOutputSLZ(departments, many=True).data


class TenantUserRetrieveOutputSLZ(TenantUserInfoOutputSLZ):
    leaders = serializers.SerializerMethodField(help_text="用户上级")

    @swagger_serializer_method(serializer_or_field=TenantUserDepartmentOutputSLZ(many=True))
    def get_departments(self, obj: TenantUser) -> List[Dict]:
        tenant_user_depts_map = TenantUserHandler.get_tenant_users_depts_map(obj.tenant_id, [obj])
        depts = tenant_user_depts_map.get(obj.id) or []
        return TenantUserDepartmentOutputSLZ(depts, many=True).data

    @swagger_serializer_method(serializer_or_field=TenantUserLeaderOutputSLZ(many=True))
    def get_leaders(self, obj: TenantUser) -> List[Dict]:
        tenant_users_leader_infos = TenantUserHandler.get_tenant_user_leader_infos(obj)
        return TenantUserLeaderOutputSLZ(tenant_users_leader_infos, many=True).data


class TenantListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户ID")
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")
    departments = serializers.SerializerMethodField(help_text="租户下每个数据源的根组织")

    def get_logo(self, obj: Tenant) -> str:
        return obj.logo or settings.DEFAULT_TENANT_LOGO

    @swagger_serializer_method(serializer_or_field=TenantDepartmentOutputSLZ(many=True))
    def get_departments(self, obj: Tenant):
        return self.context["tenant_root_depts_map"].get(obj.id) or []


class TenantDepartmentChildrenListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户部门ID")
    name = serializers.CharField(help_text="部门名称")
    has_children = serializers.BooleanField(help_text="是否有子部门")

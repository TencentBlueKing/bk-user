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

from bkuser.apis.web.organization.serializers import TenantUserDepartmentOutputSLZ, TenantUserLeaderOutputSLZ
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.tenant import TenantUserHandler


class TenantBaseInfoOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户ID")
    name = serializers.CharField(help_text="租户名称")


class TenantUserBaseInfoOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户ID")
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="全名")
    tenant = TenantBaseInfoOutputSLZ(help_text="租户")


class NaturalUserRelatedTenantUserListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="自然人ID")
    full_name = serializers.CharField(help_text="自然人全名")
    tenant_users = serializers.ListField(help_text="自然人关联的租户账号列表", child=TenantUserBaseInfoOutputSLZ())


class TenantUserRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户ID")
    username = serializers.CharField(help_text="用户名", required=False)
    full_name = serializers.CharField(help_text="用户全名", required=False)
    logo = serializers.CharField(help_text="头像", required=False)

    # 邮箱信息
    is_inherited_email = serializers.BooleanField(help_text="是否继承数据源邮箱")
    email = serializers.EmailField(help_text="用户邮箱", required=False)
    custom_email = serializers.EmailField(help_text="自定义用户邮箱")

    # 手机号信息
    is_inherited_phone = serializers.BooleanField(help_text="是否继承数据源手机号")
    phone = serializers.CharField(help_text="用户手机号", required=False)
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )
    custom_phone = serializers.CharField(help_text="自定义用户手机号")
    custom_phone_country_code = serializers.CharField(help_text="自定义用户手机国际区号")

    account_expired_at = serializers.SerializerMethodField(help_text="账号过期时间")
    departments = serializers.SerializerMethodField(help_text="用户所属部门")
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

    def get_account_expired_at(self, instance: TenantUser) -> str:
        return instance.account_expired_at_display

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
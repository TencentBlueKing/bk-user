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

from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.biz.data_source import DataSourceSimpleInfo
from bkuser.biz.tenant import TenantHandler, TenantUserWithInheritedInfo
from bkuser.biz.validators import validate_tenant_id


class TenantManagerCreateInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="管理员用户名")
    full_name = serializers.CharField(help_text="管理员姓名")
    email = serializers.EmailField(help_text="管理员邮箱")
    # TODO: 手机号&区号补充校验
    phone = serializers.CharField(help_text="管理员手机号")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )


class TenantFeatureFlagSLZ(serializers.Serializer):
    user_number_visible = serializers.BooleanField(help_text="人员数量是否可见", default=True)


class TenantCreateInputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID", validators=[validate_tenant_id])
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.CharField(help_text="租户 Logo", required=False)
    managers = serializers.ListField(help_text="管理人列表", child=TenantManagerCreateInputSLZ(), allow_empty=False)
    feature_flags = TenantFeatureFlagSLZ(help_text="租户特性集")
    # TODO: 目前还没设计数据源，待开发本地数据源时再补充
    # password_config


class TenantCreateOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")


class TenantSearchInputSLZ(serializers.Serializer):
    name = serializers.CharField(required=False, help_text="租户名", allow_blank=True)


class TenantSearchManagerOutputSchema(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="姓名")


class TenantSearchDataSourceOutputSchema(serializers.Serializer):
    id = serializers.CharField(help_text="数据源 ID")
    name = serializers.CharField(help_text="数据源名称")


class TenantSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")
    created_at = serializers.SerializerMethodField(help_text="创建时间")
    managers = serializers.SerializerMethodField(help_text="租户管理员")
    data_sources = serializers.SerializerMethodField(help_text="租户数据源")

    def get_logo(self, obj: Tenant) -> str:
        return obj.logo or settings.DEFAULT_TENANT_LOGO

    def get_created_at(self, obj: Tenant) -> str:
        return obj.created_at_display

    @swagger_serializer_method(serializer_or_field=TenantSearchManagerOutputSchema(many=True))
    def get_managers(self, obj: Tenant) -> List[Dict]:
        tenant_manager_map: Dict[str, List[TenantUserWithInheritedInfo]] = self.context["tenant_manager_map"]
        managers = tenant_manager_map.get(obj.id) or []
        return [
            {
                "id": i.id,
                **i.data_source_user.model_dump(include={"username", "full_name"}),
            }
            for i in managers
        ]

    @swagger_serializer_method(serializer_or_field=TenantSearchDataSourceOutputSchema(many=True))
    def get_data_sources(self, obj: Tenant) -> List[Dict]:
        data_source_map: Dict[str, List[DataSourceSimpleInfo]] = self.context["data_source_map"]
        data_sources = data_source_map.get(obj.id) or []
        return [i.model_dump(include={"id", "name"}) for i in data_sources]


class TenantUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.CharField(help_text="租户 Logo", required=False, default=settings.DEFAULT_TENANT_LOGO)
    manager_ids = serializers.ListField(child=serializers.CharField(), help_text="租户用户 ID 列表", allow_empty=False)
    feature_flags = TenantFeatureFlagSLZ(help_text="租户特性集")


class TenantRetrieveManagerOutputSchema(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="租户用户名")
    full_name = serializers.CharField(help_text="用户姓名")
    email = serializers.EmailField(help_text="用户邮箱")
    phone = serializers.CharField(help_text="用户手机号")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )


class TenantRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")
    feature_flags = TenantFeatureFlagSLZ(help_text="租户特性集")
    managers = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=TenantRetrieveManagerOutputSchema(many=True))
    def get_managers(self, obj: Tenant) -> List[Dict]:
        # 根据当前登录的租户用户，获取租户ID
        # NOTE 因协同数据源而展示的租户，不返回管理员
        if obj.id != self.context["current_tenant_id"]:
            return []
        managers = TenantHandler.retrieve_tenant_managers(obj.id)
        return [
            {"id": manager.id, **manager.data_source_user.model_dump(include={"username", "full_name"})}
            for manager in managers
        ]

    def get_logo(self, obj: Tenant) -> str:
        return obj.logo or settings.DEFAULT_TENANT_LOGO


class TenantUserSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False)


class TenantUserSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="租户用户名", required=False)
    full_name = serializers.CharField(help_text="用户姓名", required=False)
    email = serializers.EmailField(help_text="用户邮箱", required=False)
    phone = serializers.CharField(help_text="用户手机号", required=False)
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )

    def to_representation(self, instance: TenantUser) -> Dict:
        data = super().to_representation(instance)
        data_source_user = DataSourceUser.objects.filter(id=instance.data_source_user_id).first()
        if data_source_user is not None:
            data["username"] = data_source_user.username
            data["full_name"] = data_source_user.full_name
            data["email"] = data_source_user.email
            data["phone"] = data_source_user.phone
            data["phone_country_code"] = data_source_user.phone_country_code
            data["logo"] = data_source_user.logo or settings.DEFAULT_DATA_SOURCE_USER_LOGO

        return data

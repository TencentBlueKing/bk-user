# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from typing import Any, Dict

from django.conf import settings
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.tenant.models import Tenant


class TenantDataSourceSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="数据源 ID")
    type = serializers.CharField(help_text="数据源类型")
    plugin_id = serializers.CharField(help_text="数据源插件 ID")
    enable_password = serializers.SerializerMethodField(help_text="是否启用密码")

    @swagger_serializer_method(serializer_or_field=serializers.BooleanField)
    def get_enable_password(self, obj: DataSource) -> bool:
        return bool(obj.plugin_config["enable_password"])


class TenantListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")

    def get_logo(self, obj: Tenant) -> str:
        return obj.logo or settings.DEFAULT_TENANT_LOGO


class TenantRetrieveOutputSLZ(TenantListOutputSLZ):
    data_source = serializers.SerializerMethodField(help_text="实名用户数据源信息")

    class Meta:
        ref_name = "organization.TenantRetrieveOutputSLZ"

    @swagger_serializer_method(serializer_or_field=TenantDataSourceSLZ())
    def get_data_source(self, obj: Tenant) -> Dict[str, Any] | None:
        data_source = DataSource.objects.filter(owner_tenant_id=obj.id, type=DataSourceTypeEnum.REAL).first()
        if not data_source:
            return None

        return TenantDataSourceSLZ(data_source).data


class RequiredTenantUserFieldOutputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="字段名称")
    display_name = serializers.CharField(help_text="字段展示名")
    tips = serializers.CharField(help_text="提示信息")

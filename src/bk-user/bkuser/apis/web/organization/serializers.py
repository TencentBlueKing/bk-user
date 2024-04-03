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
from typing import Any, Dict

from django.conf import settings
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.tenant.models import Tenant


class TenantDataSourceSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="数据源 ID")
    type = serializers.CharField(help_text="数据源类型")
    plugin_id = serializers.CharField(help_text="数据源插件 ID")


class TenantListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")

    def get_logo(self, obj: Tenant) -> str:
        return obj.logo or settings.DEFAULT_TENANT_LOGO


class TenantRetrieveOutputSLZ(TenantListOutputSLZ):
    # TODO (su) 评估是否需要与虚拟账号共享 API，也即包含虚拟账号数据源信息？
    data_source = serializers.SerializerMethodField(help_text="真实用户数据源信息")

    class Meta:
        ref_name = "organization.TenantRetrieveOutputSLZ"

    @swagger_serializer_method(serializer_or_field=TenantDataSourceSLZ())
    def get_data_source(self, obj: Tenant) -> Dict[str, Any] | None:
        data_source = DataSource.objects.filter(owner_tenant_id=obj.id, type=DataSourceTypeEnum.REAL).first()
        if not data_source:
            return None

        return {"id": data_source.id, "type": data_source.type, "plugin_id": data_source.plugin_id}


class TenantDepartmentListInputSLZ(serializers.Serializer):
    parent_department_id = serializers.IntegerField(help_text="父部门 ID（为 0 表示根部门）", default=0)


class TenantDepartmentListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称")
    has_children = serializers.BooleanField(help_text="是否有子部门")

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
from typing import List

from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from bkuser.apps.tenant.models import TenantUser


class TenantUserSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", min_length=2, max_length=64)


class TenantUserSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    status = serializers.CharField(help_text="用户状态")
    tenant_id = serializers.CharField(help_text="租户 ID")
    tenant_name = serializers.SerializerMethodField(help_text="租户名称")
    organization_paths = serializers.SerializerMethodField(help_text="组织路径")

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_tenant_name(self, obj: TenantUser) -> str:
        return self.context["tenant_name_map"].get(obj.tenant_id, "")

    @swagger_serializer_method(serializer_or_field=serializers.ListSerializer(child=serializers.CharField()))
    def get_organization_paths(self, obj: TenantUser) -> List[str]:
        return self.context["org_path_map"].get(obj.id, [])

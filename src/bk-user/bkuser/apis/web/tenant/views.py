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
import logging

from django.db import transaction
from rest_framework import generics
from rest_framework.response import Response

from bkuser.apis.web.tenant.constants import DEFAULT_DATA_SOURCE_NAME
from bkuser.apis.web.tenant.serializers import (
    TenantCreateInputSlZ,
    TenantCreateOutputSLZ,
)
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import Tenant
from bkuser.biz.data_source_handler import data_source_handler
from bkuser.biz.tenant_handler import tenant_handler

logger = logging.getLogger(__name__)


class TenantListCreateApi(generics.ListCreateAPIView):
    queryset = Tenant.objects.filter()
    serializer_class = TenantCreateOutputSLZ

    def post(self, request, *args, **kwargs):
        slz = TenantCreateInputSlZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        with transaction.atomic():
            # 初始化租户
            tenant = tenant_handler.create_tenant(data)
            # 初始化本地数据源（密码配置初始化，需要根据tenant_data的manager_password进行，owner为当前租户，命名为本地数据源）
            data_source = data_source_handler.create_data_source(name=DEFAULT_DATA_SOURCE_NAME, owner=tenant.id)
            # 更新初始化后的数据源密码配置
            password_settings: dict = data["password_settings"]
            data_source_handler.update_plugin_config(
                instance=data_source, update_data=password_settings, namespace="password"
            )

        with transaction.atomic():
            # 初始化管理员在数据源的信息
            # 创建数据源用户
            new_users: list[dict] = data["managers"]
            username_list = data_source_handler.create_data_source_users(data_source, new_users)

        # 租户用户初始化
        data_source_users = DataSourceUser.objects.filter(
            data_source_id=data_source.id, username__in=username_list
        ).values("id", "username")
        with transaction.atomic():
            # 绑定到数据源到租户
            tenant_handler.data_source_bind_tenant(data_source_id=data_source.id, tenant_id=tenant.id)
            # 从数据源绑定管理员到租户
            tenant_users = tenant_handler.data_source_users_bind_tenant(tenant.id, data_source_users, is_init=True)
            # 绑定权限
            manager_ids = [user.id for user in tenant_users]
            tenant_handler.update_tenant_managers(tenant.id, manager_ids, is_init=True)

        return Response(data=TenantCreateOutputSLZ(instance=tenant).data)

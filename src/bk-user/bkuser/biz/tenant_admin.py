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
from bkuser.apps.tenant.models import DataSource, DataSourceUser, TenantDataSourceBinding, TenantManager, TenantUser


def get_managers_info_by_tenant_id(tenant_id):
    manager_ids = TenantManager.objects.filter(tenant_id=tenant_id).values_list("tenant_user_id", flat=True)
    managers = TenantUser.objects.filter(id__in=manager_ids).values("id", "username", "display_name")
    return managers


def get_user_info_by_tenant_user_id(tenant_user_id, user_field):
    data_source_user_id = TenantUser.objects.get(id=tenant_user_id).data_source_user_id
    user_info = DataSourceUser.objects.filter(id=data_source_user_id).values(user_field).first()[user_field]
    return user_info


def get_data_sources_info_by_tenant_id(tenant_id):
    data_source_ids = TenantDataSourceBinding.objects.filter(tenant_id=tenant_id).values_list(
        "data_source_id", flat=True
    )
    data_sources_info = DataSource.objects.filter(id__in=data_source_ids).values("id", "name")
    return data_sources_info

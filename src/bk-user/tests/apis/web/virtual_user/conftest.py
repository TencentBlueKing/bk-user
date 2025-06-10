# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from typing import Dict

import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation

from tests.test_utils.tenant import sync_users_depts_to_tenant

pytestmark = pytest.mark.django_db


@pytest.fixture
def _init_tenant_users_depts(random_tenant, full_local_data_source) -> None:
    """初始化租户部门 & 租户用户"""
    sync_users_depts_to_tenant(random_tenant, full_local_data_source)


@pytest.fixture
def real_owner_ids(_init_tenant_users_depts):
    return list(TenantUser.objects.filter(data_source__type=DataSourceTypeEnum.REAL).values_list("id", flat=True))


@pytest.fixture
def virtual_user_data(_init_tenant_users_depts, real_owner_ids) -> Dict:
    return {
        "users": [
            {
                "tenant_user_id": "virtual_user_id_1",
                "username": "virtual_user_1",
                "full_name": "测试用户1",
                "app_codes": ["app1", "app2"],
                "owners": real_owner_ids[:3],
            },
            {
                "tenant_user_id": "virtual_user_id_2",
                "username": "virtual_user_2",
                "full_name": "测试用户2",
                "app_codes": ["app3"],
                "owners": real_owner_ids[3:5],
            },
            {
                "tenant_user_id": "virtual_user_id_3",
                "username": "virtual_user_3",
                "full_name": "测试用户3",
                "app_codes": ["app1", "app3", "app4"],
                "owners": real_owner_ids[5:8],
            },
        ],
    }


@pytest.fixture
def _init_virtual_user(random_tenant, virtual_user_data, bare_virtual_data_source):
    data_source = bare_virtual_data_source
    for user_data in virtual_user_data["users"]:
        data_source_user = DataSourceUser.objects.create(
            username=user_data["username"],
            code=user_data["username"],
            full_name=user_data["full_name"],
            data_source=data_source,
        )
        tenant_user = TenantUser.objects.create(
            id=user_data["tenant_user_id"],
            tenant=random_tenant,
            data_source=data_source,
            data_source_user=data_source_user,
        )
        # 创建 app_code 关联
        VirtualUserAppRelation.objects.bulk_create(
            [VirtualUserAppRelation(tenant_user=tenant_user, app_code=app_code) for app_code in user_data["app_codes"]]
        )
        # 创建责任人关联
        VirtualUserOwnerRelation.objects.bulk_create(
            [VirtualUserOwnerRelation(tenant_user=tenant_user, owner_id=owner_id) for owner_id in user_data["owners"]]
        )

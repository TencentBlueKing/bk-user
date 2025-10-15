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
import pytest
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from bkuser.biz.virtual_user import VirtualUserHandler

pytestmark = pytest.mark.django_db


class TestVirtualUserHandler:
    @pytest.fixture(autouse=True)
    def _initialize(self, _init_tenant_users_depts, random_tenant, bare_virtual_data_source):
        virtual_user_data = [
            {
                "username": "virtual_user_1",
                "full_name": "虚拟用户_1",
                "app_codes": ["app1", "app2"],
                "owners": ["zhangsan", "lisi"],
            },
            {
                "username": "virtual_user_2",
                "full_name": "虚拟用户_2",
                "app_codes": ["app3"],
                "owners": ["lisi", "wangwu", "zhaoliu", "liuqi"],
            },
            {
                "username": "virtual_user_3",
                "full_name": "虚拟用户_3",
                "app_codes": ["app4", "app5"],
                "owners": ["maiba", "yangjiu", "lushi"],
            },
        ]

        for virtual_user in virtual_user_data:
            username = virtual_user["username"]

            # 创建数据源用户
            data_source_user = DataSourceUser.objects.create(
                username=username,
                code=username,
                full_name=virtual_user["full_name"],
                data_source=bare_virtual_data_source,
            )
            # 创建租户用户
            tenant_user = TenantUser.objects.create(
                id=username,
                tenant=random_tenant,
                data_source_user=data_source_user,
                data_source=bare_virtual_data_source,
            )
            # 创建 app_code 关联
            VirtualUserHandler.add_app_codes(tenant_user, list(virtual_user["app_codes"]))
            # 创建责任人关联
            VirtualUserHandler.add_owners(tenant_user, list(virtual_user["owners"]))

    def test_create(self, bare_virtual_data_source):
        VirtualUserHandler.create(bare_virtual_data_source, "test_username", "test_full_name")
        assert TenantUser.objects.filter(
            data_source=bare_virtual_data_source, data_source_user__username="test_username"
        ).exists()

        ds_user = DataSourceUser.objects.get(data_source=bare_virtual_data_source, username="test_username")
        assert ds_user.full_name == "test_full_name"

    def test_update_app_codes(self, random_tenant):
        tenant_user = TenantUser.objects.get(id="virtual_user_1")
        VirtualUserHandler.update_app_codes(tenant_user, ["app1", "app3"])
        assert set(
            VirtualUserAppRelation.objects.filter(tenant_user=tenant_user).values_list("app_code", flat=True)
        ) == {"app1", "app3"}

    def test_update_owners(self, random_tenant):
        tenant_user = TenantUser.objects.get(id="virtual_user_1")
        VirtualUserHandler.update_owners(tenant_user, ["zhangsan", "wangwu"])
        assert set(
            VirtualUserOwnerRelation.objects.filter(tenant_user=tenant_user).values_list("owner", flat=True)
        ) == {"zhangsan", "wangwu"}

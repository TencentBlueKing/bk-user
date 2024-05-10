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
import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.tenant.constants import CollaborationStrategyStatus
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from django.urls import reverse
from rest_framework import status

from tests.test_utils.data_source import init_data_source_users_depts_and_relations
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import sync_users_depts_to_tenant

pytestmark = pytest.mark.django_db


class TestCollaborationStrategyListApi:
    def test_standard(self, api_client, random_tenant, collaborate_to_strategy):
        resp = api_client.get(reverse("collaboration.to-strategy.list_create"))
        assert len(resp.data) == 1

        strategy = resp.data[0]
        assert strategy["id"] == collaborate_to_strategy.id
        assert strategy["target_tenant_id"] == collaborate_to_strategy.target_tenant_id


class TestCollaborationStrategyCreateApi:
    def test_standard(self, api_client, random_tenant, collaboration_tenant, strategy_source_config):
        resp = api_client.post(
            reverse("collaboration.to-strategy.list_create"),
            data={
                "name": generate_random_string(),
                "target_tenant_id": collaboration_tenant.id,
                "source_config": strategy_source_config,
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_collaborate_to_invalid_tenant(self, api_client, random_tenant, strategy_source_config):
        url = reverse("collaboration.to-strategy.list_create")
        resp_body = {
            "name": generate_random_string(),
            "target_tenant_id": random_tenant.id,
            "source_config": strategy_source_config,
        }

        resp = api_client.post(url, data=resp_body)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "目标租户不能是当前租户" in resp.data["message"]

        resp_body["target_tenant_id"] = "not_exists"
        resp = api_client.post(url, data=resp_body)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "目标租户不存在" in resp.data["message"]

    def test_create_with_invalid_source_config(self, api_client, random_tenant, collaboration_tenant):
        url = reverse("collaboration.to-strategy.list_create")
        resp_body = {
            "name": generate_random_string(),
            "target_tenant_id": collaboration_tenant.id,
            "source_config": {},
        }

        resp = api_client.post(url, data=resp_body)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "策略配置不合法" in resp.data["message"]


class TestCollaborationStrategyUpdateApi:
    def test_standard(self, api_client, random_tenant, collaborate_to_strategy):
        resp = api_client.put(
            reverse("collaboration.to-strategy.update_destroy", kwargs={"id": collaborate_to_strategy.id}),
            data={"name": "new_name", "source_config": collaborate_to_strategy.source_config},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        collaborate_to_strategy.refresh_from_db()
        assert collaborate_to_strategy.name == "new_name"

    def test_update_with_old_name(self, api_client, random_tenant, collaborate_to_strategy):
        resp = api_client.put(
            reverse("collaboration.to-strategy.update_destroy", kwargs={"id": collaborate_to_strategy.id}),
            data={"name": collaborate_to_strategy.name, "source_config": collaborate_to_strategy.source_config},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_update_source_config(self, api_client, random_tenant, collaborate_to_strategy, strategy_source_config):
        # 目前不支持范围，所以这里随便的 dict 配置都是 ok 的，后面改建模了，这个单测会挂，需要同步调整
        strategy_source_config["field_scope_config"] = {"a": "b", "c": ["d", "e"]}
        resp = api_client.put(
            reverse("collaboration.to-strategy.update_destroy", kwargs={"id": collaborate_to_strategy.id}),
            data={"name": "new_name", "source_config": strategy_source_config},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT


class TestCollaborationStrategyDestroyApi:
    def test_standard(
        self,
        api_client,
        random_tenant,
        collaboration_tenant,
        collaborate_to_strategy,
        local_ds_plugin,
        local_ds_plugin_cfg,
    ):
        # 初始化数据 & 向被协同的租户同步数据
        data_source = DataSource.objects.create(
            owner_tenant_id=random_tenant.id,
            type=DataSourceTypeEnum.REAL,
            plugin=local_ds_plugin,
            plugin_config=LocalDataSourcePluginConfig(**local_ds_plugin_cfg),
        )
        init_data_source_users_depts_and_relations(data_source)
        sync_users_depts_to_tenant(collaboration_tenant, data_source)

        # 先停用，待会才能删除
        collaborate_to_strategy.source_status = CollaborationStrategyStatus.DISABLED
        collaborate_to_strategy.save()

        queryset_filters = {
            "tenant": collaboration_tenant,
            "data_source__owner_tenant_id": random_tenant.id,
        }
        assert TenantUser.objects.filter(**queryset_filters).exists()
        assert TenantDepartment.objects.filter(**queryset_filters).exists()

        resp = api_client.delete(
            reverse("collaboration.to-strategy.update_destroy", kwargs={"id": collaborate_to_strategy.id})
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        assert not TenantUser.objects.filter(**queryset_filters).exists()
        assert not TenantDepartment.objects.filter(**queryset_filters).exists()

    def test_delete_enabled_strategy(self, api_client, random_tenant, collaborate_to_strategy):
        """分享方没有停用，就直接删除策略"""
        resp = api_client.delete(
            reverse("collaboration.to-strategy.update_destroy", kwargs={"id": collaborate_to_strategy.id})
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "删除前需要先停用协同策略" in resp.data["message"]


class TestCollaborationToStrategySourceStatusUpdateApi:
    def test_standard(self, api_client, random_tenant, collaborate_to_strategy):
        url = reverse("collaboration.to-strategy.source-status.update", kwargs={"id": collaborate_to_strategy.id})

        resp = api_client.put(url)
        assert resp.status_code == status.HTTP_200_OK
        # 默认是 enabled，切换一次变成 disabled
        assert resp.data["source_status"] == CollaborationStrategyStatus.DISABLED

        resp = api_client.put(url)
        assert resp.status_code == status.HTTP_200_OK
        # 再切换一次，变回 enabled
        assert resp.data["source_status"] == CollaborationStrategyStatus.ENABLED

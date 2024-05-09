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
from bkuser.apps.sync.constants import SyncTaskTrigger
from bkuser.apps.sync.data_models import TenantSyncOptions
from bkuser.apps.sync.managers import TenantSyncManager
from bkuser.apps.tenant.constants import CollaborationStrategyStatus
from bkuser.apps.tenant.models import TenantUserCustomField
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from django.urls import reverse
from rest_framework import status

from tests.test_utils.data_source import init_data_source_users_depts_and_relations

pytestmark = pytest.mark.django_db


class TestCollaborationFromStrategyListApi:
    def test_standard(
        self, api_client, random_tenant, collaborate_from_strategy, strategy_source_config, strategy_target_config
    ):
        resp = api_client.get(reverse("collaboration.from-strategy.list"))
        assert len(resp.data) == 1

        strategy = resp.data[0]
        assert strategy["id"] == collaborate_from_strategy.id
        assert strategy["source_tenant_id"] == collaborate_from_strategy.source_tenant_id
        # 刚刚新建的策略，接受方状态是未确认的
        assert strategy["target_status"] == CollaborationStrategyStatus.UNCONFIRMED
        assert strategy["source_config"] == strategy_source_config
        assert strategy["target_config"] == strategy_target_config


class TestCollaborationStrategySourceTenantCustomFieldListApi:
    @pytest.mark.usefixtures("_init_collaboration_tenant_custom_fields")
    def test_standard(self, api_client, random_tenant, collaboration_tenant, collaborate_from_strategy):
        resp = api_client.get(
            reverse(
                "collaboration.from-strategy.source-tenant-custom-fields.list",
                kwargs={"id": collaborate_from_strategy.id},
            )
        )
        assert len(resp.data) == 3  # noqa: PLR2004
        assert [field["name"] for field in resp.data] == [
            f"{collaboration_tenant.id}-{f}" for f in ["age", "gender", "region"]
        ]


class TestCollaborationFromStrategyUpdateApi:
    @pytest.mark.usefixtures("_init_random_tenant_custom_fields")
    @pytest.mark.usefixtures("_init_collaboration_tenant_custom_fields")
    def test_standard(
        self, api_client, random_tenant, collaboration_tenant, collaborate_from_strategy, strategy_target_config
    ):
        # 先确认一下策略，不然没法更新
        collaborate_from_strategy.target_status = CollaborationStrategyStatus.ENABLED
        collaborate_from_strategy.save()

        resp = api_client.put(
            reverse("collaboration.from-strategy.update", kwargs={"id": collaborate_from_strategy.id}),
            data={"target_config": strategy_target_config},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.usefixtures("_init_random_tenant_custom_fields")
    @pytest.mark.usefixtures("_init_collaboration_tenant_custom_fields")
    def test_update_target_organization_scope_config(
        self, api_client, random_tenant, collaborate_from_strategy, strategy_target_config
    ):
        # 先确认一下策略，不然没法更新
        collaborate_from_strategy.target_status = CollaborationStrategyStatus.ENABLED
        collaborate_from_strategy.save()

        # 目前不支持范围，所以这里随便的 dict 配置都是 ok 的，后面改建模了，这个单测会挂，需要同步调整
        strategy_target_config["organization_scope_config"] = {"a": "b", "c": ["d", "e"]}
        resp = api_client.put(
            reverse("collaboration.from-strategy.update", kwargs={"id": collaborate_from_strategy.id}),
            data={"target_config": strategy_target_config},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_update_with_invalid_target_config(self, api_client, random_tenant, collaborate_from_strategy):
        # 先确认一下策略，不然没法更新
        collaborate_from_strategy.target_status = CollaborationStrategyStatus.ENABLED
        collaborate_from_strategy.save()

        resp = api_client.put(
            reverse("collaboration.from-strategy.update", kwargs={"id": collaborate_from_strategy.id}),
            data={"target_config": {}},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "策略配置不合法" in resp.data["message"]

    def test_update_before_confirmed(
        self, api_client, random_tenant, collaborate_from_strategy, strategy_target_config
    ):
        resp = api_client.put(
            reverse("collaboration.from-strategy.update", kwargs={"id": collaborate_from_strategy.id}),
            data={"target_config": strategy_target_config},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "该协同策略未确认，无法进行更新" in resp.data["message"]


class TestCollaborationFromStrategyConfirmApi:
    @pytest.mark.usefixtures("_init_random_tenant_custom_fields")
    @pytest.mark.usefixtures("_init_collaboration_tenant_custom_fields")
    def test_standard(self, api_client, random_tenant, collaborate_from_strategy, strategy_target_config):
        resp = api_client.put(
            reverse("collaboration.from-strategy.confirm", kwargs={"id": collaborate_from_strategy.id}),
            data={"target_config": strategy_target_config},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        collaborate_from_strategy.refresh_from_db()
        assert collaborate_from_strategy.target_status == CollaborationStrategyStatus.ENABLED

    @pytest.mark.usefixtures("_init_collaboration_tenant_custom_fields")
    def test_update_with_not_exists_target_tenant_custom_fields(
        self, api_client, random_tenant, collaborate_from_strategy, strategy_target_config
    ):
        resp = api_client.put(
            reverse("collaboration.from-strategy.confirm", kwargs={"id": collaborate_from_strategy.id}),
            data={"target_config": strategy_target_config},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不属于本租户用户自定义字段" in resp.data["message"]

    @pytest.mark.usefixtures("_init_random_tenant_custom_fields")
    def test_update_with_not_exists_source_tenant_custom_fields(
        self, api_client, random_tenant, collaborate_from_strategy, strategy_target_config
    ):
        resp = api_client.put(
            reverse("collaboration.from-strategy.confirm", kwargs={"id": collaborate_from_strategy.id}),
            data={"target_config": strategy_target_config},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不属于源租户用户自定义字段" in resp.data["message"]

    @pytest.mark.usefixtures("_init_random_tenant_custom_fields")
    @pytest.mark.usefixtures("_init_collaboration_tenant_custom_fields")
    def test_update_with_field_mapping_incompatible_type(
        self, api_client, random_tenant, collaboration_tenant, collaborate_from_strategy, strategy_target_config
    ):
        # 第一个和第二个字段映射，互相换一下源字段，导致字段类型不一致
        strategy_target_config["field_mapping"][0]["source_field"] = f"{collaboration_tenant.id}-gender"
        strategy_target_config["field_mapping"][1]["source_field"] = f"{collaboration_tenant.id}-age"

        resp = api_client.put(
            reverse("collaboration.from-strategy.confirm", kwargs={"id": collaborate_from_strategy.id}),
            data={"target_config": strategy_target_config},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "类型不一致" in resp.data["message"]

    @pytest.mark.usefixtures("_init_random_tenant_custom_fields")
    @pytest.mark.usefixtures("_init_collaboration_tenant_custom_fields")
    def test_update_with_field_mapping_incompatible_enums(
        self, api_client, random_tenant, collaboration_tenant, collaborate_from_strategy, strategy_target_config
    ):
        gender_field = TenantUserCustomField.objects.get(name=f"{collaboration_tenant.id}-gender")
        # 修改可选枚举，导致两边枚举值不一致
        gender_field.options = [{"id": "male", "value": "男"}, {"id": "female", "value": "女"}]
        gender_field.save()

        resp = api_client.put(
            reverse("collaboration.from-strategy.confirm", kwargs={"id": collaborate_from_strategy.id}),
            data={"target_config": strategy_target_config},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "枚举值不一致" in resp.data["message"]


class TestCollaborationFromStrategyTargetStatusUpdateApi:
    def test_standard(self, api_client, random_tenant, collaborate_from_strategy):
        # 先确认一下策略，不然没法更新状态的
        collaborate_from_strategy.target_status = CollaborationStrategyStatus.ENABLED
        collaborate_from_strategy.save()

        url = reverse("collaboration.from-strategy.target-status.update", kwargs={"id": collaborate_from_strategy.id})

        resp = api_client.put(url)
        assert resp.status_code == status.HTTP_200_OK
        # 默认是 enabled，切换一次变成 disabled
        assert resp.data["target_status"] == CollaborationStrategyStatus.DISABLED

        resp = api_client.put(url)
        assert resp.status_code == status.HTTP_200_OK
        # 再切换一次，变回 enabled
        assert resp.data["target_status"] == CollaborationStrategyStatus.ENABLED

    def test_update_unconfirmed_status(self, api_client, random_tenant, collaborate_from_strategy):
        resp = api_client.put(
            reverse("collaboration.from-strategy.target-status.update", kwargs={"id": collaborate_from_strategy.id})
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "请先确认策略，再尝试修改状态" in resp.data["message"]


class TestCollaborationSyncRecordListApi:
    def test_standard(
        self,
        api_client,
        random_tenant,
        collaboration_tenant,
        collaborate_from_strategy,
        local_ds_plugin,
        local_ds_plugin_cfg,
    ):
        # 初始化协同数据
        data_source = DataSource.objects.create(
            owner_tenant_id=collaboration_tenant.id,
            type=DataSourceTypeEnum.REAL,
            plugin=local_ds_plugin,
            plugin_config=LocalDataSourcePluginConfig(**local_ds_plugin_cfg),
        )
        init_data_source_users_depts_and_relations(data_source)

        sync_opts = TenantSyncOptions(async_run=False, trigger=SyncTaskTrigger.MANUAL)
        TenantSyncManager(data_source, collaborate_from_strategy.target_tenant_id, sync_opts).execute()

        resp = api_client.get(reverse("collaboration.sync-record.list"))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 1

        record = resp.data["results"][0]
        assert record["status"] == "success"
        assert record["source_tenant_id"] == collaboration_tenant.id
        assert record["summary"] == {
            "user": {"create": 11, "update": 0, "delete": 0},
            "department": {"create": 9, "update": 0, "delete": 0},
        }

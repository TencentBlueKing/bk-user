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
import datetime
from typing import Any, Dict, List

import pytest
from bkuser.apps.data_source.constants import DataSourceStatus, FieldMappingOperation
from bkuser.apps.data_source.models import DataSource, DataSourceSensitiveInfo
from bkuser.apps.sync.constants import SyncTaskStatus, SyncTaskTrigger
from bkuser.apps.sync.models import DataSourceSyncTask
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.constants import PasswordGenerateMethod
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from django.urls import reverse
from rest_framework import status

from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import DEFAULT_TENANT

pytestmark = pytest.mark.django_db


@pytest.fixture()
def data_source(request, local_ds_plugin, local_ds_plugin_cfg) -> DataSource:
    # 支持检查是否使用 random_tenant fixture 以生成不属于默认租户的数据源
    tenant_id = DEFAULT_TENANT
    if "random_tenant" in request.fixturenames:
        tenant_id = request.getfixturevalue("random_tenant").id

    return DataSource.objects.create(
        name=generate_random_string(),
        owner_tenant_id=tenant_id,
        plugin=local_ds_plugin,
        plugin_config=LocalDataSourcePluginConfig(**local_ds_plugin_cfg),
    )


@pytest.fixture()
def field_mapping(request) -> List[Dict]:
    """字段映射，不含自定义字段"""
    fields = ["username", "full_name", "phone_country_code", "phone", "email"]
    if "tenant_user_custom_fields" in request.fixturenames:
        fields += [f.name for f in request.getfixturevalue("tenant_user_custom_fields")]

    return [{"source_field": f, "mapping_operation": "direct", "target_field": f} for f in fields]


@pytest.fixture()
def sync_config() -> Dict[str, Any]:
    """数据源同步配置"""
    return {"sync_period": 30}


@pytest.fixture()
def data_source_sync_tasks(data_source) -> List[DataSourceSyncTask]:
    success_task = DataSourceSyncTask.objects.create(
        data_source=data_source,
        status=SyncTaskStatus.SUCCESS,
        has_warning=True,
        trigger=SyncTaskTrigger.CRONTAB,
        duration=datetime.timedelta(seconds=5),
        logs="sync task success!",
        extras={"async_run": True, "overwrite": True},
    )
    failed_task = DataSourceSyncTask.objects.create(
        data_source=data_source,
        status=SyncTaskStatus.FAILED,
        has_warning=False,
        trigger=SyncTaskTrigger.MANUAL,
        duration=datetime.timedelta(minutes=5),
        logs="sync task failed!",
        extras={"async_run": True, "overwrite": True},
    )
    other_tenant_task = DataSourceSyncTask.objects.create(
        data_source_id=1,
        status=SyncTaskStatus.SUCCESS,
        has_warning=False,
        trigger=SyncTaskTrigger.SIGNAL,
        duration=datetime.timedelta(seconds=15),
        logs="sync task success!",
        extras={"async_run": True, "overwrite": True},
    )
    return [success_task, failed_task, other_tenant_task]


class TestDataSourcePluginListApi:
    def test_list(self, api_client):
        resp = api_client.get(reverse("data_source_plugin.list"))
        # 至少会有一个本地数据源插件
        assert len(resp.data) >= 1
        assert DataSourcePluginEnum.LOCAL in [d["id"] for d in resp.data]


class TestDataSourcePluginDefaultConfigApi:
    def test_retrieve(self, api_client):
        resp = api_client.get(reverse("data_source_plugin.default_config", args=[DataSourcePluginEnum.LOCAL.value]))
        assert resp.status_code == status.HTTP_200_OK

    def test_retrieve_not_exists(self, api_client):
        resp = api_client.get(reverse("data_source_plugin.default_config", args=["not_exists"]))
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestDataSourceCreateApi:
    def test_create_local_data_source(self, api_client, local_ds_plugin_cfg):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_cfg,
                # 本地数据源不需要字段映射配置
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_with_minimal_plugin_config(self, api_client):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": {"enable_account_password_login": False},
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_with_not_exist_plugin(self, api_client):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": "not_exist_plugin",
                "plugin_config": {},
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "数据源插件不存在" in resp.data["message"]

    def test_create_without_plugin_config(self, api_client):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={"name": generate_random_string(), "plugin_id": DataSourcePluginEnum.LOCAL},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "plugin_config: 该字段是必填项。" in resp.data["message"]

    def test_create_with_broken_plugin_config(self, api_client, local_ds_plugin_cfg):
        local_ds_plugin_cfg["password_initial"] = None
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_cfg,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "密码生成规则、初始密码设置、密码到期设置均不能为空" in resp.data["message"]

    def test_create_with_invalid_notification_template(self, api_client, local_ds_plugin_cfg):
        local_ds_plugin_cfg["password_expire"]["notification"]["templates"][0]["title"] = None
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_cfg,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "邮件通知模板需要提供标题" in resp.data["message"]

    def test_create_with_invalid_plugin_config(self, api_client, local_ds_plugin_cfg):
        local_ds_plugin_cfg.pop("enable_account_password_login")
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_cfg,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "插件配置不合法：enable_account_password_login: Field required" in resp.data["message"]

    def test_create_general_data_source(
        self, api_client, general_ds_plugin_cfg, tenant_user_custom_fields, field_mapping, sync_config
    ):
        """非本地数据源，需要提供字段映射"""
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.GENERAL,
                "plugin_config": general_ds_plugin_cfg,
                "field_mapping": field_mapping,
                "sync_config": sync_config,
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_without_required_field_mapping(self, api_client, general_ds_plugin_cfg, sync_config):
        """非本地数据源，需要字段映射配置"""
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.GENERAL,
                "plugin_config": general_ds_plugin_cfg,
                "field_mapping": [],
                "sync_config": sync_config,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "当前数据源类型必须配置字段映射" in resp.data["message"]

    def test_create_with_invalid_field_mapping_case_not_allowed_field(self, api_client, general_ds_plugin_cfg):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.GENERAL,
                "plugin_config": general_ds_plugin_cfg,
                "field_mapping": [
                    {
                        "source_field": "uname",
                        "mapping_operation": FieldMappingOperation.DIRECT,
                        "target_field": "xxx_username",
                    }
                ],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "字段映射中的目标字段 {'xxx_username'} 不属于用户自定义字段或内置字段" in resp.data["message"]

    def test_create_with_invalid_field_mapping_case_missed_field(self, api_client, general_ds_plugin_cfg):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.GENERAL,
                "plugin_config": general_ds_plugin_cfg,
                "field_mapping": [
                    {
                        "source_field": "uname",
                        "mapping_operation": FieldMappingOperation.DIRECT,
                        "target_field": "username",
                    }
                ],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "缺少字段映射" in resp.data["message"]

    def test_create_without_sync_config(self, api_client, general_ds_plugin_cfg, field_mapping):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.GENERAL,
                "plugin_config": general_ds_plugin_cfg,
                "field_mapping": field_mapping,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "当前数据源类型必须提供同步配置" in resp.data["message"]

    def test_create_with_invalid_sync_config(self, api_client, general_ds_plugin_cfg, field_mapping):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.GENERAL,
                "plugin_config": general_ds_plugin_cfg,
                "field_mapping": field_mapping,
                "sync_config": {"sync_period": -1},
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "sync_config.sync_period: “-1” 不是合法选项。" in resp.data["message"]


class TestDataSourceListApi:
    def test_list(self, api_client, data_source):
        resp = api_client.get(reverse("data_source.list_create"))
        assert len(resp.data) != 0

    def test_list_with_keyword(self, api_client, data_source):
        resp = api_client.get(reverse("data_source.list_create"), data={"keyword": data_source.name})
        assert len(resp.data) == 1

        ds = resp.data[0]
        assert ds["id"] == data_source.id
        assert ds["name"] == data_source.name
        assert ds["owner_tenant_id"] == data_source.owner_tenant_id
        assert ds["plugin_name"] == DataSourcePluginEnum.get_choice_label(DataSourcePluginEnum.LOCAL)
        assert ds["status"] == DataSourceStatus.ENABLED
        assert ds["cooperation_tenants"] == []

    def test_list_other_tenant_data_source(self, api_client, random_tenant, data_source):
        resp = api_client.get(reverse("data_source.list_create"), data={"keyword": data_source.name})
        # 无法查看到其他租户的数据源信息
        assert len(resp.data) == 0


class TestDataSourceUpdateApi:
    def test_update_local_data_source(self, api_client, data_source, local_ds_plugin_cfg):
        new_data_source_name = generate_random_string()
        local_ds_plugin_cfg["enable_account_password_login"] = False
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": data_source.id}),
            data={"name": new_data_source_name, "plugin_config": local_ds_plugin_cfg},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        resp = api_client.get(reverse("data_source.retrieve_update", kwargs={"id": data_source.id}))
        assert resp.data["name"] == new_data_source_name
        assert resp.data["plugin_config"]["enable_account_password_login"] is False

    def test_update_without_change_name(self, api_client, data_source, local_ds_plugin_cfg):
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": data_source.id}),
            data={"name": data_source.name, "plugin_config": local_ds_plugin_cfg},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_update_with_invalid_plugin_config(self, api_client, data_source, local_ds_plugin_cfg):
        local_ds_plugin_cfg.pop("enable_account_password_login")
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": data_source.id}),
            data={"name": generate_random_string(), "plugin_config": local_ds_plugin_cfg},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "插件配置不合法：enable_account_password_login: Field required" in resp.data["message"]

    def test_update_general_data_source(
        self, api_client, bare_general_data_source, general_ds_plugin_cfg, field_mapping, sync_config
    ):
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": bare_general_data_source.id}),
            data={
                "name": generate_random_string(),
                "plugin_config": general_ds_plugin_cfg,
                "field_mapping": field_mapping,
                "sync_config": sync_config,
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_update_without_required_field_mapping(
        self, api_client, bare_general_data_source, general_ds_plugin_cfg, sync_config
    ):
        """非本地数据源，需要字段映射配置"""
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": bare_general_data_source.id}),
            data={
                "name": generate_random_string(),
                "plugin_config": general_ds_plugin_cfg,
                "sync_config": sync_config,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data["message"] == "参数校验不通过: 当前数据源类型必须配置字段映射"

    def test_update_without_required_sync_config(
        self, api_client, bare_general_data_source, general_ds_plugin_cfg, field_mapping
    ):
        """非本地数据源，需要同步配置"""
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": bare_general_data_source.id}),
            data={
                "name": generate_random_string(),
                "plugin_config": general_ds_plugin_cfg,
                "field_mapping": field_mapping,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data["message"] == "参数校验不通过: 当前数据源类型必须提供同步配置"

    def test_update_with_sensitive_mask(
        self, api_client, bare_local_data_source, local_ds_plugin_cfg, field_mapping, sync_config
    ):
        """更新时候带上值为 ******* 的敏感字段，且之前已经在 DB 中有初始化过"""
        local_ds_plugin_cfg["password_initial"]["generate_method"] = PasswordGenerateMethod.FIXED
        local_ds_plugin_cfg["password_initial"]["fixed_password"] = "*******"
        DataSourceSensitiveInfo.objects.create(
            data_source=bare_local_data_source, key="password_initial.fixed_password", value="Pa-@-114514-2887"
        )
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": bare_local_data_source.id}),
            data={
                "name": generate_random_string(),
                "plugin_config": local_ds_plugin_cfg,
                "field_mapping": field_mapping,
                "sync_config": sync_config,
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_update_with_sensitive_mask_but_not_init(
        self, api_client, bare_local_data_source, local_ds_plugin_cfg, field_mapping, sync_config
    ):
        """更新时候带上值为 ******* 的敏感字段，但是之前没有在 DB 中有初始化过"""
        local_ds_plugin_cfg["password_initial"]["generate_method"] = PasswordGenerateMethod.FIXED
        local_ds_plugin_cfg["password_initial"]["fixed_password"] = "*******"
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": bare_local_data_source.id}),
            data={
                "name": generate_random_string(),
                "plugin_config": local_ds_plugin_cfg,
                "field_mapping": field_mapping,
                "sync_config": sync_config,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestDataSourceRetrieveApi:
    def test_retrieve(self, api_client, data_source):
        resp = api_client.get(reverse("data_source.retrieve_update", kwargs={"id": data_source.id}))
        assert resp.data["id"] == data_source.id
        assert resp.data["name"] == data_source.name
        assert resp.data["owner_tenant_id"] == data_source.owner_tenant_id
        assert resp.data["plugin"]["id"] == DataSourcePluginEnum.LOCAL
        assert resp.data["plugin"]["name"] == DataSourcePluginEnum.get_choice_label(DataSourcePluginEnum.LOCAL)
        assert resp.data["status"] == DataSourceStatus.ENABLED
        assert resp.data["plugin_config"] == data_source.plugin_config
        assert resp.data["sync_config"] == data_source.sync_config
        assert resp.data["field_mapping"] == data_source.field_mapping

    def test_retrieve_other_tenant_data_source(self, api_client, random_tenant, data_source):
        resp = api_client.get(reverse("data_source.retrieve_update", kwargs={"id": data_source.id}))
        # 无法查看到其他租户的数据源信息
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestDataSourceSwitchStatusApi:
    def test_switch(self, api_client, data_source):
        url = reverse("data_source.switch_status", kwargs={"id": data_source.id})
        # 默认启用，切换后不可用
        assert api_client.patch(url).data["status"] == DataSourceStatus.DISABLED
        # 再次切换，变成可用
        assert api_client.patch(url).data["status"] == DataSourceStatus.ENABLED

    def test_patch_other_tenant_data_source(self, api_client, random_tenant, data_source):
        resp = api_client.patch(reverse("data_source.switch_status", kwargs={"id": data_source.id}))
        # 无法操作其他租户的数据源信息
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestDataSourceSyncRecordApi:
    def test_list(self, api_client, data_source_sync_tasks):
        resp = api_client.get(reverse("data_source.sync_record.list"))
        # 不属于当前租户的数据源同步记录是看不到的
        tasks = resp.data["results"]
        assert len(tasks) == 2  # noqa: PLR2004
        assert set(tasks[0].keys()) == {
            "id",
            "data_source_id",
            "data_source_name",
            "status",
            "has_warning",
            "trigger",
            "operator",
            "start_at",
            "duration",
            "extras",
        }

    def test_list_with_filter(self, api_client, data_source_sync_tasks):
        resp = api_client.get(reverse("data_source.sync_record.list"), data={"status": "success"})
        assert len(resp.data["results"]) == 1  # noqa: PLR2004

    def test_retrieve(self, api_client, data_source_sync_tasks):
        success_task = data_source_sync_tasks[0]
        resp = api_client.get(reverse("data_source.sync_record.retrieve", kwargs={"id": success_task.id}))
        assert set(resp.data.keys()) == {"id", "status", "has_warning", "start_at", "duration", "logs"}

    def test_retrieve_other_tenant_data_source_sync_record(self, api_client, data_source_sync_tasks):
        other_tenant_task = data_source_sync_tasks[2]
        resp = api_client.get(reverse("data_source.sync_record.retrieve", kwargs={"id": other_tenant_task.id}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND

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

from urllib.parse import urlencode

import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum, FieldMappingOperation
from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourceSensitiveInfo, DataSourceUser
from bkuser.apps.idp.constants import INVALID_REAL_DATA_SOURCE_ID, IdpStatus
from bkuser.apps.idp.models import Idp, IdpSensitiveInfo
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.constants import PasswordGenerateMethod
from django.urls import reverse
from rest_framework import status

from tests.test_utils.tenant import sync_users_depts_to_tenant

pytestmark = pytest.mark.django_db


class TestDataSourceRandomPasswordApi:
    def test_generate_with_config(self, api_client, local_ds_plugin_cfg):
        resp = api_client.post(
            reverse("data_source.random_passwords"),
            data={"password_rule_config": local_ds_plugin_cfg["password_rule"]},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["password"] != ""

    def test_generate_with_data_source_id(self, api_client, data_source):
        resp = api_client.post(
            reverse("data_source.random_passwords"),
            data={"data_source_id": data_source.id},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["password"] != ""

    def test_generate_with_default_config(self, api_client):
        resp = api_client.post(reverse("data_source.random_passwords"))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["password"] != ""


class TestDataSourceCreateApi:
    def test_create_local_data_source(self, api_client, random_tenant, local_ds_plugin_cfg):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_cfg,
                # 本地数据源不需要字段映射配置
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_with_minimal_plugin_config(self, api_client, random_tenant):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": {"enable_password": False},
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_with_not_exist_plugin(self, api_client, random_tenant):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={"plugin_id": "not_exist_plugin", "plugin_config": {}},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "数据源插件不存在" in resp.data["message"]

    def test_create_without_plugin_config(self, api_client, random_tenant):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={"plugin_id": DataSourcePluginEnum.LOCAL},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "plugin_config: 该字段是必填项。" in resp.data["message"]

    def test_create_with_broken_plugin_config(self, api_client, random_tenant, local_ds_plugin_cfg):
        local_ds_plugin_cfg["password_initial"] = None
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_cfg,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "密码生成规则、初始密码设置、密码到期设置均不能为空" in resp.data["message"]

    def test_create_with_invalid_notification_template(self, api_client, random_tenant, local_ds_plugin_cfg):
        local_ds_plugin_cfg["password_expire"]["notification"]["templates"][0]["title"] = None
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_cfg,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "邮件通知模板需要提供标题" in resp.data["message"]

    def test_create_with_invalid_plugin_config(self, api_client, random_tenant, local_ds_plugin_cfg):
        local_ds_plugin_cfg.pop("enable_password")
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_cfg,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "插件配置不合法：enable_password: Field required" in resp.data["message"]

    def test_create_general_data_source(
        self, api_client, random_tenant, general_ds_plugin_cfg, tenant_user_custom_fields, field_mapping, sync_config
    ):
        """非本地数据源，需要提供字段映射"""
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "plugin_id": DataSourcePluginEnum.GENERAL,
                "plugin_config": general_ds_plugin_cfg,
                "field_mapping": field_mapping,
                "sync_config": sync_config,
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_without_required_field_mapping(
        self, api_client, random_tenant, general_ds_plugin_cfg, sync_config
    ):
        """非本地数据源，需要字段映射配置"""
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "plugin_id": DataSourcePluginEnum.GENERAL,
                "plugin_config": general_ds_plugin_cfg,
                "field_mapping": [],
                "sync_config": sync_config,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "当前数据源类型必须配置字段映射" in resp.data["message"]

    def test_create_with_invalid_field_mapping_case_not_allowed_field(
        self, api_client, random_tenant, general_ds_plugin_cfg
    ):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
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

    def test_create_with_invalid_field_mapping_case_missed_field(
        self, api_client, random_tenant, general_ds_plugin_cfg
    ):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
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

    def test_create_without_sync_config(self, api_client, random_tenant, general_ds_plugin_cfg, field_mapping):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "plugin_id": DataSourcePluginEnum.GENERAL,
                "plugin_config": general_ds_plugin_cfg,
                "field_mapping": field_mapping,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "当前数据源类型必须提供同步配置" in resp.data["message"]

    def test_create_with_invalid_sync_config(self, api_client, random_tenant, general_ds_plugin_cfg, field_mapping):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
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

    def test_list_with_type(self, api_client, data_source):
        resp = api_client.get(reverse("data_source.list_create"), data={"type": data_source.type})
        assert len(resp.data) == 1

        ds = resp.data[0]
        assert ds["id"] == data_source.id
        assert ds["type"] == data_source.type
        assert ds["owner_tenant_id"] == data_source.owner_tenant_id
        assert ds["plugin_id"] == DataSourcePluginEnum.LOCAL


class TestDataSourceUpdateApi:
    def test_update_local_data_source(self, api_client, data_source, local_ds_plugin_cfg):
        url = reverse("data_source.retrieve_update_destroy", kwargs={"id": data_source.id})
        local_ds_plugin_cfg["enable_password"] = False
        resp = api_client.put(url, data={"plugin_config": local_ds_plugin_cfg})
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        resp = api_client.get(url)
        assert resp.data["plugin_config"]["enable_password"] is False

    def test_update_with_invalid_plugin_config(self, api_client, data_source, local_ds_plugin_cfg):
        local_ds_plugin_cfg.pop("enable_password")
        resp = api_client.put(
            reverse("data_source.retrieve_update_destroy", kwargs={"id": data_source.id}),
            data={"plugin_config": local_ds_plugin_cfg},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "插件配置不合法：enable_password: Field required" in resp.data["message"]

    def test_update_general_data_source(
        self, api_client, bare_general_data_source, general_ds_plugin_cfg, field_mapping, sync_config
    ):
        resp = api_client.put(
            reverse("data_source.retrieve_update_destroy", kwargs={"id": bare_general_data_source.id}),
            data={
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
            reverse("data_source.retrieve_update_destroy", kwargs={"id": bare_general_data_source.id}),
            data={"plugin_config": general_ds_plugin_cfg, "sync_config": sync_config},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data["message"] == "参数校验不通过: 当前数据源类型必须配置字段映射"

    def test_update_without_required_sync_config(
        self, api_client, bare_general_data_source, general_ds_plugin_cfg, field_mapping
    ):
        """非本地数据源，需要同步配置"""
        resp = api_client.put(
            reverse("data_source.retrieve_update_destroy", kwargs={"id": bare_general_data_source.id}),
            data={"plugin_config": general_ds_plugin_cfg, "field_mapping": field_mapping},
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
            reverse("data_source.retrieve_update_destroy", kwargs={"id": bare_local_data_source.id}),
            data={
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
            reverse("data_source.retrieve_update_destroy", kwargs={"id": bare_local_data_source.id}),
            data={
                "plugin_config": local_ds_plugin_cfg,
                "field_mapping": field_mapping,
                "sync_config": sync_config,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestDataSourceRetrieveApi:
    def test_retrieve(self, api_client, data_source):
        resp = api_client.get(reverse("data_source.retrieve_update_destroy", kwargs={"id": data_source.id}))
        assert resp.data["id"] == data_source.id
        assert resp.data["owner_tenant_id"] == data_source.owner_tenant_id
        assert resp.data["type"] == DataSourceTypeEnum.REAL
        assert resp.data["plugin"]["id"] == DataSourcePluginEnum.LOCAL
        assert resp.data["plugin"]["name"] == DataSourcePluginEnum.get_choice_label(DataSourcePluginEnum.LOCAL)
        assert resp.data["plugin_config"] == data_source.plugin_config
        assert resp.data["sync_config"] == data_source.sync_config
        assert resp.data["field_mapping"] == data_source.field_mapping


class TestDataSourceDestroyApi:
    def test_destroy(self, api_client, data_source, idps, idp_sensitive_info):
        resp = api_client.delete(
            reverse("data_source.retrieve_update_destroy", kwargs={"id": data_source.id}),
            QUERY_STRING=urlencode({"is_delete_idp": False}, doseq=True),
        )

        assert resp.status_code == status.HTTP_204_NO_CONTENT

        assert not DataSource.objects.filter(id=data_source.id).exists()
        assert not DataSourceUser.objects.filter(data_source_id=data_source.id).exists()
        assert not DataSourceDepartment.objects.filter(data_source_id=data_source.id).exists()
        assert not DataSourceSensitiveInfo.objects.filter(data_source_id=data_source.id).exists()
        assert not Idp.objects.filter(
            data_source_id=data_source.id,
            owner_tenant_id=data_source.owner_tenant_id,
            plugin_id=BuiltinIdpPluginEnum.LOCAL,
        ).exists()
        assert Idp.objects.filter(
            status=IdpStatus.DISABLED,
            data_source_id=INVALID_REAL_DATA_SOURCE_ID,
            owner_tenant_id=data_source.owner_tenant_id,
        ).exists()
        assert (
            IdpSensitiveInfo.objects.filter(
                idp__in=Idp.objects.filter(
                    status=IdpStatus.DISABLED,
                    data_source_id=INVALID_REAL_DATA_SOURCE_ID,
                    owner_tenant_id=data_source.owner_tenant_id,
                )
            ).count()
            == 2  # noqa: PLR2004
        )

    def test_destroy_with_reset_idp_config(self, api_client, data_source, idps, idp_sensitive_info):
        resp = api_client.delete(
            reverse("data_source.retrieve_update_destroy", kwargs={"id": data_source.id}),
            QUERY_STRING=urlencode({"is_delete_idp": True}, doseq=True),
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        assert not DataSource.objects.filter(id=data_source.id).exists()
        assert not DataSourceUser.objects.filter(data_source_id=data_source.id).exists()
        assert not DataSourceDepartment.objects.filter(data_source_id=data_source.id).exists()
        assert not DataSourceSensitiveInfo.objects.filter(data_source_id=data_source.id).exists()
        assert not Idp.objects.filter(
            data_source_id=data_source.id, owner_tenant_id=data_source.owner_tenant_id
        ).exists()
        assert not IdpSensitiveInfo.objects.filter(idp_id=idps[1].id).exists()


class TestDataSourceRelatedResourceStatsApi:
    def test_list(self, api_client, full_local_data_source, default_tenant):
        sync_users_depts_to_tenant(default_tenant, full_local_data_source)

        resp = api_client.get(
            reverse(
                "data_source.related_resource_stats",
                kwargs={"id": full_local_data_source.id},
            )
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data == {
            "own_department_count": 9,
            "own_user_count": 11,
            "shared_to_tenant_count": 1,
            "shared_to_department_count": 9,
            "shared_to_user_count": 11,
        }


class TestDataSourceSyncRecordApi:
    def test_list(self, api_client, data_source, data_source_sync_tasks):
        resp = api_client.get(reverse("data_source.sync_record.list", kwargs={"id": data_source.id}))
        tasks = resp.data["results"]
        # 不属于指定数据源的同步记录是看不到的
        assert len(tasks) == 2  # noqa: PLR2004
        assert set(tasks[0].keys()) == {
            "id",
            "status",
            "has_warning",
            "trigger",
            "operator",
            "start_at",
            "duration",
            "extras",
        }

    def test_list_with_filter(self, api_client, data_source, data_source_sync_tasks):
        url = reverse("data_source.sync_record.list", kwargs={"id": data_source.id})
        resp = api_client.get(url, data={"statuses": "success"})
        assert len(resp.data["results"]) == 1  # noqa: PLR2004

        resp = api_client.get(url, data={"statuses": "success,failed"})
        assert len(resp.data["results"]) == 2  # noqa: PLR2004

    def test_retrieve(self, api_client, data_source_sync_tasks):
        success_task = data_source_sync_tasks[0]
        resp = api_client.get(reverse("data_source.sync_record.retrieve", kwargs={"id": success_task.id}))
        assert set(resp.data.keys()) == {"id", "status", "has_warning", "start_at", "duration", "logs"}

    def test_retrieve_other_tenant_data_source_sync_record(self, api_client, data_source_sync_tasks):
        other_tenant_task = data_source_sync_tasks[2]
        resp = api_client.get(reverse("data_source.sync_record.retrieve", kwargs={"id": other_tenant_task.id}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND

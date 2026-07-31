# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from typing import Any, Dict, List

import pytest
from bkuser.apps.idp.constants import IdpStatus
from bkuser.apps.idp.data_models import DataSourceMatchRule
from bkuser.apps.idp.models import Idp, IdpDataSourceRelation, IdpPlugin
from bkuser.biz.idp_data_source import IdpDataSourceRelationHandler
from bkuser.common.constants import SENSITIVE_MASK
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.wecom.plugin import WecomIdpPluginConfig
from django.urls import reverse
from rest_framework import status

from tests.test_utils.helpers import generate_random_string

pytestmark = pytest.mark.django_db


@pytest.fixture
def wecom_plugin_cfg() -> Dict[str, Any]:
    """企业微信插件配置"""
    return {
        "corp_id": generate_random_string(),
        "agent_id": generate_random_string(),
        "secret": generate_random_string(),
    }


@pytest.fixture
def data_source_match_rules(bare_general_data_source) -> List[Dict[str, Any]]:
    """匹配数据源规则"""
    return [
        {
            "data_source_id": bare_general_data_source.id,
            # Note: 当前只允许匹配内建字段
            "field_compare_rules": [{"source_field": "user_id", "target_field": "username"}],
        }
    ]


def get_idp_match_rules(idp: Idp) -> List[Dict[str, Any]]:
    relation = IdpDataSourceRelation.objects.filter(idp=idp).first()
    if relation is None:
        return []

    return [
        {
            "data_source_id": relation.data_source_id,
            "field_compare_rules": relation.field_compare_rules,
        }
    ]


@pytest.fixture
def wecom_idp(bk_user, random_tenant, wecom_plugin_cfg, data_source_match_rules) -> Idp:
    idp = Idp.objects.create(
        name=generate_random_string(),
        owner_tenant_id=random_tenant.id,
        plugin=IdpPlugin.objects.get(id=BuiltinIdpPluginEnum.WECOM),
        plugin_config=WecomIdpPluginConfig(**wecom_plugin_cfg),
        creator=bk_user.username,
        updater=bk_user.username,
    )
    IdpDataSourceRelationHandler.set_real_relations_from_match_rules(
        idp, [DataSourceMatchRule(**rule) for rule in data_source_match_rules]
    )
    return idp


class TestIdpPluginListApi:
    def test_list(self, api_client):
        resp = api_client.get(reverse("idp_plugin.list"))
        # 至少有一个默认的本地账密认证源插件
        assert len(resp.data) >= 1
        assert BuiltinIdpPluginEnum.LOCAL in [i["id"] for i in resp.data]


class TestIdpCreateApi:
    def test_create_with_wecom_idp(self, api_client, wecom_plugin_cfg, data_source_match_rules):
        resp = api_client.post(
            reverse("idp.list_create"),
            data={
                "name": generate_random_string(),
                "status": IdpStatus.ENABLED,
                "plugin_id": BuiltinIdpPluginEnum.WECOM,
                "plugin_config": wecom_plugin_cfg,
                "data_source_match_rules": data_source_match_rules,
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_with_not_exist_plugin(self, api_client):
        resp = api_client.post(
            reverse("idp.list_create"),
            data={
                "name": generate_random_string(),
                "status": IdpStatus.ENABLED,
                "plugin_id": generate_random_string(),
                "plugin_config": {},
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "认证源插件不存在" in resp.data["message"]

    def test_create_with_not_allowed_local_idp(self, api_client, data_source_match_rules):
        resp = api_client.post(
            reverse("idp.list_create"),
            data={
                "name": generate_random_string(),
                "status": IdpStatus.ENABLED,
                "plugin_id": BuiltinIdpPluginEnum.LOCAL,
                "plugin_config": {},
                "data_source_match_rules": data_source_match_rules,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不允许创建本地账密认证源" in resp.data["message"]

    def test_create_with_invalid_plugin_config(self, api_client, data_source_match_rules):
        request_data = {
            "name": generate_random_string(),
            "status": IdpStatus.ENABLED,
            "plugin_id": BuiltinIdpPluginEnum.WECOM,
            "data_source_match_rules": data_source_match_rules,
            "plugin_config": {},
        }

        resp = api_client.post(reverse("idp.list_create"), data=request_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "认证源插件配置不合法" in resp.data["message"]

        request_data["plugin_config"] = {"corp_id": generate_random_string()}
        resp = api_client.post(reverse("idp.list_create"), data=request_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "认证源插件配置不合法" in resp.data["message"]

    def test_create_with_invalid_data_source_match_rules(self, api_client, wecom_plugin_cfg, bare_general_data_source):
        request_data = {
            "name": generate_random_string(),
            "plugin_id": BuiltinIdpPluginEnum.WECOM,
            "plugin_config": wecom_plugin_cfg,
            "data_source_match_rules": [
                {
                    "data_source_id": 100000000000,
                    "field_compare_rules": [{"source_field": "user_id", "target_field": "username"}],
                }
            ],
        }

        resp = api_client.post(reverse("idp.list_create"), data=request_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "当前租户下不存在 ID 为" in resp.data["message"]

        request_data["data_source_match_rules"] = [
            {
                "data_source_id": bare_general_data_source.id,
                "field_compare_rules": [{"source_field": "user_id", "target_field": generate_random_string()}],
            }
        ]
        resp = api_client.post(reverse("idp.list_create"), data=request_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不属于用户自定义字段或内置字段" in resp.data["message"]

    def test_create_rejects_empty_data_source_match_rules(self, api_client, wecom_plugin_cfg):
        # 产品约定：生效范围不允许为空（遗留孤儿 IdP 仅通过详情 scope_pending_confirm 暴露）
        for idp_status in (IdpStatus.ENABLED, IdpStatus.DISABLED):
            request_data = {
                "name": generate_random_string(),
                "status": idp_status,
                "plugin_id": BuiltinIdpPluginEnum.WECOM,
                "plugin_config": wecom_plugin_cfg,
                "data_source_match_rules": [],
            }
            resp = api_client.post(reverse("idp.list_create"), data=request_data)
            assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestIdpListApi:
    def test_list(self, api_client, wecom_idp):
        resp = api_client.get(reverse("idp.list_create"))
        assert len(resp.data) != 0

        resp = api_client.get(reverse("idp.list_create"), data={"keyword": wecom_idp.name})
        assert len(resp.data) == 1

        idp = resp.data[0]
        assert idp["id"] == wecom_idp.id


class TestIdpUpdateApi:
    def test_update_with_wecom_idp(self, api_client, wecom_idp):
        new_name = generate_random_string()
        new_plugin_config = {
            "corp_id": generate_random_string(),
            "agent_id": generate_random_string(),
            "secret": generate_random_string(),
        }
        resp = api_client.put(
            reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}),
            data={
                "name": new_name,
                "status": IdpStatus.ENABLED,
                "plugin_config": new_plugin_config,
                "data_source_match_rules": get_idp_match_rules(wecom_idp),
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        idp = Idp.objects.get(id=wecom_idp.id)
        assert idp.name == new_name
        assert idp.plugin_config["corp_id"] == new_plugin_config["corp_id"]
        assert idp.plugin_config["agent_id"] == new_plugin_config["agent_id"]
        assert idp.plugin_config["secret"] == SENSITIVE_MASK
        assert idp.get_plugin_cfg().model_dump() == new_plugin_config

    def test_update_persists_full_scope(
        self, api_client, wecom_idp, wecom_plugin_cfg, bare_general_data_source, bare_local_data_source
    ):
        # 生效范围改为 {general, local} 两个源，全部持久化并可完整回显
        rules = [
            {
                "data_source_id": bare_general_data_source.id,
                "field_compare_rules": [{"source_field": "user_id", "target_field": "username"}],
            },
            {
                "data_source_id": bare_local_data_source.id,
                "field_compare_rules": [{"source_field": "user_id", "target_field": "username"}],
            },
        ]
        resp = api_client.put(
            reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}),
            data={
                "name": wecom_idp.name,
                "status": IdpStatus.ENABLED,
                "plugin_config": wecom_plugin_cfg,
                "data_source_match_rules": rules,
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        relation_ds_ids = set(
            IdpDataSourceRelation.objects.filter(idp=wecom_idp).values_list("data_source_id", flat=True)
        )
        assert relation_ds_ids == {bare_general_data_source.id, bare_local_data_source.id}

        detail = api_client.get(reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}))
        assert {r["data_source_id"] for r in detail.data["data_source_match_rules"]} == relation_ds_ids

    def test_update_rejects_empty_data_source_match_rules(self, api_client, wecom_idp, wecom_plugin_cfg):
        # 产品约定：更新时生效范围也不允许为空（含停用态）
        before_ds_ids = set(
            IdpDataSourceRelation.objects.filter(idp=wecom_idp).values_list("data_source_id", flat=True)
        )
        for idp_status in (IdpStatus.ENABLED, IdpStatus.DISABLED):
            resp = api_client.put(
                reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}),
                data={
                    "name": wecom_idp.name,
                    "status": idp_status,
                    "plugin_config": wecom_plugin_cfg,
                    "data_source_match_rules": [],
                },
            )
            assert resp.status_code == status.HTTP_400_BAD_REQUEST

        # 关系未被清空
        after_ds_ids = set(
            IdpDataSourceRelation.objects.filter(idp=wecom_idp).values_list("data_source_id", flat=True)
        )
        assert after_ds_ids == before_ds_ids

    def test_update_with_invalid_plugin_config(self, api_client, wecom_idp):
        resp = api_client.put(
            reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}),
            data={
                "name": wecom_idp.name,
                "plugin_config": {},
                "data_source_match_rules": get_idp_match_rules(wecom_idp),
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "认证源插件配置不合法" in resp.data["message"]

        resp = api_client.put(
            reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}),
            data={
                "name": wecom_idp.name,
                "plugin_config": {"corp_id": generate_random_string()},
                "data_source_match_rules": get_idp_match_rules(wecom_idp),
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "认证源插件配置不合法" in resp.data["message"]

    def test_partial_update_with_name(self, api_client, wecom_idp):
        new_name = generate_random_string()
        relation_count = IdpDataSourceRelation.objects.filter(idp=wecom_idp).count()
        resp = api_client.patch(
            reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}),
            data={"name": new_name, "data_source_match_rules": []},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        idp = Idp.objects.get(id=wecom_idp.id)
        assert idp.name == new_name
        assert IdpDataSourceRelation.objects.filter(idp=idp).count() == relation_count

    # def test_partial_update_with_duplicate_name(self, bk_user, api_client, wecom_idp):
    #     new_name = generate_random_string()
    #     Idp.objects.create(
    #         name=new_name,
    #         owner_tenant_id=wecom_idp.owner_tenant_id,
    #         plugin=wecom_idp.plugin,
    #         plugin_config=WecomIdpPluginConfig(**wecom_idp.plugin_config),
    #         creator=bk_user.username,
    #         updater=bk_user.username,
    #     )
    #     resp = api_client.patch(reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}), data={"name": new_name})
    #     assert resp.status_code == status.HTTP_400_BAD_REQUEST
    #     assert "同名认证源已存在" in resp.data["message"]


class TestIdpRetrieveApi:
    def test_retrieve(self, api_client, wecom_idp):
        resp = api_client.get(reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}))
        assert resp.data["id"] == wecom_idp.id
        assert resp.data["name"] == wecom_idp.name
        assert resp.data["status"] == wecom_idp.status
        assert resp.data["plugin"]["id"] == wecom_idp.plugin.id
        assert resp.data["plugin"]["name"] == wecom_idp.plugin.name
        assert resp.data["plugin_config"] == wecom_idp.plugin_config
        assert resp.data["data_source_match_rules"] == get_idp_match_rules(wecom_idp)
        assert resp.data["callback_uri"] == wecom_idp.callback_uri
        # 启用且有 REAL 关系 -> 非待确认态
        assert resp.data["scope_pending_confirm"] is False

    def test_retrieve_scope_pending_confirm_for_orphan(self, api_client, wecom_idp):
        # 启用中但无任何 REAL 关系（孤儿）-> 待管理员确认范围
        IdpDataSourceRelation.objects.filter(idp=wecom_idp).delete()
        resp = api_client.get(reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}))
        assert resp.data["status"] == IdpStatus.ENABLED
        assert resp.data["data_source_match_rules"] == []
        assert resp.data["scope_pending_confirm"] is True


class TestIdpStatusUpdateApi:
    def test_update(self, api_client, wecom_idp):
        url = reverse("idp.update_status", kwargs={"id": wecom_idp.id})
        # 默认启用，切换后不可用
        assert api_client.put(url).data["status"] == IdpStatus.DISABLED
        # 再次切换，变成可用
        assert api_client.put(url).data["status"] == IdpStatus.ENABLED


class TestLocalIdpCreateApi:
    def test_create_with_valid_email_sender(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin_cfg
    ):
        # 修改邮件发送模版的 sender 为合法邮箱
        local_ds_plugin_cfg["password_initial"]["notification"]["templates"][0]["sender"] = "test@example.com"
        local_ds_plugin_cfg["password_expire"]["notification"]["templates"][0]["sender"] = "test@example.com"

        resp = api_client.post(
            reverse("idp.local.create"),
            data={
                "name": generate_random_string(),
                "status": IdpStatus.ENABLED,
                "plugin_config": local_ds_plugin_cfg,
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_with_empty_email_sender(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin_cfg
    ):
        resp = api_client.post(
            reverse("idp.local.create"),
            data={
                "name": generate_random_string(),
                "status": IdpStatus.ENABLED,
                "plugin_config": local_ds_plugin_cfg,
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_with_invalid_email_sender(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin_cfg
    ):
        local_ds_plugin_cfg["password_initial"]["notification"]["templates"][0]["sender"] = "not-an-email"

        resp = api_client.post(
            reverse("idp.local.create"),
            data={
                "name": generate_random_string(),
                "status": IdpStatus.ENABLED,
                "plugin_config": local_ds_plugin_cfg,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "认证源插件配置不合法" in resp.data["message"]

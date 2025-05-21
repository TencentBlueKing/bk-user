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
from bkuser.apps.tenant.constants import UserFieldDataType
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestTenantListApi:
    def test_standard(self, api_client, default_tenant, random_tenant):
        resp = api_client.get(reverse("open_v3.tenant.list"))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["id"] for t in resp.data} == {default_tenant.id, random_tenant.id}
        assert set(resp.data[0].keys()) == {"id", "name", "status"}


class TestTenantCommonVariableListApi:
    def test_standard(self, api_client, tenant_common_variable):
        resp = api_client.get(reverse("open_v3.tenant_common_variable.list"))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["name"] for t in resp.data} == {"key_1", "key_2"}
        assert {t["value"] for t in resp.data} == {"value_1", "value_2"}


class TestTenantUserCustomEnumFieldListApi:
    def test_standard(self, api_client, tenant_user_custom_fields):
        resp = api_client.get(reverse("open_v3.tenant_user_custom_enum_field.list"))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["name"] for t in resp.data} == {"gender", "sport_hobby"}
        assert {t["display_name"] for t in resp.data} == {"性别", "运动爱好"}
        assert {t["data_type"] for t in resp.data} == {UserFieldDataType.ENUM, UserFieldDataType.MULTI_ENUM}
        assert [{"id": "male", "value": "男"}, {"id": "female", "value": "女"}, {"id": "other", "value": "其他"}] in [
            t["options"] for t in resp.data
        ]
        assert [
            {"id": "running", "value": "跑步"},
            {"id": "swimming", "value": "游泳"},
            {"id": "basketball", "value": "篮球"},
            {"id": "football", "value": "足球"},
            {"id": "golf", "value": "高尔夫"},
            {"id": "cycling", "value": "骑行"},
        ] in [t["options"] for t in resp.data]

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
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestTenantUserRetrieveApi:
    def test_retrieve_tenant_user(self, apigw_api_client, default_tenant_user_data, default_tenant):
        resp = apigw_api_client.get(reverse("apigw.tenant_user.retrieve", kwargs={"id": "zhangsan"}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["tenant_id"] == default_tenant.id

    def test_retrieve_tenant_user_not_found(self, apigw_api_client, default_tenant_user_data):
        resp = apigw_api_client.get(reverse("apigw.tenant_user.retrieve", kwargs={"id": "zhangsan_not_found"}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestTenantUserContactInfoListApi:
    def test_list_tenant_user(self, apigw_api_client, default_tenant_user_data, default_tenant):
        resp = apigw_api_client.get(
            reverse("apigw.tenant_user.contact_info.list"), data={"bk_usernames": "zhangsan,lisi"}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["tenant_id"] for t in resp.data} == {default_tenant.id, default_tenant.id}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}
        assert {t["phone"] for t in resp.data} == {"13512345671", "13512345672"}
        assert {t["email"] for t in resp.data} == {"zhangsan@m.com", "lisi@m.com"}
        assert {t["phone_country_code"] for t in resp.data} == {"86"}

    def test_with_invalid_bk_usernames(self, apigw_api_client, default_tenant_user_data, default_tenant):
        resp = apigw_api_client.get(
            reverse("apigw.tenant_user.contact_info.list"), data={"bk_usernames": "zhangsan,not_exist"}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == "zhangsan"
        assert resp.data[0]["tenant_id"] == default_tenant.id
        assert resp.data[0]["display_name"] == "zhangsan(张三)"
        assert resp.data[0]["phone"] == "13512345671"
        assert resp.data[0]["email"] == "zhangsan@m.com"
        assert resp.data[0]["phone_country_code"] == "86"

    def test_with_no_bk_usernames(self, apigw_api_client):
        resp = apigw_api_client.get(reverse("apigw.tenant_user.contact_info.list"), data={"bk_usernames": ""})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_with_invalid_length(self, apigw_api_client):
        resp = apigw_api_client.get(
            reverse("apigw.tenant_user.contact_info.list"),
            data={"bk_usernames": ",".join(map(str, range(1, 102)))},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

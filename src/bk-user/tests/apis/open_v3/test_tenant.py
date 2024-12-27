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
from bkuser.apps.tenant.models import TenantUser
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestTenantList:
    def test_standard(self, api_client, default_tenant, random_tenant):
        resp = api_client.get(reverse("open_v3.tenant.list"))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 2
        assert {t["id"] for t in resp.data["results"]} == {default_tenant.id, random_tenant.id}
        assert set(resp.data["results"][0].keys()) == {"id", "name", "status"}


class TestTenantUserDisplayNameList:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client):
        zhangsan_id = TenantUser.objects.get(data_source_user__code="zhangsan").id
        lisi_id = TenantUser.objects.get(data_source_user__code="lisi").id
        resp = api_client.get(
            reverse("open_v3.tenant_user.display_name.list"), data={"bk_usernames": ",".join([zhangsan_id, lisi_id])}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan_id, lisi_id}
        assert {t["display_name"] for t in resp.data} == {"张三", "李四"}

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_invalid_bk_usernames(self, api_client):
        zhangsan_id = TenantUser.objects.get(data_source_user__code="zhangsan").id
        resp = api_client.get(
            reverse("open_v3.tenant_user.display_name.list"), data={"bk_usernames": ",".join([zhangsan_id, "invalid"])}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == zhangsan_id
        assert resp.data[0]["display_name"] == "张三"

    def test_with_no_bk_usernames(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.display_name.list"), data={"bk_usernames": ""})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_with_invalid_length(self, api_client):
        resp = api_client.get(
            reverse("open_v3.tenant_user.display_name.list"), data={"bk_usernames": ",".join(map(str, range(1, 52)))}
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

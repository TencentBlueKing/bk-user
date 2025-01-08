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
from django.conf import settings
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserDisplayNameList:
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
            reverse("open_v3.tenant_user.display_name.list"),
            data={
                "bk_usernames": ",".join(
                    map(str, range(1, settings.BATCH_QUERY_USER_DISPLAY_NAME_BY_BK_USERNAME_LIMIT + 2))
                )
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserRetrieveApi:
    def test_standard(self, api_client, random_tenant):
        zhangsan = TenantUser.objects.get(data_source_user__code="zhangsan")
        resp = api_client.get(reverse("open_v3.tenant_user.retrieve", kwargs={"id": zhangsan.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["bk_username"] == zhangsan.id
        assert resp.data["display_name"] == "张三"
        assert resp.data["language"] == "zh-cn"
        assert resp.data["time_zone"] == "Asia/Shanghai"
        assert resp.data["tenant_id"] == random_tenant.id

    def test_tenant_not_found(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.retrieve", kwargs={"id": "not_exist"}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserLeaderListApi:
    def test_with_single_leader(self, api_client):
        lisi = TenantUser.objects.get(data_source_user__code="lisi")
        zhangsan = TenantUser.objects.get(data_source_user__code="zhangsan")
        resp = api_client.get(reverse("open_v3.tenant_user.leaders.list", kwargs={"id": lisi.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data[0]["bk_username"] == zhangsan.id
        assert resp.data[0]["display_name"] == "张三"

    def test_with_multiple_leader(self, api_client):
        lisi = TenantUser.objects.get(data_source_user__code="lisi")
        wangwu = TenantUser.objects.get(data_source_user__code="wangwu")
        maiba = TenantUser.objects.get(data_source_user__code="maiba")
        resp = api_client.get(reverse("open_v3.tenant_user.leaders.list", kwargs={"id": maiba.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert {t["bk_username"] for t in resp.data} == {wangwu.id, lisi.id}
        assert {t["display_name"] for t in resp.data} == {"王五", "李四"}

    def test_with_no_leader(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__code="zhangsan")
        resp = api_client.get(reverse("open_v3.tenant_user.leaders.list", kwargs={"id": zhangsan.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

    def test_with_invalid_user(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.leaders.list", kwargs={"id": "a1e5b2f6c3g7d4h8"}))
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

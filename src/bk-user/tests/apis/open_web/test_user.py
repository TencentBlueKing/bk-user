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
from bkuser.biz.tenant import TenantUserHandler
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserDisplayInfoRetrieveApi:
    def test_standard(self, api_client):
        zhangsan_id = TenantUser.objects.get(data_source_user__username="zhangsan").id
        resp = api_client.get(reverse("open_web.tenant_user.display_info.retrieve", kwargs={"id": zhangsan_id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["display_name"] == "张三"

    def test_with_invalid_bk_username(self, api_client):
        resp = api_client.get(reverse("open_web.tenant_user.display_info.retrieve", kwargs={"id": "invalid"}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserDisplayInfoListApi:
    def test_standard(self, api_client):
        zhangsan_id = TenantUser.objects.get(data_source_user__username="zhangsan").id
        lisi_id = TenantUser.objects.get(data_source_user__username="lisi").id
        resp = api_client.get(
            reverse("open_web.tenant_user.display_info.list"),
            data={"bk_usernames": ",".join([zhangsan_id, lisi_id])},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan_id, lisi_id}
        assert {t["display_name"] for t in resp.data} == {"张三", "李四"}

    def test_with_invalid_bk_usernames(self, api_client):
        zhangsan_id = TenantUser.objects.get(data_source_user__username="zhangsan").id
        resp = api_client.get(
            reverse("open_web.tenant_user.display_info.list"),
            data={"bk_usernames": ",".join([zhangsan_id, "invalid"])},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == zhangsan_id
        assert resp.data[0]["display_name"] == "张三"

    def test_with_no_bk_usernames(self, api_client):
        resp = api_client.get(reverse("open_web.tenant_user.display_info.list"), data={"bk_usernames": ""})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_with_invalid_length(self, api_client):
        resp = api_client.get(
            reverse("open_web.tenant_user.display_info.list"),
            data={
                "bk_usernames": ",".join(
                    map(str, range(1, settings.BATCH_QUERY_USER_DISPLAY_INFO_BY_BK_USERNAME_LIMIT + 2))
                )
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("_init_tenant_users_depts")
@pytest.mark.usefixtures("_init_collaboration_users_depts")
@pytest.mark.usefixtures("_init_virtual_tenant_users")
class TestTenantUserSearchApi:
    def test_with_full_name(self, api_client, random_tenant):
        with override_settings(ENABLE_SEARCH_COLLABORATION_TENANT=False, ENABLE_SEARCH_VIRTUAL_USER=False):
            wangwu = TenantUser.objects.get(
                data_source_user__username="wangwu",
                data_source__type="real",
                data_source__owner_tenant_id=random_tenant.id,
            )

            resp = api_client.get(reverse("open_web.tenant_user.search"), data={"keyword": "王"})

            assert resp.status_code == status.HTTP_200_OK
            assert resp.data[0]["bk_username"] == wangwu.id
            assert resp.data[0]["login_name"] == "wangwu"
            assert resp.data[0]["display_name"] == TenantUserHandler.generate_tenant_user_display_name(wangwu)
            assert resp.data[0]["type"] == "real"
            assert resp.data[0]["tenant_id"] == ""
            assert resp.data[0]["tenant_name"] == ""

    def test_with_login_name(self, api_client, random_tenant):
        with override_settings(ENABLE_SEARCH_COLLABORATION_TENANT=False, ENABLE_SEARCH_VIRTUAL_USER=False):
            lisi = TenantUser.objects.get(
                data_source_user__username="lisi",
                data_source__type="real",
                data_source__owner_tenant_id=random_tenant.id,
            )
            resp = api_client.get(reverse("open_web.tenant_user.search"), data={"keyword": "lis"})

            assert resp.status_code == status.HTTP_200_OK
            assert resp.data[0]["bk_username"] == lisi.id
            assert resp.data[0]["login_name"] == "lisi"
            assert resp.data[0]["display_name"] == TenantUserHandler.generate_tenant_user_display_name(lisi)
            assert resp.data[0]["type"] == "real"
            assert resp.data[0]["tenant_id"] == ""
            assert resp.data[0]["tenant_name"] == ""

    def test_with_all_users(self, api_client, random_tenant, collaboration_tenant):
        with override_settings(ENABLE_COLLABORATION_TENANT=True, ENABLE_VIRTUAL_USER=True):
            real_zhangsan = TenantUser.objects.get(
                data_source_user__username="zhangsan",
                data_source__type="real",
                data_source__owner_tenant_id=random_tenant.id,
            )
            virtual_zhangsan = TenantUser.objects.get(
                data_source_user__username="zhangsan", data_source__type="virtual"
            )
            collab_zhangsan = TenantUser.objects.get(
                data_source_user__username="zhangsan", data_source__owner_tenant_id=collaboration_tenant.id
            )
            resp = api_client.get(reverse("open_web.tenant_user.search"), data={"keyword": "张"})

            assert resp.status_code == status.HTTP_200_OK
            assert {t["bk_username"] for t in resp.data} == {real_zhangsan.id, virtual_zhangsan.id, collab_zhangsan.id}
            assert {t["login_name"] for t in resp.data} == {"zhangsan"}
            assert {t["display_name"] for t in resp.data} == {
                TenantUserHandler.generate_tenant_user_display_name(real_zhangsan),
                TenantUserHandler.generate_tenant_user_display_name(virtual_zhangsan),
                TenantUserHandler.generate_tenant_user_display_name(collab_zhangsan),
            }
            assert {t["type"] for t in resp.data} == {"real", "virtual"}
            assert {t["tenant_id"] for t in resp.data} == {"", collaboration_tenant.id}
            assert {t["tenant_name"] for t in resp.data} == {"", collaboration_tenant.name}

    def test_with_not_match(self, api_client):
        resp = api_client.get(reverse("open_web.tenant_user.search"), data={"keyword": "陈"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

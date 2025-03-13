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
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.tenant import TenantUserHandler
from django.conf import settings
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
        baishier = TenantUser.objects.get(
            data_source_user__username="baishier",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )

        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "白十", "data_source_type": "real", "owner_tenant_id": random_tenant.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == baishier.id
        assert resp.data[0]["login_name"] == "baishier"
        assert resp.data[0]["full_name"] == "白十二"
        assert resp.data[0]["display_name"] == TenantUserHandler.generate_tenant_user_display_name(baishier)
        assert resp.data[0]["data_source_type"] == DataSourceTypeEnum.REAL
        assert resp.data[0]["owner_tenant_id"] == random_tenant.id

    def test_with_login_name(self, api_client, random_tenant):
        lisi = TenantUser.objects.get(
            data_source_user__username="lisi",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "lis", "data_source_type": "real", "owner_tenant_id": random_tenant.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == lisi.id
        assert resp.data[0]["login_name"] == "lisi"
        assert resp.data[0]["full_name"] == "李四"
        assert resp.data[0]["display_name"] == TenantUserHandler.generate_tenant_user_display_name(lisi)
        assert resp.data[0]["data_source_type"] == DataSourceTypeEnum.REAL
        assert resp.data[0]["owner_tenant_id"] == random_tenant.id

    def test_with_collaborative_tenant(self, api_client, collaboration_tenant):
        collab_wangwu = TenantUser.objects.get(
            data_source_user__username="wangwu", data_source__owner_tenant_id=collaboration_tenant.id
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "wang", "data_source_type": "real", "owner_tenant_id": collaboration_tenant.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == collab_wangwu.id
        assert resp.data[0]["login_name"] == "wangwu"
        assert resp.data[0]["full_name"] == "王五"
        assert resp.data[0]["display_name"] == TenantUserHandler.generate_tenant_user_display_name(collab_wangwu)
        assert resp.data[0]["data_source_type"] == DataSourceTypeEnum.REAL
        assert resp.data[0]["owner_tenant_id"] == collaboration_tenant.id

    def test_with_virtual_user(self, api_client, random_tenant):
        virtual_zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan", data_source__type="virtual")
        resp = api_client.get(
            reverse("open_web.tenant_user.search"), data={"keyword": "zhan", "data_source_type": "virtual"}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == virtual_zhangsan.id
        assert resp.data[0]["login_name"] == "zhangsan"
        assert resp.data[0]["full_name"] == "张三"
        assert resp.data[0]["display_name"] == TenantUserHandler.generate_tenant_user_display_name(virtual_zhangsan)
        assert resp.data[0]["data_source_type"] == DataSourceTypeEnum.VIRTUAL
        assert resp.data[0]["owner_tenant_id"] == random_tenant.id

    def test_with_all_users(self, api_client, random_tenant, collaboration_tenant):
        real_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        virtual_zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan", data_source__type="virtual")
        collab_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan", data_source__owner_tenant_id=collaboration_tenant.id
        )
        resp = api_client.get(reverse("open_web.tenant_user.search"), data={"keyword": "zhang"})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 3
        assert {t["bk_username"] for t in resp.data} == {real_zhangsan.id, virtual_zhangsan.id, collab_zhangsan.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan"}
        assert {t["full_name"] for t in resp.data} == {"张三"}
        assert {t["display_name"] for t in resp.data} == {
            TenantUserHandler.generate_tenant_user_display_name(real_zhangsan),
            TenantUserHandler.generate_tenant_user_display_name(virtual_zhangsan),
            TenantUserHandler.generate_tenant_user_display_name(collab_zhangsan),
        }
        assert {t["data_source_type"] for t in resp.data} == {DataSourceTypeEnum.REAL, DataSourceTypeEnum.VIRTUAL}
        assert {t["owner_tenant_id"] for t in resp.data} == {random_tenant.id, collaboration_tenant.id}

    def test_with_not_match(self, api_client):
        resp = api_client.get(reverse("open_web.tenant_user.search"), data={"keyword": "chen"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0


@pytest.mark.usefixtures("_init_tenant_users_depts")
@pytest.mark.usefixtures("_init_collaboration_users_depts")
@pytest.mark.usefixtures("_init_virtual_tenant_users")
class TestTenantUserLookupApi:
    def test_all_users(self, api_client, random_tenant, collaboration_tenant):
        real_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        virtual_zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan", data_source__type="virtual")
        collab_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan", data_source__owner_tenant_id=collaboration_tenant.id
        )
        real_lisi = TenantUser.objects.get(
            data_source_user__username="lisi",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        virtual_lisi = TenantUser.objects.get(data_source_user__username="lisi", data_source__type="virtual")
        collab_lisi = TenantUser.objects.get(
            data_source_user__username="lisi", data_source__owner_tenant_id=collaboration_tenant.id
        )

        resp = api_client.get(reverse("open_web.tenant_user.lookup"), data={"lookups": "zhangsan,lisi"})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 6
        assert {t["bk_username"] for t in resp.data} == {
            real_zhangsan.id,
            virtual_zhangsan.id,
            collab_zhangsan.id,
            real_lisi.id,
            virtual_lisi.id,
            collab_lisi.id,
        }
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {
            TenantUserHandler.generate_tenant_user_display_name(real_zhangsan),
            TenantUserHandler.generate_tenant_user_display_name(virtual_zhangsan),
            TenantUserHandler.generate_tenant_user_display_name(collab_zhangsan),
            TenantUserHandler.generate_tenant_user_display_name(real_lisi),
            TenantUserHandler.generate_tenant_user_display_name(virtual_lisi),
            TenantUserHandler.generate_tenant_user_display_name(collab_lisi),
        }
        assert {t["data_source_type"] for t in resp.data} == {DataSourceTypeEnum.REAL, DataSourceTypeEnum.VIRTUAL}
        assert {t["owner_tenant_id"] for t in resp.data} == {random_tenant.id, collaboration_tenant.id}

    def test_with_current_tenant(self, api_client, random_tenant):
        lisi = TenantUser.objects.get(
            data_source_user__username="lisi", data_source__type="real", data_source__owner_tenant_id=random_tenant.id
        )
        zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={"lookups": "zhangsan,lisi", "owner_tenant_id": random_tenant.id, "data_source_type": "real"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {
            TenantUserHandler.generate_tenant_user_display_name(zhangsan),
            TenantUserHandler.generate_tenant_user_display_name(lisi),
        }
        assert {t["data_source_type"] for t in resp.data} == {DataSourceTypeEnum.REAL}
        assert {t["owner_tenant_id"] for t in resp.data} == {random_tenant.id}

    def test_with_collaborative_tenant(self, api_client, collaboration_tenant):
        lisi = TenantUser.objects.get(
            data_source_user__username="lisi",
            data_source__type="real",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )
        zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="real",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": "zhangsan,lisi",
                "owner_tenant_id": collaboration_tenant.id,
                "data_source_type": "real",
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {
            TenantUserHandler.generate_tenant_user_display_name(zhangsan),
            TenantUserHandler.generate_tenant_user_display_name(lisi),
        }
        assert {t["data_source_type"] for t in resp.data} == {DataSourceTypeEnum.REAL}
        assert {t["owner_tenant_id"] for t in resp.data} == {collaboration_tenant.id}

    def test_with_virtual_user(self, api_client, random_tenant):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan", data_source__type="virtual")
        lisi = TenantUser.objects.get(data_source_user__username="lisi", data_source__type="virtual")
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={"lookups": "zhangsan,lisi", "owner_tenant_id": random_tenant.id, "data_source_type": "virtual"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {
            TenantUserHandler.generate_tenant_user_display_name(zhangsan),
            TenantUserHandler.generate_tenant_user_display_name(lisi),
        }
        assert {t["data_source_type"] for t in resp.data} == {DataSourceTypeEnum.VIRTUAL}
        assert {t["owner_tenant_id"] for t in resp.data} == {random_tenant.id}

    def test_with_filter_by_bk_username(self, api_client, random_tenant):
        lisi = TenantUser.objects.get(
            data_source_user__username="lisi", data_source__type="real", data_source__owner_tenant_id=random_tenant.id
        )
        zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": ",".join([zhangsan.id, lisi.id]),
                "lookup_fields": "bk_username,login_name",
                "owner_tenant_id": random_tenant.id,
                "data_source_type": "real",
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {
            TenantUserHandler.generate_tenant_user_display_name(zhangsan),
            TenantUserHandler.generate_tenant_user_display_name(lisi),
        }
        assert {t["data_source_type"] for t in resp.data} == {DataSourceTypeEnum.REAL}
        assert {t["owner_tenant_id"] for t in resp.data} == {random_tenant.id}

    def test_with_filter_by_full_name(self, api_client, random_tenant):
        lisi = TenantUser.objects.get(
            data_source_user__username="lisi", data_source__type="real", data_source__owner_tenant_id=random_tenant.id
        )
        zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": "张三,李四",
                "lookup_fields": "bk_username,login_name,full_name",
                "owner_tenant_id": random_tenant.id,
                "data_source_type": "real",
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {
            TenantUserHandler.generate_tenant_user_display_name(zhangsan),
            TenantUserHandler.generate_tenant_user_display_name(lisi),
        }
        assert {t["data_source_type"] for t in resp.data} == {DataSourceTypeEnum.REAL}
        assert {t["owner_tenant_id"] for t in resp.data} == {random_tenant.id}

    def test_with_not_match(self, api_client):
        resp = api_client.get(reverse("open_web.tenant_user.lookup"), data={"lookups": "zhangsan123,lisi123"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

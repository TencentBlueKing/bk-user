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
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from django.conf import settings
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserDisplayInfoListApi:
    def test_standard(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        resp = api_client.get(
            reverse("open_v3.tenant_user.display_info.list"), data={"bk_usernames": ",".join([zhangsan.id, lisi.id])}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}

    def test_with_invalid_bk_usernames(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        resp = api_client.get(
            reverse("open_v3.tenant_user.display_info.list"), data={"bk_usernames": ",".join([zhangsan.id, "invalid"])}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == zhangsan.id
        assert resp.data[0]["display_name"] == "zhangsan(张三)"

    def test_with_no_bk_usernames(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.display_info.list"), data={"bk_usernames": ""})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_with_invalid_length(self, api_client):
        resp = api_client.get(
            reverse("open_v3.tenant_user.display_info.list"),
            data={
                "bk_usernames": ",".join(
                    map(str, range(1, settings.BATCH_QUERY_USER_DISPLAY_INFO_BY_BK_USERNAME_LIMIT + 2))
                )
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserRetrieveApi:
    def test_standard(self, api_client, random_tenant):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        resp = api_client.get(reverse("open_v3.tenant_user.retrieve", kwargs={"id": zhangsan.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["bk_username"] == zhangsan.id
        assert resp.data["display_name"] == "zhangsan(张三)"
        assert resp.data["language"] == "zh-cn"
        assert resp.data["time_zone"] == "Asia/Shanghai"
        assert resp.data["tenant_id"] == random_tenant.id

    def test_tenant_not_found(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.retrieve", kwargs={"id": "not_exist"}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserDepartmentListApi:
    def test_with_not_ancestors(self, api_client):
        # with_ancestors = False
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        resp = api_client.get(reverse("open_v3.tenant_user.department.list", kwargs={"id": zhangsan.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data[0]["id"] == company.id
        assert resp.data[0]["name"] == "公司"
        assert "ancestors" not in resp.data[0]

    def test_with_no_ancestors(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        resp = api_client.get(
            reverse("open_v3.tenant_user.department.list", kwargs={"id": zhangsan.id}), data={"with_ancestors": True}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data[0]["id"] == company.id
        assert resp.data[0]["name"] == "公司"
        assert resp.data[0]["ancestors"] == []

    def test_with_ancestors(self, api_client):
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        dept_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")
        resp = api_client.get(
            reverse("open_v3.tenant_user.department.list", kwargs={"id": lisi.id}), data={"with_ancestors": True}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {d["id"] for d in resp.data} == {dept_a.id, dept_aa.id}
        assert {d["name"] for d in resp.data} == {"部门A", "中心AA"}
        assert resp.data[0]["ancestors"] == [{"id": company.id, "name": "公司"}]
        assert resp.data[1]["ancestors"] == [{"id": company.id, "name": "公司"}, {"id": dept_a.id, "name": "部门A"}]

    def test_with_invalid_user(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.department.list", kwargs={"id": "a1e5b2f6c3g7d4h8"}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_with_no_department(self, api_client):
        freedom = TenantUser.objects.get(data_source_user__username="freedom")
        resp = api_client.get(
            reverse("open_v3.tenant_user.department.list", kwargs={"id": freedom.id}), data={"with_ancestors": True}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserLeaderListApi:
    def test_with_single_leader(self, api_client):
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        resp = api_client.get(reverse("open_v3.tenant_user.leader.list", kwargs={"id": lisi.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data[0]["bk_username"] == zhangsan.id
        assert resp.data[0]["display_name"] == "zhangsan(张三)"

    def test_with_multiple_leader(self, api_client):
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        wangwu = TenantUser.objects.get(data_source_user__username="wangwu")
        maiba = TenantUser.objects.get(data_source_user__username="maiba")
        resp = api_client.get(reverse("open_v3.tenant_user.leader.list", kwargs={"id": maiba.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert {t["bk_username"] for t in resp.data} == {wangwu.id, lisi.id}
        assert {t["display_name"] for t in resp.data} == {"lisi(李四)", "wangwu(王五)"}

    def test_with_no_leader(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        resp = api_client.get(reverse("open_v3.tenant_user.leader.list", kwargs={"id": zhangsan.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

    def test_with_invalid_user(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.leader.list", kwargs={"id": "a1e5b2f6c3g7d4h8"}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserListApi:
    def test_standard(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.list"), data={"page": 1, "page_size": 11})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 11
        assert len(resp.data["results"]) == 11
        assert all("bk_username" in t for t in resp.data["results"])
        assert {t["full_name"] for t in resp.data["results"]} == {
            "张三",
            "李四",
            "王五",
            "赵六",
            "柳七",
            "麦八",
            "杨九",
            "鲁十",
            "林十一",
            "白十二",
            "自由人",
        }
        assert {t["display_name"] for t in resp.data["results"]} == {
            "zhangsan(张三)",
            "lisi(李四)",
            "wangwu(王五)",
            "zhaoliu(赵六)",
            "liuqi(柳七)",
            "maiba(麦八)",
            "yangjiu(杨九)",
            "lushi(鲁十)",
            "linshiyi(林十一)",
            "baishier(白十二)",
            "freedom(自由人)",
        }


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserSensitiveInfoListApi:
    def test_list_tenant_user(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        resp = api_client.get(
            reverse("open_v3.tenant_user.sensitive_info.list"), data={"bk_usernames": ",".join([zhangsan.id, lisi.id])}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["phone"] for t in resp.data} == {"13512345671", "13512345672"}
        assert {t["email"] for t in resp.data} == {"zhangsan@m.com", "lisi@m.com"}
        assert {t["phone_country_code"] for t in resp.data} == {"86"}
        assert all("wx_userid" in t for t in resp.data)

    def test_with_invalid_bk_usernames(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        resp = api_client.get(
            reverse("open_v3.tenant_user.sensitive_info.list"),
            data={"bk_usernames": ",".join([zhangsan.id, "invalid"])},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == zhangsan.id
        assert resp.data[0]["phone"] == "13512345671"
        assert resp.data[0]["email"] == "zhangsan@m.com"
        assert resp.data[0]["phone_country_code"] == "86"
        assert all("wx_userid" in t for t in resp.data)

    def test_with_no_bk_usernames(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_user.sensitive_info.list"), data={"bk_usernames": ""})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_with_invalid_length(self, api_client):
        resp = api_client.get(
            reverse("open_v3.tenant_user.sensitive_info.list"),
            data={"bk_usernames": ",".join(map(str, range(1, 102)))},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

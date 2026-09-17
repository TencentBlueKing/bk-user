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
from unittest import mock

import pytest
from bkuser.apis.open_web.views.users import TenantUserSearchApi
from bkuser.apps.tenant.constants import TenantUserStatus
from bkuser.apps.tenant.models import TenantDepartment, TenantUser, TenantUserDisplayNameExpressionConfig
from django.conf import settings
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserDisplayInfoRetrieveApi:
    def test_standard(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        resp = api_client.get(reverse("open_web.tenant_user.display_info.retrieve", kwargs={"id": zhangsan.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["display_name"] == "zhangsan(张三)"
        assert resp.data["login_name"] == "zhangsan"
        assert resp.data["full_name"] == "张三"

    def test_with_contact_field(self, api_client, display_name_expression_config_with_contact_field):
        with mock.patch(
            "bkuser.apps.tenant.models.TenantUserDisplayNameExpressionConfig.objects.get",
            return_value=display_name_expression_config_with_contact_field,
        ):
            zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
            resp = api_client.get(reverse("open_web.tenant_user.display_info.retrieve", kwargs={"id": zhangsan.id}))

            assert resp.status_code == status.HTTP_200_OK
            assert resp.data["display_name"] == "86-13512345671--zhangsan@m.com"

    @pytest.mark.usefixtures("_create_custom_fields")
    def test_with_custom_field(self, api_client, display_name_expression_config_with_custom_field):
        with mock.patch(
            "bkuser.apps.tenant.models.TenantUserDisplayNameExpressionConfig.objects.get",
            return_value=display_name_expression_config_with_custom_field,
        ):
            zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
            resp = api_client.get(reverse("open_web.tenant_user.display_info.retrieve", kwargs={"id": zhangsan.id}))

            assert resp.status_code == status.HTTP_200_OK
            assert resp.data["display_name"] == "13512345671-zhangsan--张三"

    @pytest.mark.usefixtures("_init_virtual_tenant_users")
    def test_with_virtual_user(self, api_client):
        virtual_zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan", data_source__type="virtual")
        resp = api_client.get(
            reverse("open_web.tenant_user.display_info.retrieve", kwargs={"id": virtual_zhangsan.id})
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["display_name"] == "zhangsan(张三)"
        assert resp.data["login_name"] == "zhangsan"
        assert resp.data["full_name"] == "张三"

    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_with_collaboration_user(self, api_client, collaboration_tenant):
        collab_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )
        resp = api_client.get(reverse("open_web.tenant_user.display_info.retrieve", kwargs={"id": collab_zhangsan.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["display_name"] == "zhangsan(张三)"
        assert resp.data["login_name"] == f"zhangsan@{collaboration_tenant.id}"
        assert resp.data["full_name"] == "张三"

    def test_with_invalid_bk_username(self, api_client):
        resp = api_client.get(reverse("open_web.tenant_user.display_info.retrieve", kwargs={"id": "invalid"}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserDisplayInfoListApi:
    def test_standard(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        resp = api_client.get(
            reverse("open_web.tenant_user.display_info.list"),
            data={"bk_usernames": ",".join([zhangsan.id, lisi.id])},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}

    @pytest.mark.usefixtures("_init_virtual_tenant_users")
    def test_with_virtual_user(self, api_client):
        virtual_zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan", data_source__type="virtual")
        virtual_lisi = TenantUser.objects.get(data_source_user__username="lisi", data_source__type="virtual")
        resp = api_client.get(
            reverse("open_web.tenant_user.display_info.list"),
            data={"bk_usernames": ",".join([virtual_zhangsan.id, virtual_lisi.id])},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {virtual_zhangsan.id, virtual_lisi.id}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}

    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_with_collaboration_user(self, api_client, collaboration_tenant):
        collab_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )
        collab_lisi = TenantUser.objects.get(
            data_source_user__username="lisi",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.display_info.list"),
            data={"bk_usernames": ",".join([collab_zhangsan.id, collab_lisi.id])},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {collab_zhangsan.id, collab_lisi.id}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}
        assert {t["login_name"] for t in resp.data} == {
            f"zhangsan@{collaboration_tenant.id}",
            f"lisi@{collaboration_tenant.id}",
        }

    def test_with_invalid_bk_usernames(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        resp = api_client.get(
            reverse("open_web.tenant_user.display_info.list"),
            data={"bk_usernames": ",".join([zhangsan.id, "invalid"])},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == zhangsan.id
        assert resp.data[0]["display_name"] == "zhangsan(张三)"
        assert resp.data[0]["login_name"] == "zhangsan"
        assert resp.data[0]["full_name"] == "张三"

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
            data={"keyword": "白十", "owner_tenant_id": random_tenant.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == baishier.id
        assert resp.data[0]["login_name"] == "baishier"
        assert resp.data[0]["full_name"] == "白十二"
        assert resp.data[0]["display_name"] == "baishier(白十二)"
        assert resp.data[0]["owner_tenant_id"] == random_tenant.id
        assert resp.data[0]["status"] == TenantUserStatus.ENABLED

    def test_with_login_name(self, api_client, random_tenant):
        lisi = TenantUser.objects.get(
            data_source_user__username="lisi",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={
                "keyword": "lis",
                "owner_tenant_id": random_tenant.id,
                "with_organization_paths": True,
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == lisi.id
        assert resp.data[0]["login_name"] == "lisi"
        assert resp.data[0]["full_name"] == "李四"
        assert resp.data[0]["display_name"] == "lisi(李四)"
        assert resp.data[0]["owner_tenant_id"] == random_tenant.id
        assert set(resp.data[0]["organization_paths"]) == {"公司/部门A/中心AA", "公司/部门A"}

    def test_with_collaborative_tenant(self, api_client, collaboration_tenant):
        collab_wangwu = TenantUser.objects.get(
            data_source_user__username="wangwu", data_source__owner_tenant_id=collaboration_tenant.id
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={
                "keyword": "wang",
                "owner_tenant_id": collaboration_tenant.id,
                "with_organization_paths": True,
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == collab_wangwu.id
        assert resp.data[0]["login_name"] == f"wangwu@{collaboration_tenant.id}"
        assert resp.data[0]["full_name"] == "王五"
        assert resp.data[0]["display_name"] == "wangwu(王五)"
        assert resp.data[0]["owner_tenant_id"] == collaboration_tenant.id
        assert set(resp.data[0]["organization_paths"]) == {"公司/部门A", "公司/部门B"}

    def test_with_all_users(self, api_client, random_tenant, collaboration_tenant):
        real_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        collab_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan", data_source__owner_tenant_id=collaboration_tenant.id
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.search"), data={"keyword": "zhang", "with_organization_paths": True}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {real_zhangsan.id, collab_zhangsan.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", f"zhangsan@{collaboration_tenant.id}"}
        assert {t["full_name"] for t in resp.data} == {"张三"}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)"}
        assert {t["owner_tenant_id"] for t in resp.data} == {random_tenant.id, collaboration_tenant.id}
        assert {p for t in resp.data for p in t["organization_paths"]} == {
            "公司",
        }

    def test_with_contact_field(self, api_client, random_tenant, display_name_expression_config_with_contact_field):
        config = TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=random_tenant.id)
        config.expression = display_name_expression_config_with_contact_field.expression
        config.fields = display_name_expression_config_with_contact_field.fields
        config.save()

        real_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "13512345671", "owner_tenant_id": random_tenant.id, "with_organization_paths": False},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert {t["bk_username"] for t in resp.data} == {real_zhangsan.id}
        assert {t["display_name"] for t in resp.data} == {"86-13512345671--zhangsan@m.com"}

    def test_with_collaboration_tenant_by_other_expression(
        self, api_client, collaboration_tenant, display_name_expression_config_with_collaboration_tenant_user
    ):
        config = TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=collaboration_tenant.id)
        config.expression = display_name_expression_config_with_collaboration_tenant_user.expression
        config.fields = display_name_expression_config_with_collaboration_tenant_user.fields
        config.save()

        collab_zhangsan = TenantUser.objects.get(
            data_source__owner_tenant_id=collaboration_tenant.id, data_source_user__username="zhangsan"
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "zhangsan", "owner_tenant_id": collaboration_tenant.id, "with_organization_paths": False},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert {t["bk_username"] for t in resp.data} == {collab_zhangsan.id}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)"}

    def test_with_not_match(self, api_client):
        resp = api_client.get(reverse("open_web.tenant_user.search"), data={"keyword": "chen"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserSearchApiWithExclusion:
    """用户搜索 - 黑名单排除（必须发生在 search_limit 截断之前）"""

    def test_exclude_user_ids(self, api_client):
        lisi = TenantUser.objects.get(data_source_user__username="lisi")

        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "lisi", "excluded_user_ids": lisi.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

    def test_exclude_by_department_subtree(self, api_client):
        """
        排除「部门A」后，挂在其子树上的人都搜不到

        keyword=十 可命中 鲁十(lushi)、林十一(linshiyi)、白十二(baishier)，
        其中 lushi 同属「小组ABA」与「中心BA」（多组织任一命中即排除），linshiyi 属「小组ABA」
        """
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")

        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "十", "excluded_department_ids": str(dept_a.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert {d["login_name"] for d in resp.data} == {"baishier"}

    def test_no_department_user_not_excluded_by_department(self, api_client):
        """无部门用户不受 excluded_department_ids 影响"""
        company = TenantDepartment.objects.get(data_source_department__code="company")

        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "freedom", "excluded_department_ids": str(company.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [d["login_name"] for d in resp.data] == ["freedom"]

    def test_exclude_before_search_limit(self, api_client):
        """
        关键用例：卡住「先截断再由调用方过滤」的实现

        search_limit=1 时，keyword=十 命中 3 人，其中 2 人在「部门A」子树上；
        若排除发生在截断之后，结果可能为空。正确实现应返回唯一的合格用户 baishier
        """
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")

        with mock.patch.object(TenantUserSearchApi, "search_limit", 1):
            resp = api_client.get(
                reverse("open_web.tenant_user.search"),
                data={"keyword": "十", "excluded_department_ids": str(dept_a.id)},
            )

        assert resp.status_code == status.HTTP_200_OK
        assert [d["login_name"] for d in resp.data] == ["baishier"]

    def test_with_blank_exclusion_params(self, api_client):
        """传空值等价于不传（DRF 会将 QueryDict 中非必填字段的空串视作未提供）"""
        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "lisi", "excluded_department_ids": "", "excluded_user_ids": ""},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [d["login_name"] for d in resp.data] == ["lisi"]

    def test_without_exclusion_params(self, api_client):
        """不传排除参数时与现网行为一致"""
        resp = api_client.get(reverse("open_web.tenant_user.search"), data={"keyword": "lisi"})

        assert resp.status_code == status.HTTP_200_OK
        assert [d["login_name"] for d in resp.data] == ["lisi"]

    def test_with_too_many_excluded_user_ids(self, api_client):
        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "lisi", "excluded_user_ids": ",".join(map(str, range(1, 102)))},
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST


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
        collab_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan", data_source__owner_tenant_id=collaboration_tenant.id
        )
        real_lisi = TenantUser.objects.get(
            data_source_user__username="lisi",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        collab_lisi = TenantUser.objects.get(
            data_source_user__username="lisi", data_source__owner_tenant_id=collaboration_tenant.id
        )
        virtual_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="virtual",
            data_source__owner_tenant_id=random_tenant.id,
        )
        virtual_lisi = TenantUser.objects.get(
            data_source_user__username="lisi",
            data_source__type="virtual",
            data_source__owner_tenant_id=random_tenant.id,
        )

        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={"lookups": "zhangsan,lisi", "lookup_fields": "login_name", "with_organization_paths": True},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 6
        assert {t["bk_username"] for t in resp.data} == {
            real_zhangsan.id,
            collab_zhangsan.id,
            real_lisi.id,
            collab_lisi.id,
            virtual_zhangsan.id,
            virtual_lisi.id,
        }
        assert {t["login_name"] for t in resp.data} == {
            "zhangsan",
            "lisi",
            f"zhangsan@{collaboration_tenant.id}",
            f"lisi@{collaboration_tenant.id}",
        }
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}
        assert {t["owner_tenant_id"] for t in resp.data} == {random_tenant.id, collaboration_tenant.id}
        assert {t["status"] for t in resp.data} == {TenantUserStatus.ENABLED}
        assert {p for t in resp.data for p in t["organization_paths"]} == {
            "公司",
            "公司/部门A/中心AA",
            "公司/部门A",
        }

    def test_with_current_tenant(self, api_client, random_tenant):
        lisi = TenantUser.objects.get(
            data_source_user__username="lisi", data_source__type="real", data_source__owner_tenant_id=random_tenant.id
        )
        zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        virtual_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="virtual",
            data_source__owner_tenant_id=random_tenant.id,
        )
        virtual_lisi = TenantUser.objects.get(
            data_source_user__username="lisi",
            data_source__type="virtual",
            data_source__owner_tenant_id=random_tenant.id,
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": "zhangsan,lisi",
                "lookup_fields": "login_name",
                "owner_tenant_id": random_tenant.id,
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 4
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id, virtual_zhangsan.id, virtual_lisi.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}
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
                "lookup_fields": "login_name",
                "owner_tenant_id": collaboration_tenant.id,
                "with_organization_paths": True,
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["login_name"] for t in resp.data} == {
            f"zhangsan@{collaboration_tenant.id}",
            f"lisi@{collaboration_tenant.id}",
        }
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}
        assert {t["owner_tenant_id"] for t in resp.data} == {collaboration_tenant.id}
        assert {p for t in resp.data for p in t["organization_paths"]} == {
            "公司",
            "公司/部门A/中心AA",
            "公司/部门A",
        }

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
                "with_organization_paths": True,
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}
        assert {t["owner_tenant_id"] for t in resp.data} == {random_tenant.id}
        assert {p for t in resp.data for p in t["organization_paths"]} == {
            "公司",
            "公司/部门A/中心AA",
            "公司/部门A",
        }

    def test_with_filter_by_full_name(self, api_client, random_tenant):
        lisi = TenantUser.objects.get(
            data_source_user__username="lisi", data_source__type="real", data_source__owner_tenant_id=random_tenant.id
        )
        zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )
        virtual_zhangsan = TenantUser.objects.get(
            data_source_user__username="zhangsan",
            data_source__type="virtual",
            data_source__owner_tenant_id=random_tenant.id,
        )
        virtual_lisi = TenantUser.objects.get(
            data_source_user__username="lisi",
            data_source__type="virtual",
            data_source__owner_tenant_id=random_tenant.id,
        )
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": "张三,李四",
                "lookup_fields": "bk_username,login_name,full_name",
                "owner_tenant_id": random_tenant.id,
                "with_organization_paths": True,
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 4
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id, virtual_zhangsan.id, virtual_lisi.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}
        assert {t["owner_tenant_id"] for t in resp.data} == {random_tenant.id}
        assert {p for t in resp.data for p in t["organization_paths"]} == {
            "公司",
            "公司/部门A/中心AA",
            "公司/部门A",
        }

    def test_with_not_match(self, api_client):
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={"lookups": "zhangsan123,lisi123", "lookup_fields": "login_name"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserLookupApiWithExclusion:
    """用户 lookup - 黑名单排除（回填/批量录入场景，调用方无法自行判断所属组织）"""

    def test_exclude_user_ids(self, api_client):
        lisi = TenantUser.objects.get(data_source_user__username="lisi")

        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": "zhangsan,lisi",
                "lookup_fields": "login_name",
                "excluded_user_ids": lisi.id,
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [t["login_name"] for t in resp.data] == ["zhangsan"]

    def test_exclude_by_department_subtree(self, api_client):
        """回填「中心AA」下的 zhaoliu 时排除其祖先「部门A」，zhaoliu 不应出现"""
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")

        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": "zhangsan,zhaoliu",
                "lookup_fields": "login_name",
                "excluded_department_ids": str(dept_a.id),
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [t["login_name"] for t in resp.data] == ["zhangsan"]

    def test_exclude_multi_org_user(self, api_client):
        """多组织用户 wangwu 属于「部门A」和「部门B」，排除任一即不应出现"""
        dept_b = TenantDepartment.objects.get(data_source_department__code="dept_b")

        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": "wangwu",
                "lookup_fields": "login_name",
                "excluded_department_ids": str(dept_b.id),
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

    def test_virtual_user_not_excluded_by_department(self, api_client, random_tenant):
        """无部门用户不受 excluded_department_ids 影响"""
        company = TenantDepartment.objects.get(data_source_department__code="company")

        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": "freedom",
                "lookup_fields": "login_name",
                "excluded_department_ids": str(company.id),
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [t["login_name"] for t in resp.data] == ["freedom"]

    def test_without_exclusion_params(self, api_client):
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={"lookups": "zhangsan,zhaoliu", "lookup_fields": "login_name"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "zhaoliu"}


@pytest.mark.usefixtures("_init_virtual_tenant_users")
class TestVirtualUserListApi:
    def test_with_standard(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        resp = api_client.get(reverse("open_web.tenant.virtual_user.list"))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 2
        assert {t["bk_username"] for t in resp.data["results"]} == {zhangsan.id, lisi.id}
        assert {t["login_name"] for t in resp.data["results"]} == {"zhangsan", "lisi"}
        assert {t["display_name"] for t in resp.data["results"]} == {
            "zhangsan(张三)",
            "lisi(李四)",
        }


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserLanguageUpdateApi:
    def test_update_language(self, api_client, auth_user):
        api_client.force_authenticate(user=auth_user)
        resp = api_client.put(
            reverse("open_web.tenant.current_user.language.update"),
            data={"language": "en"},
        )
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["language"] == "en"
        assert zhangsan.language == "en"

        resp = api_client.put(
            reverse("open_web.tenant.current_user.language.update"),
            data={"language": "zh-cn"},
        )
        zhangsan.refresh_from_db()
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["language"] == "zh-cn"
        assert zhangsan.language == "zh-cn"

    def test_update_invalid_language(self, api_client, auth_user):
        api_client.force_authenticate(user=auth_user)
        resp = api_client.put(
            reverse("open_web.tenant.current_user.language.update"),
            data={"language": "invalid"},
        )

        # 不合法语言静默处理，不报错
        assert resp.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("_init_virtual_tenant_users")
class TestVirtualUserSearchApi:
    def test_with_username(self, api_client):
        """通过 username 关键字搜索虚拟用户"""
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan", data_source__type="virtual")
        resp = api_client.get(
            reverse("open_web.tenant.virtual_user.search"),
            data={"keyword": "zhang"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == zhangsan.id
        assert resp.data[0]["login_name"] == "zhangsan"
        assert resp.data[0]["full_name"] == "张三"
        assert resp.data[0]["display_name"] == "zhangsan(张三)"
        assert resp.data[0]["status"] == TenantUserStatus.ENABLED

    def test_with_full_name(self, api_client):
        """通过 full_name 关键字搜索虚拟用户"""
        lisi = TenantUser.objects.get(data_source_user__username="lisi", data_source__type="virtual")
        resp = api_client.get(
            reverse("open_web.tenant.virtual_user.search"),
            data={"keyword": "李四"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == lisi.id
        assert resp.data[0]["login_name"] == "lisi"
        assert resp.data[0]["full_name"] == "李四"
        assert resp.data[0]["display_name"] == "lisi(李四)"

    def test_with_all_match(self, api_client):
        """搜索所有虚拟用户（使用通用关键字）"""
        resp = api_client.get(
            reverse("open_web.tenant.virtual_user.search"),
            data={"keyword": "si"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["login_name"] == "lisi"


@pytest.mark.usefixtures("_init_virtual_tenant_users")
class TestVirtualUserLookupApi:
    """通过统一 lookup API 使用 data_source_type=virtual 过滤虚拟用户"""

    def test_with_bk_username(self, api_client):
        """通过 bk_username 批量精确查询虚拟用户"""
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan", data_source__type="virtual")
        lisi = TenantUser.objects.get(data_source_user__username="lisi", data_source__type="virtual")
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": ",".join([zhangsan.id, lisi.id]),
                "lookup_fields": "bk_username",
                "data_source_type": "virtual",
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}

    def test_with_full_name(self, api_client):
        """通过 full_name 批量精确查询虚拟用户"""
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan", data_source__type="virtual")
        lisi = TenantUser.objects.get(data_source_user__username="lisi", data_source__type="virtual")
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={"lookups": "张三,李四", "lookup_fields": "full_name", "data_source_type": "virtual"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}

    def test_with_multiple_lookup_fields(self, api_client):
        """同时使用多个 lookup_fields 查询虚拟用户"""
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan", data_source__type="virtual")
        lisi = TenantUser.objects.get(data_source_user__username="lisi", data_source__type="virtual")
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": ",".join([zhangsan.id, lisi.id]),
                "lookup_fields": "bk_username,login_name",
                "data_source_type": "virtual",
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["bk_username"] for t in resp.data} == {zhangsan.id, lisi.id}
        assert {t["login_name"] for t in resp.data} == {"zhangsan", "lisi"}
        assert {t["full_name"] for t in resp.data} == {"张三", "李四"}
        assert {t["display_name"] for t in resp.data} == {"zhangsan(张三)", "lisi(李四)"}

    def test_with_not_match(self, api_client):
        """查询不存在的虚拟用户"""
        resp = api_client.get(
            reverse("open_web.tenant_user.lookup"),
            data={
                "lookups": "not_exist_user1,not_exist_user2",
                "lookup_fields": "login_name",
                "data_source_type": "virtual",
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

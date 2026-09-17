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
from bkuser.apis.open_web.views.departments import TenantDepartmentSearchApi
from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceDepartmentUserRelation, DataSourceUser
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
@pytest.mark.usefixtures("_init_collaboration_users_depts")
class TestTenantDepartmentSearchApi:
    def test_with_current_tenant(self, api_client, random_tenant):
        center_ba = TenantDepartment.objects.get(
            data_source_department__name="中心BA",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )

        resp = api_client.get(
            reverse("open_web.tenant_department.search"),
            data={"keyword": "中心B", "owner_tenant_id": random_tenant.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data[0]["id"] == center_ba.id
        assert resp.data[0]["name"] == "中心BA"
        assert resp.data[0]["owner_tenant_id"] == random_tenant.id
        assert resp.data[0]["organization_path"] == "公司/部门B"
        assert resp.data[0]["has_child"]
        assert resp.data[0]["has_user"]

    def test_with_not_child(self, api_client, random_tenant):
        group_baa = TenantDepartment.objects.get(
            data_source_department__name="小组BAA",
            data_source__type="real",
            data_source__owner_tenant_id=random_tenant.id,
        )

        resp = api_client.get(
            reverse("open_web.tenant_department.search"),
            data={"keyword": "小组BA", "owner_tenant_id": random_tenant.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data[0]["id"] == group_baa.id
        assert resp.data[0]["name"] == "小组BAA"
        assert resp.data[0]["owner_tenant_id"] == random_tenant.id
        assert resp.data[0]["organization_path"] == "公司/部门B/中心BA"
        assert not resp.data[0]["has_child"]
        assert resp.data[0]["has_user"]

    def test_with_collaboration_tenant(self, api_client, random_tenant, collaboration_tenant):
        collab_center_ba = TenantDepartment.objects.get(
            data_source_department__name="中心BA",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )

        resp = api_client.get(
            reverse("open_web.tenant_department.search"),
            data={"keyword": "中心B", "owner_tenant_id": collaboration_tenant.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data[0]["id"] == collab_center_ba.id
        assert resp.data[0]["name"] == "中心BA"
        assert resp.data[0]["owner_tenant_id"] == collaboration_tenant.id
        assert resp.data[0]["organization_path"] == "公司/部门B"
        assert resp.data[0]["has_child"]
        assert resp.data[0]["has_user"]

    def test_with_all_depts(self, api_client, random_tenant, collaboration_tenant):
        ceter_ba = TenantDepartment.objects.get(
            data_source_department__name="中心BA",
            data_source__owner_tenant_id=random_tenant.id,
        )
        collab_center_ba = TenantDepartment.objects.get(
            data_source_department__name="中心BA",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )

        resp = api_client.get(reverse("open_web.tenant_department.search"), data={"keyword": "中心B"})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["id"] for t in resp.data} == {ceter_ba.id, collab_center_ba.id}
        assert {t["name"] for t in resp.data} == {"中心BA"}
        assert {t["owner_tenant_id"] for t in resp.data} == {random_tenant.id, collaboration_tenant.id}
        assert {t["organization_path"] for t in resp.data} == {"公司/部门B"}
        assert {t["has_child"] for t in resp.data} == {True}
        assert {t["has_user"] for t in resp.data} == {True}

    def test_with_not_match(self, api_client):
        resp = api_client.get(reverse("open_web.tenant_department.search"), data={"keyword": "chen"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantDepartmentSearchApiWithExclusion:
    """部门搜索 - 黑名单排除（必须发生在 search_limit 截断之前）"""

    def test_exclude_self_and_descendants(self, api_client, random_tenant):
        """排除「部门A」后，其自身及子孙都不应出现，「部门B」分支不受影响"""
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")

        resp = api_client.get(
            reverse("open_web.tenant_department.search"),
            data={"keyword": "A", "excluded_department_ids": str(dept_a.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        # keyword=A 可命中 部门A/中心AA/中心AB/小组AAA/小组ABA/中心BA/小组BAA，前 5 个应被排除
        assert {d["name"] for d in resp.data} == {"中心BA", "小组BAA"}

    def test_not_exclude_other_branch(self, api_client, random_tenant):
        """排除「部门A」不应影响「部门B」分支"""
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")

        resp = api_client.get(
            reverse("open_web.tenant_department.search"),
            data={"keyword": "小组", "excluded_department_ids": str(dept_a.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert {d["name"] for d in resp.data} == {"小组BAA"}

    def test_exclude_before_search_limit(self, api_client, random_tenant):
        """
        关键用例：卡住「先截断再由调用方过滤」的实现

        将 search_limit 调整为 1，keyword 命中「中心AA / 中心AB / 中心BA」，
        若排除发生在截断之后，则结果会为空；正确实现应返回「中心BA」
        """
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")

        with mock.patch.object(TenantDepartmentSearchApi, "search_limit", 1):
            resp = api_client.get(
                reverse("open_web.tenant_department.search"),
                data={"keyword": "中心", "excluded_department_ids": str(dept_a.id)},
            )

        assert resp.status_code == status.HTTP_200_OK
        assert [d["name"] for d in resp.data] == ["中心BA"]

    def test_with_blank_excluded_department_ids(self, api_client):
        """
        传空值等价于不传

        Note: DRF 对 QueryDict（HTML 表单输入）中非必填字段的空串会视作未提供该字段，
         因此前端拼接出 `?excluded_department_ids=` 时不会报错
        """
        resp = api_client.get(
            reverse("open_web.tenant_department.search"),
            data={"keyword": "小组", "excluded_department_ids": ""},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert {d["name"] for d in resp.data} == {"小组AAA", "小组ABA", "小组BAA"}

    def test_without_excluded_department_ids(self, api_client):
        """不传该参数时与现网行为一致"""
        resp = api_client.get(reverse("open_web.tenant_department.search"), data={"keyword": "小组"})

        assert resp.status_code == status.HTTP_200_OK
        assert {d["name"] for d in resp.data} == {"小组AAA", "小组ABA", "小组BAA"}

    def test_with_too_many_excluded_department_ids(self, api_client):
        resp = api_client.get(
            reverse("open_web.tenant_department.search"),
            data={"keyword": "小组", "excluded_department_ids": ",".join(map(str, range(1, 102)))},
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("_init_second_root_dept")
class TestExcludeRootDepartment:
    """
    拉黑整个根部门 —— 组织选择器最常见的黑名单用法

    组织树形如：
      公司           <- 保留
      外部合作伙伴     <- 拉黑（连带「合作中心A」及其下人员）
    """

    def test_dept_search_excludes_whole_root_tree(self, api_client):
        """搜索「中心」时，被拉黑根部门下的「合作中心A」不应出现，其他根部门下的中心正常返回"""
        partner = TenantDepartment.objects.get(data_source_department__code="partner")

        resp = api_client.get(
            reverse("open_web.tenant_department.search"),
            data={"keyword": "中心", "excluded_department_ids": str(partner.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert {d["name"] for d in resp.data} == {"中心AA", "中心AB", "中心BA"}

    def test_dept_search_excludes_root_itself(self, api_client):
        partner = TenantDepartment.objects.get(data_source_department__code="partner")

        resp = api_client.get(
            reverse("open_web.tenant_department.search"),
            data={"keyword": "合作", "excluded_department_ids": str(partner.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

    def test_other_root_not_affected(self, api_client):
        """拉黑一个根部门不应影响另一棵树（不同 tree_id）"""
        company = TenantDepartment.objects.get(data_source_department__code="company")

        resp = api_client.get(
            reverse("open_web.tenant_department.search"),
            data={"keyword": "合作", "excluded_department_ids": str(company.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert {d["name"] for d in resp.data} == {"外部合作伙伴", "合作中心A"}

    def test_user_search_excludes_whole_root_tree(self, api_client):
        """被拉黑根部门下的人员（含深层子部门）都搜不到"""
        partner = TenantDepartment.objects.get(data_source_department__code="partner")

        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "伙伴", "excluded_department_ids": str(partner.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

    def test_user_search_keeps_other_root_users(self, api_client):
        partner = TenantDepartment.objects.get(data_source_department__code="partner")

        resp = api_client.get(
            reverse("open_web.tenant_user.search"),
            data={"keyword": "zhangsan", "excluded_department_ids": str(partner.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [d["login_name"] for d in resp.data] == ["zhangsan"]

    def test_dept_user_list_excludes_multi_org_user_in_blacklisted_root(self, api_client, full_local_data_source):
        """
        多组织人员：一个归属在被拉黑的根树下，从另一个未拉黑部门点进去也不应出现
        """
        partner_center = DataSourceDepartment.objects.get(code="partner_center_a")
        zhaoliu_ds = DataSourceUser.objects.get(username="zhaoliu")
        # 让 zhaoliu 额外归属到被拉黑根树下的「合作中心A」
        DataSourceDepartmentUserRelation.objects.create(
            department=partner_center, user=zhaoliu_ds, data_source=full_local_data_source
        )

        center_aa = TenantDepartment.objects.get(data_source_department__code="center_aa")
        partner = TenantDepartment.objects.get(data_source_department__code="partner")

        resp = api_client.get(
            reverse("open_web.tenant_department.user.list", kwargs={"id": center_aa.id}),
            data={"excluded_department_ids": str(partner.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert "zhaoliu" not in {d["login_name"] for d in resp.data}

    def test_lookup_excludes_descendant_of_blacklisted_root(self, api_client):
        """回填「合作中心A」时拉黑其根部门，不应出现"""
        partner = TenantDepartment.objects.get(data_source_department__code="partner")
        partner_center = TenantDepartment.objects.get(data_source_department__code="partner_center_a")
        center_aa = TenantDepartment.objects.get(data_source_department__code="center_aa")

        resp = api_client.get(
            reverse("open_web.tenant_department.lookup"),
            data={
                "department_ids": f"{partner_center.id},{center_aa.id}",
                "excluded_department_ids": str(partner.id),
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [d["id"] for d in resp.data] == [center_aa.id]

    def test_root_children_list_returns_both_roots(self, api_client, random_tenant):
        """children 接口不带排除参数：根部门列表原样返回，由调用方按自身 id 过滤"""
        resp = api_client.get(
            reverse("open_web.tenant_department.child.list", kwargs={"id": 0}),
            data={"owner_tenant_id": random_tenant.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert {d["name"] for d in resp.data} == {"公司", "外部合作伙伴"}


class TestTenantDepartmentChildrenListApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_current_tenant(self, api_client, random_tenant):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")
        center_ab = TenantDepartment.objects.get(data_source_department__name="中心AB")

        resp = api_client.get(reverse("open_web.tenant_department.child.list", kwargs={"id": dept_a.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {d["id"] for d in resp.data} == {center_aa.id, center_ab.id}
        assert {d["name"] for d in resp.data} == {"中心AA", "中心AB"}
        assert {d["has_child"] for d in resp.data} == {True}
        assert {d["has_user"] for d in resp.data} == {True}

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_sub_dept_with_not_child(self, api_client, random_tenant):
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")
        group_aaa = TenantDepartment.objects.get(data_source_department__name="小组AAA")

        resp = api_client.get(reverse("open_web.tenant_department.child.list", kwargs={"id": center_aa.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["id"] == group_aaa.id
        assert resp.data[0]["name"] == "小组AAA"
        assert not resp.data[0]["has_child"]
        assert resp.data[0]["has_user"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_not_child(self, api_client, random_tenant):
        group_aaa = TenantDepartment.objects.get(data_source_department__name="小组AAA")

        resp = api_client.get(reverse("open_web.tenant_department.child.list", kwargs={"id": group_aaa.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_with_collaboration_tenant(self, api_client, collaboration_tenant):
        dept_a = TenantDepartment.objects.get(
            data_source_department__name="部门A",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )
        center_aa = TenantDepartment.objects.get(
            data_source_department__name="中心AA",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )
        center_ab = TenantDepartment.objects.get(
            data_source_department__name="中心AB",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )

        resp = api_client.get(reverse("open_web.tenant_department.child.list", kwargs={"id": dept_a.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {d["id"] for d in resp.data} == {center_aa.id, center_ab.id}
        assert {d["name"] for d in resp.data} == {"中心AA", "中心AB"}
        assert {d["has_child"] for d in resp.data} == {True}
        assert {d["has_user"] for d in resp.data} == {True}

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_root_department(self, api_client, random_tenant):
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        resp = api_client.get(
            reverse("open_web.tenant_department.child.list", kwargs={"id": 0}),
            data={"owner_tenant_id": random_tenant.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["id"] == company.id
        assert resp.data[0]["name"] == "公司"
        assert resp.data[0]["has_child"]
        assert resp.data[0]["has_user"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_invalid_owner_tenant_id(self, api_client, random_tenant):
        resp = api_client.get(reverse("open_web.tenant_department.child.list", kwargs={"id": 0}))

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_invalid_department(self, api_client, random_tenant):
        resp = api_client.get(
            reverse("open_web.tenant_department.child.list", kwargs={"id": 123456}),
            data={"owner_tenant_id": random_tenant.id},
        )

        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestTenantDepartmentUserListApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_current_tenant(self, api_client, random_tenant):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        wangwu = TenantUser.objects.get(data_source_user__username="wangwu")

        resp = api_client.get(reverse("open_web.tenant_department.user.list", kwargs={"id": dept_a.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {d["bk_username"] for d in resp.data} == {lisi.id, wangwu.id}
        assert {d["login_name"] for d in resp.data} == {"lisi", "wangwu"}
        assert {d["display_name"] for d in resp.data} == {"lisi(李四)", "wangwu(王五)"}

    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_with_collaboration_tenant(self, api_client, collaboration_tenant):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        wangwu = TenantUser.objects.get(data_source_user__username="wangwu")

        resp = api_client.get(reverse("open_web.tenant_department.user.list", kwargs={"id": dept_a.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {d["bk_username"] for d in resp.data} == {lisi.id, wangwu.id}
        assert {d["login_name"] for d in resp.data} == {"lisi", "wangwu"}
        assert {d["display_name"] for d in resp.data} == {"lisi(李四)", "wangwu(王五)"}

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_no_department(self, api_client, random_tenant):
        freedom = TenantUser.objects.get(data_source_user__username="freedom")
        resp = api_client.get(
            reverse("open_web.tenant_department.user.list", kwargs={"id": 0}),
            data={"owner_tenant_id": random_tenant.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["bk_username"] == freedom.id
        assert resp.data[0]["login_name"] == "freedom"
        assert resp.data[0]["display_name"] == "freedom(自由人)"

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_invalid_owner_tenant_id(self, api_client, random_tenant):
        resp = api_client.get(reverse("open_web.tenant_department.user.list", kwargs={"id": 0}))

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_invalid_department(self, api_client, random_tenant):
        resp = api_client.get(reverse("open_web.tenant_department.user.list", kwargs={"id": 123456}))

        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantDepartmentUserListApiWithExclusion:
    """部门下翻人 - 黑名单排除（必须发生在分页之前）"""

    def test_exclude_user_ids(self, api_client):
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        wangwu = TenantUser.objects.get(data_source_user__username="wangwu")

        resp = api_client.get(
            reverse("open_web.tenant_department.user.list", kwargs={"id": dept_a.id}),
            data={"excluded_user_ids": lisi.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [d["bk_username"] for d in resp.data] == [wangwu.id]

    def test_exclude_multi_org_user_by_other_branch(self, api_client):
        """
        多组织用户：wangwu 同时属于「部门A」和「部门B」

        从「部门A」点进去并排除「部门B」，wangwu 也不应出现（lisi 只属于部门A 分支，应保留）
        """
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")
        dept_b = TenantDepartment.objects.get(data_source_department__code="dept_b")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")

        resp = api_client.get(
            reverse("open_web.tenant_department.user.list", kwargs={"id": dept_a.id}),
            data={"excluded_department_ids": str(dept_b.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [d["bk_username"] for d in resp.data] == [lisi.id]

    def test_exclude_by_ancestor_department(self, api_client):
        """
        排除「中心BA」的祖先「部门B」时，挂在「中心BA」上的 lushi 也应被排除

        lushi 同时属于「小组ABA」和「中心BA」，从「小组ABA」点进去、排除「部门B」，lushi 应被排除
        """
        group_aba = TenantDepartment.objects.get(data_source_department__code="group_aba")
        dept_b = TenantDepartment.objects.get(data_source_department__code="dept_b")
        linshiyi = TenantUser.objects.get(data_source_user__username="linshiyi")

        resp = api_client.get(
            reverse("open_web.tenant_department.user.list", kwargs={"id": group_aba.id}),
            data={"excluded_department_ids": str(dept_b.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [d["bk_username"] for d in resp.data] == [linshiyi.id]

    def test_exclude_before_pagination(self, api_client):
        """
        关键用例：卡住「先分页再由调用方过滤」的实现

        「部门A」下有 lisi、wangwu 两人，page_size=1 时排除 lisi：
        若排除发生在分页之后，第一页会是空数组；正确实现应直接返回 wangwu
        """
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        wangwu = TenantUser.objects.get(data_source_user__username="wangwu")

        resp = api_client.get(
            reverse("open_web.tenant_department.user.list", kwargs={"id": dept_a.id}),
            data={"page": 1, "page_size": 1, "excluded_user_ids": lisi.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [d["bk_username"] for d in resp.data] == [wangwu.id]

    def test_no_department_user_only_affected_by_excluded_user_ids(self, api_client, random_tenant):
        """无部门用户只受 excluded_user_ids 影响"""
        company = TenantDepartment.objects.get(data_source_department__code="company")
        freedom = TenantUser.objects.get(data_source_user__username="freedom")

        resp = api_client.get(
            reverse("open_web.tenant_department.user.list", kwargs={"id": 0}),
            data={"owner_tenant_id": random_tenant.id, "excluded_department_ids": str(company.id)},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert [d["bk_username"] for d in resp.data] == [freedom.id]

        resp = api_client.get(
            reverse("open_web.tenant_department.user.list", kwargs={"id": 0}),
            data={"owner_tenant_id": random_tenant.id, "excluded_user_ids": freedom.id},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

    def test_without_exclusion_params(self, api_client):
        """不传排除参数时行为与现网一致"""
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        wangwu = TenantUser.objects.get(data_source_user__username="wangwu")

        resp = api_client.get(reverse("open_web.tenant_department.user.list", kwargs={"id": dept_a.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert {d["bk_username"] for d in resp.data} == {lisi.id, wangwu.id}


@pytest.mark.usefixtures("_init_tenant_users_depts")
@pytest.mark.usefixtures("_init_collaboration_users_depts")
class TestTenantDepartmentLookupApi:
    def test_with_all_depts(self, api_client, random_tenant, collaboration_tenant):
        dept_a = TenantDepartment.objects.get(
            data_source_department__name="部门A", data_source__owner_tenant_id=random_tenant.id
        )
        center_aa = TenantDepartment.objects.get(
            data_source_department__name="中心AA", data_source__owner_tenant_id=random_tenant.id
        )
        collab_dept_a = TenantDepartment.objects.get(
            data_source_department__name="部门A", data_source__owner_tenant_id=collaboration_tenant.id
        )
        collab_center_aa = TenantDepartment.objects.get(
            data_source_department__name="中心AA", data_source__owner_tenant_id=collaboration_tenant.id
        )

        resp = api_client.get(
            reverse("open_web.tenant_department.lookup"),
            data={
                "department_ids": ",".join(
                    [str(dept_a.id), str(center_aa.id), str(collab_dept_a.id), str(collab_center_aa.id)]
                )
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 4
        assert {d["id"] for d in resp.data} == {dept_a.id, center_aa.id, collab_dept_a.id, collab_center_aa.id}
        assert {d["name"] for d in resp.data} == {"部门A", "中心AA"}
        assert {d["owner_tenant_id"] for d in resp.data} == {random_tenant.id, collaboration_tenant.id}
        assert {d["organization_path"] for d in resp.data} == {"公司", "公司/部门A"}

    def test_with_not_match(self, api_client):
        resp = api_client.get(reverse("open_web.tenant_department.lookup"), data={"department_ids": "123456"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantDepartmentLookupApiWithExclusion:
    """部门 lookup - 黑名单排除（回填场景，调用方无法自行判断祖先）"""

    def test_exclude_descendant_department(self, api_client):
        """回填「中心AA」时排除其祖先「部门A」，中心AA 不应出现"""
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")
        center_aa = TenantDepartment.objects.get(data_source_department__code="center_aa")
        center_ba = TenantDepartment.objects.get(data_source_department__code="center_ba")

        resp = api_client.get(
            reverse("open_web.tenant_department.lookup"),
            data={
                "department_ids": f"{center_aa.id},{center_ba.id}",
                "excluded_department_ids": str(dept_a.id),
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert [d["id"] for d in resp.data] == [center_ba.id]

    def test_exclude_self(self, api_client):
        center_aa = TenantDepartment.objects.get(data_source_department__code="center_aa")

        resp = api_client.get(
            reverse("open_web.tenant_department.lookup"),
            data={"department_ids": str(center_aa.id), "excluded_department_ids": str(center_aa.id)},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

    def test_without_exclusion_params(self, api_client):
        center_aa = TenantDepartment.objects.get(data_source_department__code="center_aa")

        resp = api_client.get(reverse("open_web.tenant_department.lookup"), data={"department_ids": str(center_aa.id)})

        assert resp.status_code == status.HTTP_200_OK
        assert [d["id"] for d in resp.data] == [center_aa.id]

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
from bkuser.biz.tenant import TenantUserHandler
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
        assert {d["display_name"] for d in resp.data} == {
            TenantUserHandler.generate_tenant_user_display_name(lisi),
            TenantUserHandler.generate_tenant_user_display_name(wangwu),
        }

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
        assert {d["display_name"] for d in resp.data} == {
            TenantUserHandler.generate_tenant_user_display_name(lisi),
            TenantUserHandler.generate_tenant_user_display_name(wangwu),
        }

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
        assert resp.data[0]["display_name"] == TenantUserHandler.generate_tenant_user_display_name(freedom)

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_invalid_owner_tenant_id(self, api_client, random_tenant):
        resp = api_client.get(reverse("open_web.tenant_department.user.list", kwargs={"id": 0}))

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_invalid_department(self, api_client, random_tenant):
        resp = api_client.get(reverse("open_web.tenant_department.user.list", kwargs={"id": 123456}))

        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestTenantDepartmentLookupApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_current_tenant(self, api_client, random_tenant):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")

        resp = api_client.get(
            reverse("open_web.tenant_department.lookup"),
            data={
                "department_ids": ",".join([str(dept_a.id), str(center_aa.id)]),
                "owner_tenant_id": random_tenant.id,
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {d["id"] for d in resp.data} == {dept_a.id, center_aa.id}
        assert {d["name"] for d in resp.data} == {"部门A", "中心AA"}
        assert {d["owner_tenant_id"] for d in resp.data} == {random_tenant.id}
        assert {d["organization_path"] for d in resp.data} == {"公司", "公司/部门A"}

    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_with_collaboration_tenant(self, api_client, collaboration_tenant):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")

        resp = api_client.get(
            reverse("open_web.tenant_department.lookup"),
            data={
                "department_ids": ",".join([str(dept_a.id), str(center_aa.id)]),
                "owner_tenant_id": collaboration_tenant.id,
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {d["id"] for d in resp.data} == {dept_a.id, center_aa.id}
        assert {d["name"] for d in resp.data} == {"部门A", "中心AA"}
        assert {d["owner_tenant_id"] for d in resp.data} == {collaboration_tenant.id}
        assert {d["organization_path"] for d in resp.data} == {"公司", "公司/部门A"}

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    @pytest.mark.usefixtures("_init_collaboration_users_depts")
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

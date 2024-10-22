# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import pytest
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantDepartmentIDRecord
from django.urls import reverse
from rest_framework import status

from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import sync_users_depts_to_tenant

pytestmark = pytest.mark.django_db


class TestTenantDepartmentListApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_list_root_depts(self, api_client, random_tenant):
        """当前租户的根部门"""
        resp = api_client.get(
            reverse(
                "organization.tenant_department.list_create",
                kwargs={"id": random_tenant.id},
            ),
            data={"parent_department_id": 0},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1

        first_dept = resp.data[0]
        excepted_dept = TenantDepartment.objects.get(
            data_source_department__name="公司",
            data_source__owner_tenant_id=random_tenant.id,
        )
        assert first_dept["id"] == excepted_dept.id
        assert first_dept["name"] == excepted_dept.data_source_department.name
        assert first_dept["has_children"] is True

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_list_child_depts(self, api_client, random_tenant):
        """当前租户的某级子部门"""
        company = TenantDepartment.objects.get(
            data_source_department__name="公司",
            data_source__owner_tenant_id=random_tenant.id,
        )
        resp = api_client.get(
            reverse(
                "organization.tenant_department.list_create",
                kwargs={"id": random_tenant.id},
            ),
            data={"parent_department_id": company.id},
        )

        excepted_depts = TenantDepartment.objects.filter(
            data_source_department__name__contains="部门",
            data_source__owner_tenant_id=random_tenant.id,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == excepted_depts.count()
        assert {d["id"] for d in resp.data} == set(excepted_depts.values_list("id", flat=True))
        assert {d["name"] for d in resp.data} == {"部门A", "部门B"}
        assert all(d["has_children"] for d in resp.data)

    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_list_collaboration_root_depts(self, api_client, collaboration_tenant):
        """某协作租户的根部门"""
        resp = api_client.get(
            reverse(
                "organization.tenant_department.list_create",
                kwargs={"id": collaboration_tenant.id},
            ),
            data={"parent_department_id": 0},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1

        excepted_dept = TenantDepartment.objects.get(
            data_source_department__name="公司",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )
        assert resp.data[0]["id"] == excepted_dept.id

    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_list_collaboration_child_depts(self, api_client, collaboration_tenant):
        """某协作租户的某级子部门"""
        dept_a = TenantDepartment.objects.get(
            data_source_department__name="部门A",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )
        resp = api_client.get(
            reverse(
                "organization.tenant_department.list_create",
                kwargs={"id": collaboration_tenant.id},
            ),
            data={"parent_department_id": dept_a.id},
        )

        excepted_depts = TenantDepartment.objects.filter(
            data_source_department__name__contains="中心A",
            data_source__owner_tenant_id=collaboration_tenant.id,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {d["id"] for d in resp.data} == set(excepted_depts.values_list("id", flat=True))


class TestTenantDepartmentCreateApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, full_local_data_source, random_tenant):
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})

        # 创建根部门
        root_dept_name = generate_random_string()
        resp = api_client.post(url, data={"parent_department_id": 0, "name": root_dept_name})
        assert resp.status_code == status.HTTP_201_CREATED

        # 创建子部门
        child_dept_name = generate_random_string()
        company = TenantDepartment.objects.get(data_source_department__name="公司", tenant=random_tenant)
        resp = api_client.post(url, data={"parent_department_id": company.id, "name": child_dept_name})
        assert resp.status_code == status.HTTP_201_CREATED

        codes = DataSourceDepartment.objects.filter(
            data_source=full_local_data_source,
            name__in=[root_dept_name, child_dept_name],
        ).values_list("code", flat=True)

        # 租户部门 ID 会被记录，以便后续复用
        assert TenantDepartmentIDRecord.objects.filter(tenant=random_tenant, code__in=codes).count() == 2

    def test_create_without_data_source(self, api_client, random_tenant):
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})
        resp = api_client.post(url, data={"parent_department_id": 0, "name": generate_random_string()})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "租户数据源不存在" in resp.data["message"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_create_with_invalid_parent_id(self, api_client, random_tenant):
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})
        resp = api_client.post(url, data={"parent_department_id": 10**7, "name": generate_random_string()})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "指定的父部门在当前租户中不存在" in resp.data["message"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_create_with_duplicate_name(self, api_client, random_tenant):
        company = TenantDepartment.objects.get(data_source_department__name="公司", tenant=random_tenant)
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})

        # duplicate with brother
        resp = api_client.post(url, data={"parent_department_id": company.id, "name": "部门A"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "父部门下已存在同名部门" in resp.data["message"]

        # duplicate with ancestor
        resp = api_client.post(url, data={"parent_department_id": company.id, "name": "公司"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "上级部门中存在同名部门" in resp.data["message"]

    def test_create_other_tenant_dept(self, api_client, random_tenant, collaboration_tenant):
        url = reverse("organization.tenant_department.list_create", kwargs={"id": collaboration_tenant.id})
        resp = api_client.post(url, data={"parent_department_id": 0, "name": generate_random_string()})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "仅可创建属于当前租户的部门" in resp.data["message"]


class TestTenantDepartmentUpdateApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant):
        company = TenantDepartment.objects.get(data_source_department__name="公司", tenant=random_tenant)
        url = reverse("organization.tenant_department.update_destroy", kwargs={"id": company.id})
        resp = api_client.put(url, data={"name": "总公司"})
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        company.refresh_from_db()
        assert company.data_source_department.name == "总公司"

    def test_update_invalid_dept(self, api_client):
        url = reverse("organization.tenant_department.update_destroy", kwargs={"id": 10**7})
        resp = api_client.put(url, data={"name": generate_random_string()})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_update_with_duplicate_name(self, api_client, random_tenant):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A", tenant=random_tenant)
        url = reverse("organization.tenant_department.update_destroy", kwargs={"id": dept_a.id})

        # duplicate_with_self is ok
        resp = api_client.put(url, data={"name": "部门A"})
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # duplicate with brother
        resp = api_client.put(url, data={"name": "部门B"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "父部门下已存在同名部门" in resp.data["message"]

        # duplicate with ancestor
        resp = api_client.put(url, data={"name": "公司"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "上级部门中存在同名部门" in resp.data["message"]


class TestTenantDepartmentDestroyApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant):
        center_ba = TenantDepartment.objects.get(data_source_department__name="中心BA", tenant=random_tenant)
        url = reverse("organization.tenant_department.update_destroy", kwargs={"id": center_ba.id})

        resp = api_client.delete(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "部门下存在用户" in resp.data["message"]

        # 仅仅解除本层级的用户关联还不行，子部门有用户也不能删除
        DataSourceDepartmentUserRelation.objects.filter(department_id=center_ba.data_source_department_id).delete()
        resp = api_client.delete(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "部门下存在用户" in resp.data["message"]

        # 把子部门里面的用户关系都解除后才可以删除该部门
        DataSourceDepartmentUserRelation.objects.filter(department__name="小组BAA").delete()
        resp = api_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_collaboration(self, api_client, random_tenant, collaboration_tenant, full_local_data_source):
        # 从随机租户协同数据到协同租户
        sync_users_depts_to_tenant(collaboration_tenant, full_local_data_source)

        dept_b = TenantDepartment.objects.get(data_source_department__name="部门B", tenant=random_tenant)
        # 把关联数据都干掉，专心测试删除的影响情况
        DataSourceDepartmentUserRelation.objects.filter(data_source__owner_tenant_id=random_tenant.id).delete()

        resp = api_client.delete(reverse("organization.tenant_department.update_destroy", kwargs={"id": dept_b.id}))
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        tenant_ids = [random_tenant.id, collaboration_tenant.id]
        deleted_dept_codes = ["dept_b", "center_ba", "group_baa"]
        # 租户部门和子部门都干掉了
        assert not TenantDepartment.objects.filter(
            tenant_id__in=tenant_ids, data_source_department__code__in=deleted_dept_codes
        ).exists()
        # 数据源部门也是活不了
        assert not DataSourceDepartment.objects.filter(
            data_source=full_local_data_source, code__in=deleted_dept_codes
        ).exists()
        # mptt 树里面的也别想跑
        assert not DataSourceDepartmentRelation.objects.filter(
            data_source=full_local_data_source, department__code__in=deleted_dept_codes
        ).exists()

    def test_delete_invalid_dept(self, api_client):
        resp = api_client.delete(reverse("organization.tenant_department.update_destroy", kwargs={"id": 10**7}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestTenantDepartmentSearchApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_single_tenant(self, api_client, random_tenant):
        resp = api_client.get(reverse("organization.tenant_department.search"), data={"keyword": "小组"})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 3  # noqa: PLR2004  magic number here is ok

        assert {dept["name"] for dept in resp.data} == {"小组AAA", "小组ABA", "小组BAA"}
        assert all(dept["tenant_id"] == random_tenant.id for dept in resp.data)
        assert {dept["organization_path"] for dept in resp.data} == {
            "公司/部门A/中心AA/小组AAA",
            "公司/部门A/中心AB/小组ABA",
            "公司/部门B/中心BA/小组BAA",
        }

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_multi_tenant(self, api_client, random_tenant, collaboration_tenant):
        resp = api_client.get(reverse("organization.tenant_department.search"), data={"keyword": "部门"})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 4  # noqa: PLR2004  magic number here is ok

        assert {dept["name"] for dept in resp.data} == {"部门A", "部门B"}
        assert {dept["tenant_id"] for dept in resp.data} == {random_tenant.id, collaboration_tenant.id}
        assert {dept["organization_path"] for dept in resp.data} == {"公司/部门A", "公司/部门B"}

    def test_match_nothing(self, api_client):
        resp = api_client.get(reverse("organization.tenant_department.search"), data={"keyword": "2887"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0


class TestOptionalTenantDepartmentListApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_search_dept(self, api_client, random_tenant):
        resp = api_client.get(reverse("organization.optional_department.list"), data={"keyword": "部门"})

        assert resp.status_code == status.HTTP_200_OK
        assert {dept["name"] for dept in resp.data} == {"部门A", "部门B"}
        assert {dept["organization_path"] for dept in resp.data} == {"公司/部门A", "公司/部门B"}

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_search_aa_keyword(self, api_client, random_tenant):
        resp = api_client.get(reverse("organization.optional_department.list"), data={"keyword": "AA"})

        assert resp.status_code == status.HTTP_200_OK
        assert {dept["name"] for dept in resp.data} == {"中心AA", "小组AAA", "小组BAA"}
        assert {dept["organization_path"] for dept in resp.data} == {
            "公司/部门A/中心AA",
            "公司/部门A/中心AA/小组AAA",
            "公司/部门B/中心BA/小组BAA",
        }


class TestTenantDepartmentParentUpdateApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_dept_parent_update(self, api_client, random_tenant):
        """将小组 BAA 移动至中心 AB 下"""

        group_baa = TenantDepartment.objects.get(data_source_department__name="小组BAA", tenant=random_tenant)
        center_ab = TenantDepartment.objects.get(data_source_department__name="中心AB", tenant=random_tenant)

        url = reverse("organization.tenant_department.parent.update", kwargs={"id": group_baa.id})
        resp = api_client.put(url, data={"parent_department_id": center_ab.id})

        assert resp.status_code == status.HTTP_204_NO_CONTENT

        group_baa_dept_relation = DataSourceDepartmentRelation.objects.get(department=group_baa.data_source_department)
        center_ab_dept_relation = DataSourceDepartmentRelation.objects.get(department=center_ab.data_source_department)
        assert group_baa_dept_relation.parent == center_ab_dept_relation

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_dept_parent_update_to_root(self, api_client, random_tenant):
        """将小组 BAA 移动至根部门"""

        group_baa = TenantDepartment.objects.get(data_source_department__name="小组BAA", tenant=random_tenant)

        url = reverse("organization.tenant_department.parent.update", kwargs={"id": group_baa.id})
        resp = api_client.put(url, data={"parent_department_id": 0})

        assert resp.status_code == status.HTTP_204_NO_CONTENT

        group_baa_dept_relation = DataSourceDepartmentRelation.objects.get(department=group_baa.data_source_department)
        assert group_baa_dept_relation.parent is None

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_dept_parent_update_to_itself(self, api_client, random_tenant):
        """将小组 BAA 移动至自己下面"""

        group_baa = TenantDepartment.objects.get(data_source_department__name="小组BAA", tenant=random_tenant)

        url = reverse("organization.tenant_department.parent.update", kwargs={"id": group_baa.id})
        resp = api_client.put(url, data={"parent_department_id": group_baa.id})

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "自己不能成为自己的子部门" in resp.data["message"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_dept_parent_update_to_descendant(self, api_client, random_tenant):
        """将部门 A 移动至自己的子部门小组 ABA 下"""

        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A", tenant=random_tenant)
        group_aaa = TenantDepartment.objects.get(data_source_department__name="小组AAA", tenant=random_tenant)

        url = reverse("organization.tenant_department.parent.update", kwargs={"id": dept_a.id})
        resp = api_client.put(url, data={"parent_department_id": group_aaa.id})

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不能移动至自己的子部门下" in resp.data["message"]

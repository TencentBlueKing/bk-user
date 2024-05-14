# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import pytest
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentUserRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestTenantDeptUserRelationBatchCreateApi:
    """测试 批量添加 / 拉取租户用户（添加部门 - 用户关系）"""

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant):
        linshiyi = TenantUser.objects.get(data_source_user__username="linshiyi", tenant=random_tenant)
        baishier = TenantUser.objects.get(data_source_user__username="baishier", tenant=random_tenant)
        group_aaa = TenantDepartment.objects.get(data_source_department__name="小组AAA", tenant=random_tenant)
        group_aba = TenantDepartment.objects.get(data_source_department__name="小组ABA", tenant=random_tenant)

        resp = api_client.post(
            reverse("organization.tenant_dept_user_relation.batch_create"),
            data={
                "user_ids": [linshiyi.id, baishier.id],
                "target_department_ids": [group_aaa.id, group_aba.id],
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # baishier 属于小组 BAA，linshiyi 属于小组 ABA，将他们两个添加到 小组 AAA & 小组 ABA
        # 则 baishier 应该属于三个组，linshiyi 属于两个组（因为原来就在 小组 ABA 中，会忽略冲突）
        dept_ids = DataSourceDepartmentUserRelation.objects.filter(user_id=linshiyi.data_source_user_id).values_list(
            "department_id", flat=True
        )
        dept_names = set(DataSourceDepartment.objects.filter(id__in=dept_ids).values_list("name", flat=True))
        assert dept_names == {"小组AAA", "小组ABA"}

        dept_ids = DataSourceDepartmentUserRelation.objects.filter(user_id=baishier.data_source_user_id).values_list(
            "department_id", flat=True
        )
        dept_names = set(DataSourceDepartment.objects.filter(id__in=dept_ids).values_list("name", flat=True))
        assert dept_names == {"小组AAA", "小组ABA", "小组BAA"}

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_invalid_user_id(self, api_client, random_tenant):
        company = TenantDepartment.objects.get(data_source_department__name="公司", tenant=random_tenant)

        resp = api_client.post(
            reverse("organization.tenant_dept_user_relation.batch_create"),
            data={"user_ids": ["not_exists"], "target_department_ids": [company.id]},
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户 ID not_exists 在当前租户中不存在" in resp.data["message"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_invalid_department_id(self, api_client, random_tenant):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan", tenant=random_tenant)

        resp = api_client.post(
            reverse("organization.tenant_dept_user_relation.batch_create"),
            data={"user_ids": [zhangsan.id], "target_department_ids": [-1]},
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "部门 ID {-1} 在当前租户中不存在" in resp.data["message"]


class TestTenantDeptUserRelationBatchUpdatePutApi:
    """测试 清空并加入到其他组织（会删除当前所有关系）"""

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant):
        wangwu = TenantUser.objects.get(data_source_user__username="wangwu", tenant=random_tenant)
        liuqi = TenantUser.objects.get(data_source_user__username="liuqi", tenant=random_tenant)
        dept_b = TenantDepartment.objects.get(data_source_department__name="部门B", tenant=random_tenant)
        center_ab = TenantDepartment.objects.get(data_source_department__name="中心AB", tenant=random_tenant)

        resp = api_client.put(
            reverse("organization.tenant_dept_user_relation.batch_update"),
            data={
                "user_ids": [wangwu.id, liuqi.id],
                "target_department_ids": [dept_b.id, center_ab.id],
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # wangwu 属于部门 A & 部门 B，linshiyi 属于小组 AAA，将他们清空并加入
        # 部门 B & 中心 AB，则 wangwu，liuqi 应该只属于部门 B & 中心 AB
        for user in [wangwu, liuqi]:
            relations = DataSourceDepartmentUserRelation.objects.filter(user_id=user.data_source_user_id)
            assert set(relations.values_list("department_id", flat=True)) == {
                dept_b.data_source_department_id,
                center_ab.data_source_department_id,
            }


class TestTenantDeptUserRelationBatchUpdatePatchApi:
    """测试 移至其他组织（仅删除当前部门关系）"""

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant):
        lushi = TenantUser.objects.get(data_source_user__username="lushi", tenant=random_tenant)
        linshiyi = TenantUser.objects.get(data_source_user__username="linshiyi", tenant=random_tenant)
        group_aaa = TenantDepartment.objects.get(data_source_department__name="小组AAA", tenant=random_tenant)
        group_aba = TenantDepartment.objects.get(data_source_department__name="小组ABA", tenant=random_tenant)
        group_baa = TenantDepartment.objects.get(data_source_department__name="小组BAA", tenant=random_tenant)

        resp = api_client.patch(
            reverse("organization.tenant_dept_user_relation.batch_update"),
            data={
                "user_ids": [lushi.id, linshiyi.id],
                "target_department_ids": [group_aaa.id, group_baa.id],
                "source_department_id": group_aba.id,
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # lushi 属中心 BA，小组 ABA，linshiyi 只属于小组 ABA，将他们退出小组 ABA 并加入小组 AAA & 小组 BAA
        # 则 lushi 应该属于中心 BA & 小组 AAA & 小组 BAA，linshiyi 应该属于小组 AAA & 小组 BAA
        dept_ids = DataSourceDepartmentUserRelation.objects.filter(user_id=lushi.data_source_user_id).values_list(
            "department_id", flat=True
        )
        dept_names = set(DataSourceDepartment.objects.filter(id__in=dept_ids).values_list("name", flat=True))
        assert dept_names == {"中心BA", "小组AAA", "小组BAA"}

        dept_ids = DataSourceDepartmentUserRelation.objects.filter(user_id=linshiyi.data_source_user_id).values_list(
            "department_id", flat=True
        )
        dept_names = set(DataSourceDepartment.objects.filter(id__in=dept_ids).values_list("name", flat=True))
        assert dept_names == {"小组AAA", "小组BAA"}


class TestTenantDeptUserRelationBatchDeleteApi:
    """测试 移出当前组织（仅删除当前部门关系）"""

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant):
        lisi = TenantUser.objects.get(data_source_user__username="lisi", tenant=random_tenant)
        zhaoliu = TenantUser.objects.get(data_source_user__username="zhaoliu", tenant=random_tenant)
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A", tenant=random_tenant)
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA", tenant=random_tenant)

        resp = api_client.delete(
            reverse("organization.tenant_dept_user_relation.batch_delete"),
            QUERY_STRING=urlencode(
                {
                    "user_ids": ",".join([lisi.id, zhaoliu.id]),
                    "source_department_id": center_aa.id,
                },
                doseq=True,
            ),
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # lisi，zhaoliu 属于中心 AA，将他们移出中心 AA 后，zhaoliu 不属于任何部门，lisi 还属于部门 A
        relations = DataSourceDepartmentUserRelation.objects.filter(user_id=lisi.data_source_user_id)
        assert relations.count() == 1
        assert relations.first().department_id == dept_a.data_source_department_id

        assert not DataSourceDepartmentUserRelation.objects.filter(user_id=zhaoliu.data_source_user_id).exists()

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
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import TenantDepartment
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestListDeptProfileRelations:
    def test_standard(self, api_client, default_tenant, local_data_source):
        resp = api_client.get(reverse("open_v2.list_department_profile_relations"), data={"page": 1, "page_size": 10})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 13  # noqa: PLR2004
        assert len(resp.data["results"]) == 10  # noqa: PLR2004

        dept_ids = {d["department_id"] for d in resp.data["results"]}
        profile_ids = {d["profile_id"] for d in resp.data["results"]}

        # 兼容的 OpenV2 api 中，department_id 是租户部门 ID，profile_id 是数据源用户 ID
        assert TenantDepartment.objects.filter(id__in=dept_ids).count() == len(dept_ids)
        assert DataSourceUser.objects.filter(id__in=profile_ids).count() == len(profile_ids)

    def test_no_page(self, api_client, default_tenant, local_data_source, collaboration_data_source):
        resp = api_client.get(
            reverse("open_v2.list_department_profile_relations"),
            data={"page": 1, "page_size": 10, "no_page": True},
        )

        assert resp.status_code == status.HTTP_200_OK
        # 不分页模式下，没有 count, results 结构
        assert len(resp.data) == 26  # noqa: PLR2004


class TestListProfileLeaderRelations:
    def test_standard(self, api_client, default_tenant, local_data_source):
        resp = api_client.get(reverse("open_v2.list_profile_leader_relations"), data={"page": 1, "page_size": 10})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 11  # noqa: PLR2004
        assert len(resp.data["results"]) == 10  # noqa: PLR2004

        from_profile_ids = {d["from_profile_id"] for d in resp.data["results"]}
        to_profile_ids = {d["to_profile_id"] for d in resp.data["results"]}

        # 兼容的 OpenV2 api 中，from_profile_id，to_profile_id 都是数据源用户 ID
        profile_ids = from_profile_ids | to_profile_ids
        assert DataSourceUser.objects.filter(id__in=profile_ids).count() == len(profile_ids)

    def test_no_page(self, api_client, default_tenant, local_data_source, collaboration_data_source):
        resp = api_client.get(
            reverse("open_v2.list_profile_leader_relations"),
            data={"page": 1, "page_size": 10, "no_page": True},
        )

        assert resp.status_code == status.HTTP_200_OK
        # 不分页模式下，没有 count, results 结构
        assert len(resp.data) == 22  # noqa: PLR2004

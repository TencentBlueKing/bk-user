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
from bkuser.apps.tenant.models import TenantDepartment
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestListProfiles:
    def test_standard(self, api_client, local_data_source, collaboration_data_source):
        resp = api_client.get(reverse("open_v2.list_profiles"), data={"page": 1, "page_size": 10})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 22  # noqa: PLR2004
        assert len(resp.data["results"]) == 10  # noqa: PLR2004

    def test_list_with_exist_departments(self, api_client, local_data_source, collaboration_data_source):
        department_ids = TenantDepartment.objects.values_list("id", flat=True)
        resp = api_client.get(
            reverse("open_v2.list_profiles"),
            data={"lookup_field": "departments", "exact_lookups": ",".join(map(str, department_ids))},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 20

    def test_list_with_non_exist_departments(self, api_client, local_data_source, collaboration_data_source):
        resp = api_client.get(
            reverse("open_v2.list_profiles"),
            data={"lookup_field": "departments", "exact_lookups": "9999"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 0

# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestListCategories:
    def test_standard(self, api_client, default_tenant, random_tenant, local_data_source, collaboration_data_source):
        resp = api_client.get(reverse("open_v2.list_categories"))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 2  # noqa: PLR2004
        assert {c["id"] for c in resp.data["results"]} == {local_data_source.id, collaboration_data_source.id}
        assert {c["display_name"] for c in resp.data["results"]} == {default_tenant.name, random_tenant.name}
        assert {c["default"] for c in resp.data["results"]} == {True, False}

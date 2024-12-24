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
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestTenantUserRetrieve:
    def test_retrieve_tenant_user(self, apigw_api_client, default_tenant_user_data, default_tenant):
        resp = apigw_api_client.get(reverse("apigw.tenant_user.retrieve", kwargs={"tenant_user_id": "zhangsan"}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["tenant_id"] == default_tenant.id

    def test_retrieve_tenant_user_not_found(self, apigw_api_client, default_tenant_user_data):
        resp = apigw_api_client.get(
            reverse("apigw.tenant_user.retrieve", kwargs={"tenant_user_id": "zhangsan_not_found"})
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

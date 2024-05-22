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
from bkuser.apps.tenant.models import TenantUser
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture()
def tenant_user(bk_user) -> TenantUser:
    return TenantUser.objects.get(tenant_id=bk_user.get_property("tenant_id"), id=bk_user.username)


class TestTenantUserExtrasUpdateApi:
    def test_update(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"gender": "male", "sport_hobby": ["basketball"]}},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_update_without_all_editable_fields(self, api_client, tenant_user, tenant_user_custom_fields):
        """只指定部分可编辑的字段进行更新是被允许的"""
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"gender": "male"}},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_update_not_editable_field(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"age": 18}},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "当前用户无可编辑的租户自定义字段" in resp.data["message"]

    def test_update_with_invalid_value_case_1(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"gender": "make", "sport_hobby": ["basketball"]}},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "字段 性别 的值 make 不是可选项之一" in resp.data["message"]

    def test_update_with_invalid_value_case_2(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"gender": "female", "sport_hobby": []}},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "多选枚举类型自定义字段值必须是非空列表" in resp.data["message"]

    def test_update_with_invalid_value_case_3(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"gender": "female", "sport_hobby": ["flying"]}},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "字段 运动爱好 的值 ['flying'] 不是可选项的子集" in resp.data["message"]


class TestTenantUserFieldListApi:
    def test_list(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.get(reverse("personal_center.tenant_users.fields.list", kwargs={"id": tenant_user.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["builtin_fields"]) == 5  # noqa: PLR2004
        assert [f["name"] for f in resp.data["custom_fields"]] == ["age", "gender", "sport_hobby"]
        assert [f["name"] for f in resp.data["custom_fields"] if f["editable"]] == ["gender", "sport_hobby"]


class TestTenantUserFeatureFlagListApi:
    def test_list(self, api_client, tenant_user):
        resp = api_client.get(reverse("personal_center.tenant_users.feature_flag.list", kwargs={"id": tenant_user.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["can_change_password"] is False

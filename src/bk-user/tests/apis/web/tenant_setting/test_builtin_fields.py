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
from bkuser.apps.tenant.models import TenantUser, TenantUserBuiltinField
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantUserBuiltinFieldUpdateApi:
    def test_update_builtin_field_success(self, api_client, random_tenant):
        """测试成功更新字段配置"""
        phone_field = TenantUserBuiltinField.objects.get(tenant=random_tenant, name="email")

        data = {
            "required": True,
            "unique": True,
            "personal_center_visible": False,
            "personal_center_editable": False,
            "manager_editable": False,
        }

        resp = api_client.put(reverse("tenant_builtin_fields.update", kwargs={"id": phone_field.id}), data=data)

        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # 验证字段配置已更新
        phone_field.refresh_from_db()
        assert phone_field.required
        assert phone_field.unique
        assert not phone_field.personal_center_visible
        assert not phone_field.personal_center_editable
        assert not phone_field.manager_editable

    def test_with_missing_values(
        self,
        api_client,
        random_tenant,
    ):
        """测试字段设置必填时有用户缺少该字段值的情况"""

        phone_field = TenantUserBuiltinField.objects.get(tenant=random_tenant, name="phone")

        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        ds_zhangsan = zhangsan.data_source_user
        ds_zhangsan.phone = ""
        ds_zhangsan.save()

        data = {
            "required": True,
            "unique": True,
            "personal_center_visible": False,
            "personal_center_editable": False,
            "manager_editable": False,
        }

        resp = api_client.put(reverse("tenant_builtin_fields.update", kwargs={"id": phone_field.id}), data=data)

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "无法将字段 'phone' 设为必填：zhangsan 未填写该字段的值。请先完善这些用户的字段数据。"
            in resp.data["message"]
        )

    def test_with_duplicate_values(self, api_client, random_tenant):
        """测试字段设置唯一时有重复值的情况"""
        email_field = TenantUserBuiltinField.objects.get(tenant=random_tenant, name="email")

        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        ds_zhangsan = zhangsan.data_source_user
        ds_zhangsan.email = "duplicate@test.com"
        ds_zhangsan.save()

        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        ds_lisi = lisi.data_source_user
        ds_lisi.email = "duplicate@test.com"
        ds_lisi.save()

        data = {
            "required": True,
            "unique": True,
            "personal_center_visible": False,
            "personal_center_editable": False,
            "manager_editable": False,
        }

        resp = api_client.put(reverse("tenant_builtin_fields.update", kwargs={"id": email_field.id}), data=data)

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "无法将字段 'email' 设为唯一：zhangsan, lisi 存在重复的字段值。请先修正这些重复数据。"
            in resp.data["message"]
        )

    def test_update_email_not_required(self, api_client, random_tenant):
        """测试更新邮箱字段为非必填"""
        email_field = TenantUserBuiltinField.objects.get(tenant=random_tenant, name="email")

        data = {
            "required": False,
            "unique": True,
            "personal_center_visible": False,
            "personal_center_editable": False,
            "manager_editable": False,
        }

        resp = api_client.put(reverse("tenant_builtin_fields.update", kwargs={"id": email_field.id}), data=data)

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "无法将字段 'email' 设为非必填：另一个字段 'phone' 已为非必填。" in resp.data["message"]

    def test_update_username_builtin_field(self, api_client, random_tenant):
        """测试更新用户名字段"""
        username_field = TenantUserBuiltinField.objects.get(tenant=random_tenant, name="username")

        data = {
            "required": True,
            "unique": True,
            "personal_center_visible": False,
            "personal_center_editable": False,
            "manager_editable": False,
        }

        resp = api_client.put(reverse("tenant_builtin_fields.update", kwargs={"id": username_field.id}), data=data)

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

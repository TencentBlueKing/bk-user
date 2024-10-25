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
from bkuser.apps.tenant.models import TenantUser
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestProfileUpdate:
    @pytest.mark.parametrize(
        ("username", "language"),
        [
            ("lisi", "en"),
            ("lisi", "zh-cn"),
            ("zhangsan", "zh-cn"),
            ("zhangsan", "en"),
        ],
    )
    def test_standard(self, open_v1_api_client, local_data_source, username, language):
        resp = open_v1_api_client.post(
            reverse("open_v1.update_profile"), data={"username": username, "language": language}
        )

        assert resp.status_code == status.HTTP_200_OK

        tenant_user = TenantUser.objects.get(id=username)
        assert tenant_user.language == language
        assert tenant_user.time_zone == "Asia/Shanghai"
        assert tenant_user.wx_userid == ""

    def test_wx_userid_with_empty_string(self, open_v1_api_client, local_data_source):
        TenantUser.objects.filter(id="lisi").update(wx_userid="has_value")

        resp = open_v1_api_client.post(reverse("open_v1.update_profile"), data={"username": "lisi", "wx_userid": ""})

        assert resp.status_code == status.HTTP_200_OK
        tenant_user = TenantUser.objects.get(id="lisi")
        assert tenant_user.wx_userid == ""

    def test_invalid_user(self, open_v1_api_client, local_data_source):
        resp = open_v1_api_client.post(
            reverse("open_v1.update_profile"), data={"username": "zhansan_not_found", "language": "en"}
        )

        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestProfileBatchQuery:
    def test_standard(self, open_v1_api_client, local_data_source):
        resp = open_v1_api_client.post(reverse("open_v1.query_profile"), data={"username_list": ["lisi", "zhangsan"]})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2

        excepted_keys = {
            "username",
            "chname",
            "display_name",
            "email",
            "phone",
            "iso_code",
            "time_zone",
            "language",
            "wx_userid",
            "qq",
            "role",
        }
        assert set(resp.data[0].keys()) == excepted_keys

    def test_invalid_user(self, open_v1_api_client, local_data_source):
        resp = open_v1_api_client.post(
            reverse("open_v1.query_profile"), data={"username_list": ["lisi_not_found", "zhangsan_not_found"]}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from django.test.utils import override_settings
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestLanguageListApi:
    def test_list_builtin_languages(self, api_client):
        """默认仅返回内置语言，英文码为 en"""
        with override_settings(EXTRA_LANGUAGES=()):
            resp = api_client.get(reverse("basic.languages.list"))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data == [
            {"code": "zh-cn", "name": "中文"},
            {"code": "en", "name": "英文"},
        ]

    def test_list_with_extra_languages(self, api_client):
        """配置额外语言后，语言列表包含额外语言"""
        with override_settings(EXTRA_LANGUAGES=(("ja", "日本語"),)):
            resp = api_client.get(reverse("basic.languages.list"))

        assert resp.status_code == status.HTTP_200_OK
        codes = [item["code"] for item in resp.data]
        assert codes == ["zh-cn", "en", "ja"]

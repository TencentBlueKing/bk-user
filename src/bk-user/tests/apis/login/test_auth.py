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
from bkuser.apps.idp.models import Idp, IdpPlugin
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from django.urls import reverse

from tests.test_utils.helpers import generate_random_string

pytestmark = pytest.mark.django_db


class TestGlobalInfoRetrieveApi:
    def test_retrieve_with_only_tenant(self, api_client, default_tenant):
        resp = api_client.get(reverse("login.global_info.retrieve"))
        assert resp.data["tenant_visible"]
        assert resp.data["enabled_auth_tenant_number"] == 1
        assert resp.data["only_enabled_auth_tenant"] is not None
        assert resp.data["only_enabled_auth_tenant"]["id"] == default_tenant.id
        assert len(resp.data["only_enabled_auth_tenant"]["enabled_idps"]) == 1
        assert resp.data["only_enabled_auth_tenant"]["enabled_idps"][0]["plugin_id"] == BuiltinIdpPluginEnum.LOCAL

    def test_retrieve_with_mult_tenant_but_not_mult_idp(self, api_client, default_tenant, random_tenant):
        self.test_retrieve_with_only_tenant(api_client, default_tenant)

    def test_retrieve_with_mult_tenant_and_mult_idp(self, api_client, default_tenant, random_tenant):
        Idp.objects.create(
            name=generate_random_string(),
            owner_tenant_id=random_tenant.id,
            plugin=IdpPlugin.objects.get(id=BuiltinIdpPluginEnum.LOCAL),
            data_source_id=0,
        )
        resp = api_client.get(reverse("login.global_info.retrieve"))

        assert resp.data["tenant_visible"]
        assert resp.data["enabled_auth_tenant_number"] > 1
        assert resp.data["only_enabled_auth_tenant"] is None

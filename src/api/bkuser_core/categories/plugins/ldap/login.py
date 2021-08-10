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
from bkuser_core.categories.plugins.ldap.client import LDAPClient
from bkuser_core.categories.plugins.ldap.syncer import ProfileFieldMapper
from bkuser_core.user_settings.loader import ConfigProvider
from django.utils.encoding import force_str

from .exceptions import FetchUserMetaInfoFailed
from .syncer import SETTING_FIELD_MAP


class LoginHandler:
    @staticmethod
    def fetch_username(field_fetcher, user_info: dict) -> str:
        return force_str(field_fetcher.get_field(user_meta=user_info["raw_attributes"], field_name="username"))

    @staticmethod
    def fetch_dn(user_info: dict) -> str:
        return force_str(user_info["raw_attributes"]["entryDN"][0])

    def check(self, profile, password):
        category_id = profile.category_id
        config_loader = ConfigProvider(category_id=category_id)
        client = LDAPClient(config_loader)
        field_fetcher = ProfileFieldMapper(config_loader, SETTING_FIELD_MAP)

        users = client.search(
            object_class=config_loader["user_class"],
            attributes=field_fetcher.get_user_attributes(),
        )
        target_dn = None
        for user in users:
            if not user.get("raw_attributes"):
                continue

            if self.fetch_username(field_fetcher, user) == profile.username:
                target_dn = self.fetch_dn(user)

        if not target_dn:
            raise FetchUserMetaInfoFailed("获取用户基本信息失败")

        # 检验
        client.check(username=target_dn, password=password)

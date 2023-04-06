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
import logging

from django.utils.encoding import force_str

from bkuser_core.categories.plugins.ldap.adaptor import ProfileFieldMapper
from bkuser_core.categories.plugins.ldap.client import LDAPClient
from bkuser_core.categories.plugins.ldap.exceptions import FetchUserMetaInfoFailed
from bkuser_core.user_settings.loader import ConfigProvider

logger = logging.getLogger(__name__)


class LoginHandler:
    @staticmethod
    def fetch_username(field_fetcher, user_info: dict) -> str:
        return force_str(field_fetcher.get_value(field_name="username", user_meta=user_info["raw_attributes"]))

    @staticmethod
    def fetch_dn(user_info: dict) -> str:
        return force_str(user_info["raw_attributes"]["entryDN"][0])

    def check(self, profile, password):
        category_id = profile.category_id
        config_loader = ConfigProvider(category_id=category_id)
        client = LDAPClient(config_loader)
        field_fetcher = ProfileFieldMapper(config_loader)

        user_class = config_loader["user_class"]
        username_field = config_loader["username"]
        logger.debug(
            "going to search users, filter_condition( object_class = %s, username_field = %s, attributes: %s )",
            user_class,
            username_field,
            field_fetcher.get_user_attributes(),
        )
        force_filter_str = f"(&(objectClass={user_class})({username_field}={profile.username}))"

        users = client.search(
            force_filter_str=force_filter_str,
            attributes=field_fetcher.get_user_attributes(),
        )
        logger.debug("search results users: %s", users)

        # NOTE: 1. 如果用户反馈登录一直不成功, 怎么排查? 2.target_dn可能被后面命中的覆盖?
        target_dn = None
        for user in users:
            if not user.get("raw_attributes"):
                logger.debug("user %s has no raw_attributes, skip", user)
                continue

            if self.fetch_username(field_fetcher, user) == profile.username:
                target_dn = self.fetch_dn(user)

        if not target_dn:
            raise FetchUserMetaInfoFailed("获取用户基本信息失败")

        # 检验
        logger.debug("going to check user, dn: %s", target_dn)
        client.check(username=target_dn, password=password)

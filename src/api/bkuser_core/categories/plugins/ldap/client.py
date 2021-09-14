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
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List

import ldap3
from bkuser_core.categories.loader import get_plugin_by_name
from django.conf import settings
from ldap3 import ALL, SIMPLE, Connection, Server

from . import exceptions as local_exceptions

if TYPE_CHECKING:
    from bkuser_core.user_settings.loader import ConfigProvider


logger = logging.getLogger(__name__)


@dataclass
class LDAPClient:
    config_provider: "ConfigProvider"

    def __post_init__(self):
        self.con = self.initialize(
            connection_url=self.config_provider.get("connection_url"),
            user=self.config_provider.get("user"),
            password=self.config_provider.get("password"),
            timeout_setting=self.config_provider.get("timeout_setting", 120),
            use_ssl=bool(self.config_provider.get("ssl_encryption") == "SSL"),
        )

        self.start_root = self.config_provider.get("basic_pull_node")

    @classmethod
    def initialize(
        cls,
        connection_url: str,
        user: str = None,
        password: str = None,
        timeout_setting: int = 120,
        use_ssl: bool = False,
    ) -> Connection:
        """初始化 ldap 服务器，包括连接"""
        server_params = {}
        try:
            if use_ssl:
                server_params.update({"use_ssl": True})

            connection_params = {
                "server": Server(connection_url, **server_params),
                "auto_bind": True,
                "receive_timeout": timeout_setting,
            }

            if hasattr(settings, "LDAP_CONNECTION_EXTRAS_PARAMS"):
                connection_params.update(settings.LDAP_CONNECTION_EXTRAS_PARAMS)

            # 目前只支持简单鉴权
            if user and password:
                connection_params.update({"user": user, "password": password, "authentication": SIMPLE})

            return Connection(**connection_params)

        except KeyError:
            raise local_exceptions.LDAPSettingNotReady
        except ldap3.core.exceptions.LDAPSocketReceiveError:
            raise local_exceptions.LdapCannotBeInitialized
        except Exception:
            logger.exception("failed to initialize ldap server")
            raise local_exceptions.LdapCannotBeInitialized

    def search(
        self,
        object_class: str = "",
        force_filter_str: str = "",
        start_root: str = None,
        attributes: list = None,
    ) -> List[Dict]:
        """搜索"""
        if not start_root:
            start_root = self.start_root

        search_filter = force_filter_str or f"(objectClass={object_class})"
        logger.info("going to search %s from %s", search_filter, start_root)
        result = self.con.extend.standard.paged_search(
            search_base=start_root,
            search_filter=search_filter,
            get_operational_attributes=True,
            attributes=attributes or [],
            paged_size=get_plugin_by_name("ldap").extra_config["ldap_max_paged_size"],
            generator=False,
        )

        if not result and not self.con.result["result"] == 0 and not self.con.last_error:
            raise local_exceptions.SearchFailed

        return self.con.response

    def check(self, username, password):
        params = {
            "host": self.config_provider["connection_url"],
            "get_info": ALL,
            "use_ssl": bool(self.config_provider["ssl_encryption"] == "SSL"),
        }
        server = Server(**params)
        conn = Connection(server, username, password, auto_bind=True)
        conn.extend.standard.who_am_i()

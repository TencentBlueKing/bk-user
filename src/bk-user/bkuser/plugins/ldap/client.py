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

from typing import List

from ldap3 import ALL_ATTRIBUTES, DEREF_NEVER, SAFE_SYNC, Connection, Server
from ldap3.extend.standard.PagedSearch import paged_search_accumulator

from bkuser.plugins.ldap.constants import REQUIRED_OPERATIONAL_ATTRIBUTES
from bkuser.plugins.ldap.exceptions import DataNotFoundError
from bkuser.plugins.ldap.models import LDAPObject, ServerConfig


class LDAPClient:
    """LDAP 客户端"""

    def __init__(self, server_config: ServerConfig):
        self.server_config = server_config

    def __enter__(self):
        self._conn = self._gen_conn(self.server_config)
        self._conn.bind()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._conn.unbind()

    def fetch_all_objects(self, search_filter: str, object_class: str) -> List[LDAPObject]:
        return self._fetch_objects_with_page(search_filter, object_class, self.server_config.page_size)

    def fetch_first_object(self, search_filter: str, object_class: str) -> LDAPObject:
        results = self._fetch_objects_with_page(search_filter, object_class, 1)
        if not results:
            raise DataNotFoundError(f"no object found in {search_filter} (objectclass={object_class})")

        return results[0]

    def _fetch_objects_with_page(self, search_filter: str, object_class: str, page_size: int) -> List[LDAPObject]:
        """
        以分页方式获取对象列表

        :param search_filter: LDAP 查询过滤器，如：ou=company,dc=bk,dc=example,dc=com
        :param object_class: LDAP 对象类，如：inetOrgPerson
        :param page_size: 分页大小
        :return: 对象列表
        """
        if page_size <= 0:
            raise ValueError("page_size must be greater than 0")

        results = paged_search_accumulator(
            self._conn,
            search_base=search_filter,
            search_filter=f"(objectclass={object_class})",
            dereference_aliases=DEREF_NEVER,
            get_operational_attributes=False,
            attributes=[
                ALL_ATTRIBUTES,
                *REQUIRED_OPERATIONAL_ATTRIBUTES,
            ],
            paged_size=page_size,
        )
        # 丢弃多余的信息，如 type，raw_dn，raw_attributes 等
        return [LDAPObject(dn=r["dn"], attrs=r["attributes"]) for r in results]

    @staticmethod
    def _gen_conn(server_config: ServerConfig) -> Connection:
        server = Server(
            server_config.server_url,
            connect_timeout=server_config.request_timeout,
        )
        return Connection(
            server=server,
            user=server_config.bind_dn,
            password=server_config.bind_password,
            client_strategy=SAFE_SYNC,
            read_only=True,
            raise_exceptions=True,
            receive_timeout=server_config.request_timeout,
        )

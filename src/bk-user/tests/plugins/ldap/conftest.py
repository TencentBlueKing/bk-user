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

from typing import Dict, List
from unittest import mock

import pytest
from bkuser.plugins.ldap.models import LDAPDataSourcePluginConfig

# 部门数据
organizational_unit_data = [
    {
        "dn": "ou=group_baa,ou=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "ou": ["group_baa"],
            "objectClass": ["organizationalUnit", "top"],
            "entryUUID": "97aaa370-0e9d-103f-8e7f-fb1e46baa127",
        },
    },
    {
        "dn": "ou=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "ou": ["center_ba"],
            "objectClass": ["organizationalUnit", "top"],
            "entryUUID": "97a9aa88-0e9d-103f-8e7e-fb1e46baa127",
        },
    },
    {
        "dn": "ou=group_aba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "ou": ["group_aba"],
            "objectClass": ["organizationalUnit", "top"],
            "entryUUID": "97a93076-0e9d-103f-8e7d-fb1e46baa127",
        },
    },
    {
        "dn": "ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "ou": ["center_ab"],
            "objectClass": ["organizationalUnit", "top"],
            "entryUUID": "97a8b06a-0e9d-103f-8e7c-fb1e46baa127",
        },
    },
    {
        "dn": "ou=group_aaa,ou=center_aa,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "ou": ["group_aaa"],
            "objectClass": ["organizationalUnit", "top"],
            "entryUUID": "97a843e6-0e9d-103f-8e7b-fb1e46baa127",
        },
    },
    {
        "dn": "ou=center_aa,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "ou": ["center_aa"],
            "objectClass": ["organizationalUnit", "top"],
            "entryUUID": "97a7a882-0e9d-103f-8e7a-fb1e46baa127",
        },
    },
    {
        "dn": "ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "ou": ["dept_b"],
            "objectClass": ["organizationalUnit", "top"],
            "entryUUID": "97a73a14-0e9d-103f-8e79-fb1e46baa127",
        },
    },
    {
        "dn": "ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "ou": ["dept_a"],
            "objectClass": ["organizationalUnit", "top"],
            "entryUUID": "97a63966-0e9d-103f-8e78-fb1e46baa127",
        },
    },
    {
        "dn": "ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "ou": ["company"],
            "objectClass": ["organizationalUnit", "top"],
            "entryUUID": "97a49458-0e9d-103f-8e77-fb1e46baa127",
        },
    },
]


# 用户组数据
group_of_names_data = [
    {
        "dn": "cn=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "objectClass": ["top", "groupOfNames"],
            "cn": ["center_ba"],
            "member": ["cn=lushi,ou=group_aba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com"],
            "entryUUID": "97b93908-0e9d-103f-8e8b-fb1e46baa127",
        },
    },
    {
        "dn": "cn=dept_b,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "objectClass": ["top", "groupOfNames"],
            "cn": ["dept_b"],
            "member": ["cn=wangwu,ou=dept_a,ou=company,dc=bk,dc=example,dc=com"],
            "entryUUID": "97b8b6ea-0e9d-103f-8e8a-fb1e46baa127",
        },
    },
    {
        "dn": "cn=center_aa,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "objectClass": ["top", "groupOfNames"],
            "cn": ["center_aa"],
            "member": ["cn=lisi,ou=dept_a,ou=company,dc=bk,dc=example,dc=com"],
            "entryUUID": "97b2869e-0e9d-103f-8e83-fb1e46baa127",
        },
    },
]


# 用户数据
inet_org_person_data = [
    {
        "dn": "cn=baishier,ou=group_baa,ou=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "givenName": ["shier"],
            "sn": ["bai"],
            "cn": ["baishier"],
            "uid": ["baishier"],
            "manager": ["cn=lushi,ou=group_aba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com"],
            "objectClass": ["inetOrgPerson", "top"],
            "entryUUID": "97b9bdce-0e9d-103f-8e8c-fb1e46baa127",
        },
    },
    {
        "dn": "cn=linshiyi,ou=group_aba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "givenName": ["shiyi"],
            "sn": ["lin"],
            "cn": ["linshiyi"],
            "uid": ["linshiyi"],
            "manager": ["cn=lushi,ou=group_aba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com"],
            "objectClass": ["inetOrgPerson", "top"],
            "entryUUID": "97b75822-0e9d-103f-8e89-fb1e46baa127",
        },
    },
    {
        "dn": "cn=lushi,ou=group_aba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "givenName": ["shi"],
            "sn": ["lu"],
            "cn": ["lushi"],
            "uid": ["lushi"],
            "manager": [
                "cn=maiba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
                "cn=wangwu,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
            ],
            "objectClass": ["inetOrgPerson", "top"],
            "entryUUID": "97b65b84-0e9d-103f-8e88-fb1e46baa127",
        },
    },
    {
        "dn": "cn=yangjiu,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "givenName": ["jiu"],
            "sn": ["yang"],
            "cn": ["yangjiu"],
            "uid": ["yangjiu"],
            "manager": ["cn=wangwu,ou=dept_a,ou=company,dc=bk,dc=example,dc=com"],
            "objectClass": ["inetOrgPerson", "top"],
            "entryUUID": "97b5d394-0e9d-103f-8e87-fb1e46baa127",
        },
    },
    {
        "dn": "cn=maiba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "givenName": ["ba"],
            "sn": ["mai"],
            "cn": ["maiba"],
            "uid": ["maiba"],
            "manager": [
                "cn=wangwu,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
                "cn=lisi,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
            ],
            "objectClass": ["inetOrgPerson", "top"],
            "entryUUID": "97b534de-0e9d-103f-8e86-fb1e46baa127",
        },
    },
    {
        "dn": "cn=zhaoliu,ou=center_aa,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "givenName": ["liu"],
            "sn": ["zhao"],
            "cn": ["zhaoliu"],
            "uid": ["zhaoliu"],
            "manager": ["cn=lisi,ou=dept_a,ou=company,dc=bk,dc=example,dc=com"],
            "objectClass": ["inetOrgPerson", "top"],
            "entryUUID": "97b48c00-0e9d-103f-8e85-fb1e46baa127",
        },
    },
    {
        "dn": "cn=wangwu,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "givenName": ["wu"],
            "sn": ["wang"],
            "cn": ["wangwu"],
            "uid": ["wangwu"],
            "manager": ["cn=zhangsan,ou=company,dc=bk,dc=example,dc=com"],
            "objectClass": ["inetOrgPerson", "top"],
            "entryUUID": "97b33a9e-0e9d-103f-8e84-fb1e46baa127",
        },
    },
    {
        "dn": "cn=lisi,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "givenName": ["si"],
            "sn": ["li"],
            "cn": ["lisi"],
            "uid": ["lisi"],
            "manager": ["cn=zhangsan,ou=company,dc=bk,dc=example,dc=com"],
            "objectClass": ["inetOrgPerson", "top"],
            "entryUUID": "97b11232-0e9d-103f-8e82-fb1e46baa127",
        },
    },
    {
        "dn": "cn=zhangsan,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "givenName": ["san"],
            "sn": ["zhang"],
            "cn": ["zhangsan"],
            "uid": ["zhangsan"],
            "objectClass": ["inetOrgPerson", "top"],
            "entryUUID": "97ae75c2-0e9d-103f-8e81-fb1e46baa127",
        },
    },
    {
        "dn": "cn=liuqi,ou=group_aaa,ou=center_aa,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        "attributes": {
            "givenName": ["qi"],
            "sn": ["liu"],
            "cn": ["liuqi"],
            "uid": ["liuqi"],
            "manager": ["cn=zhaoliu,ou=center_aa,ou=dept_a,ou=company,dc=bk,dc=example,dc=com"],
            "objectClass": ["inetOrgPerson", "top"],
            "entryUUID": "97abbfe4-0e9d-103f-8e80-fb1e46baa127",
        },
    },
]


def _mocked_paged_search_accumulator(*args, **kwargs) -> List[Dict]:
    """测试用函数，用于屏蔽 LDAP 服务"""

    search_base = kwargs["search_base"]
    search_filter = kwargs["search_filter"]

    if "inetOrgPerson" in search_filter:
        return [p for p in inet_org_person_data if p["dn"].endswith(search_base)]  # type: ignore

    if "organizationalUnit" in search_filter:
        return [ou for ou in organizational_unit_data if ou["dn"].endswith(search_base)]  # type: ignore

    if "groupOfNames" in search_filter:
        return [g for g in group_of_names_data if g["dn"].endswith(search_base)]  # type: ignore

    return []


class MockedLDAPConnection:
    def __init__(self, *args, **kwargs):
        pass

    def bind(self, *args, **kwargs):
        pass

    def unbind(self, *args, **kwargs):
        pass


@pytest.fixture
def _mock_ldap_client():
    with mock.patch(
        "bkuser.plugins.ldap.client.paged_search_accumulator",
        new=_mocked_paged_search_accumulator,
    ), mock.patch(
        "bkuser.plugins.ldap.client.LDAPClient._gen_conn",
        return_value=MockedLDAPConnection(),
    ):
        yield


@pytest.fixture
def ldap_ds_cfg(ldap_ds_plugin_cfg) -> LDAPDataSourcePluginConfig:
    return LDAPDataSourcePluginConfig(**ldap_ds_plugin_cfg)

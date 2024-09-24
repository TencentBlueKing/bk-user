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

from typing import List, NamedTuple

import ldap3.utils.dn as dn_utils


class RDN(NamedTuple):
    """RelativeDistinguishedName"""

    attr_type: str
    attr_value: str
    separator: str


def parse_dn(dn: str, restrict_types: List[str] | None = None) -> List[RDN]:
    """A DN is a sequence of relative distinguished names (RDN) connected by commas, For examples:

    we have a dn = "cn=zhangsan,ou=company,dc=example,dc=com", this method will parse the dn to:
    >>> parse_dn("cn=zhangsan,ou=company,dc=example,dc=com")
    [RDN(type='cn', value='zhangsan', separator=','),
     RDN(type='ou', value='company', separator=','),
     RDN(type='dc', value='example', separator=','),
     RDN(type='dc', value='com', separator='')]

    if provide restrict_types, this method will ignore the attribute not in restrict_types, For examples:
    >>> parse_dn("cn=zhangsan,ou=company,dc=example,dc=com", restrict_types=["dc"])
    [RDN(type='dc', value='example', separator=','), RDN(type='dc', value='com', separator='')]

    Furthermore, restrict_types is Case-insensitive, the ["DC"], ["dc"], ["Dc"] are Exactly equal.
    >>> parse_dn("cn=zhangsan,ou=company,dc=example,dc=com", restrict_types=["DC"])
    [RDN(type='dc', value='example', separator=','), RDN(type='dc', value='com', separator='')]

    See Also: https://docs.microsoft.com/en-us/previous-versions/windows/desktop/ldap/distinguished-names
    """
    restrict_types = [t.lower() for t in (restrict_types or [])]
    items = dn_utils.parse_dn(dn, escape=True)

    if restrict_types:
        return [RDN(*i) for i in items if i[0].lower() in restrict_types]

    return [RDN(*i) for i in items]


def gen_dn(rdns: List[RDN]) -> str:
    """根据 RDN 列表生成 DN"""
    if not rdns:
        return ""

    separator = rdns[0].separator
    return separator.join([f"{rdn.attr_type}={rdn.attr_value}" for rdn in rdns])

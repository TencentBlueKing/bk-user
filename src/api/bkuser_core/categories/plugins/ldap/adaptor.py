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
from dataclasses import dataclass
from typing import Any, Dict, List, NamedTuple, Optional

from bkuser_core.categories.plugins.ldap.models import LdapDepartment, LdapUserProfile
from bkuser_core.user_settings.loader import ConfigProvider
from django.utils.encoding import force_str
from ldap3.utils import dn as dn_utils


@dataclass
class ProfileFieldMapper:
    """从 ldap 对象属性中获取用户字段"""

    config_loader: ConfigProvider
    setting_field_map: dict

    def get_field(self, user_meta: Dict[str, List[bytes]], field_name: str, raise_exception: bool = False) -> str:
        """根据字段映射关系, 从 ldap 中获取 `field_name` 的值"""
        try:
            setting_name = self.setting_field_map[field_name]
        except KeyError:
            if raise_exception:
                raise ValueError("该用户字段没有在配置中有对应项，无法同步")
            return ""

        try:
            ldap_field_name = self.config_loader[setting_name]
        except KeyError:
            if raise_exception:
                raise ValueError(f"用户目录配置中缺失字段 {setting_name}")
            return ""

        try:
            if user_meta[ldap_field_name]:
                return force_str(user_meta[ldap_field_name][0])

            return ""
        except KeyError:
            if raise_exception:
                raise ValueError(f"搜索数据中没有对应的字段 {ldap_field_name}")
            return ""

    def get_user_attributes(self) -> list:
        """获取远端属性名列表"""
        return [self.config_loader[x] for x in self.setting_field_map.values() if self.config_loader[x]]


def user_adapter(
    code: str, user_meta: Dict[str, Any], field_mapper: ProfileFieldMapper, restrict_types: List[str]
) -> LdapUserProfile:
    groups = user_meta["attributes"][field_mapper.config_loader["user_member_of"]]

    return LdapUserProfile(
        username=field_mapper.get_field(user_meta=user_meta["raw_attributes"], field_name="username"),
        email=field_mapper.get_field(user_meta=user_meta["raw_attributes"], field_name="email"),
        telephone=field_mapper.get_field(user_meta=user_meta["raw_attributes"], field_name="telephone"),
        display_name=field_mapper.get_field(user_meta=user_meta["raw_attributes"], field_name="display_name"),
        code=code,
        # TODO: 完成转换 departments 的逻辑
        departments=[
            # 根据约定, dn 中除去第一个成分以外的部分即为用户所在的部门, 因此需要取 [1:]
            list(reversed(parse_dn_value_list(user_meta["dn"], restrict_types)[1:])),
            # 用户与用户组之间的关系
            *[list(reversed(parse_dn_value_list(group, restrict_types))) for group in groups],
        ],
    )


def department_adapter(code: str, dept_meta: Dict, is_group: bool, restrict_types: List[str]) -> LdapDepartment:
    dn = dept_meta["dn"]
    dn_values = parse_dn_value_list(dn, restrict_types=restrict_types)

    parent_dept: Optional[LdapDepartment] = None
    for dept_name in reversed(dn_values):
        parent_dept = LdapDepartment(
            name=dept_name,
            parent=parent_dept,
            is_group=is_group,
        )

    assert parent_dept is not None, "未从 dn 中提取到任何部门信息"
    parent_dept.code = code
    return parent_dept


class RDN(NamedTuple):
    """RelativeDistinguishedName"""

    type: str
    value: str
    separator: str


def parse_dn_tree(dn: str, restrict_types: List[str] = None) -> List[RDN]:
    """A DN is a sequence of relative distinguished names (RDN) connected by commas, For examples:

    we have a dn = "CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM", this method will parse the dn to:
    >>> parse_dn_tree("CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM")
    [RDN(type='CN', value='Jeff Smith', separator=','),
     RDN(type='OU', value='Sales', separator=','),
     RDN(type='DC', value='Fabrikam', separator=','),
     RDN(type='DC', value='COM', separator='')]

    if provide restrict_types, this method will ignore the attribute not in restrict_types, For examples:
    >>> parse_dn_tree("CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM", restrict_types=["DC"])
    [RDN(type='DC', value='Fabrikam', separator=','), RDN(type='DC', value='COM', separator='')]

    Furthermore, restrict_types is Case-insensitive, the ["DC"], ["dc"], ["Dc"] are Exactly equal.
    >>> parse_dn_tree("CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM", restrict_types=["dc"])
    [RDN(type='DC', value='Fabrikam', separator=','), RDN(type='DC', value='COM', separator='')]

    See Also: https://docs.microsoft.com/en-us/previous-versions/windows/desktop/ldap/distinguished-names
    """
    restrict_types = [type_.upper() for type_ in (restrict_types or [])]
    items = dn_utils.parse_dn(dn, escape=True)

    if restrict_types:
        parts = [RDN(*i) for i in items if i[0].upper() in restrict_types]
    else:
        parts = [RDN(*i) for i in items]

    return parts


def parse_dn_value_list(dn: str, restrict_types: List[str] = None) -> List[str]:
    """this method work like parse_dn_tree, be only return values of those attributes, For examples:

    >>> parse_dn_value_list("CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM")
    ['Jeff Smith', 'Sales', 'Fabrikam', 'COM']

    if provide restrict_types, this method will ignore the attribute not in restrict_types, For examples:
    >>> parse_dn_value_list("CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM", restrict_types=["DC"])
    ['Fabrikam', 'COM']

    """
    tree = parse_dn_tree(dn, restrict_types)
    parts = []
    for part in tree:
        parts.append(part.value)
    return parts

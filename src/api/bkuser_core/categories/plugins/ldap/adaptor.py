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
from dataclasses import dataclass, field
from typing import Any, Dict, List, NamedTuple, Optional

from django.utils.encoding import force_str
from ldap3.utils import dn as dn_utils

from bkuser_core.categories.plugins.constants import DYNAMIC_FIELDS_SETTING_KEY
from bkuser_core.categories.plugins.ldap.models import LdapDepartment, LdapUserProfile
from bkuser_core.user_settings.loader import ConfigProvider

logger = logging.getLogger(__name__)


@dataclass
class ProfileFieldMapper:
    """从 ldap 对象属性中获取用户字段"""

    config_loader: ConfigProvider
    embed_fields = [
        "username",
        "display_name",
        "email",
        "telephone",
    ]
    dynamic_fields: List = field(default_factory=list)

    def __post_init__(self):
        self.dynamic_fields_mapping = self.config_loader.get(DYNAMIC_FIELDS_SETTING_KEY)

        self.dynamic_fields = list(self.dynamic_fields_mapping.keys()) if self.dynamic_fields_mapping else []

    def get_value(
        self, field_name: str, user_meta: Dict[str, List[bytes]], remain_raw: bool = False, dynamic_field: bool = False
    ) -> Any:
        """通过 field_name 从 ldap 数据中获取具体值"""

        # 获取自定义字段对应的属性值
        if dynamic_field:
            ldap_field_name = field_name
            if ldap_field_name not in self.dynamic_fields_mapping.values():
                logger.warning("no config[%s] in configs of dynamic_fields_mapping", field_name)
                return ""

        else:
            # 从目录配置中获取 字段名
            ldap_field_name = self.config_loader.get(field_name)
            if not ldap_field_name:
                logger.warning("no config[%s] in configs of category", field_name)
                return ""

        # 1. 通过字段名，获取具体值
        if ldap_field_name not in user_meta or not user_meta[ldap_field_name]:
            logger.warning("field[%s] is missing in raw attributes of user data from ldap", field_name)
            return ""

        # 2. 类似 memberOf 字段，将会返回原始列表
        if remain_raw:
            return user_meta[ldap_field_name]

        return force_str(user_meta[ldap_field_name][0])

    def get_values(self, user_meta: Dict[str, List[bytes]]) -> Dict[str, Any]:
        """根据字段映射关系, 从 ldap 中获取 `field_name` 的值"""

        values = {}
        for field_name in self.embed_fields:
            values.update({field_name: self.get_value(field_name, user_meta)})

        return values

    def get_dynamic_values(self, user_meta: Dict[str, List[bytes]]) -> Dict[str, Any]:
        """获取自定义字段 在ldap中的对应值"""
        values = {}

        if self.dynamic_fields:
            values.update(
                {
                    field_name: self.get_value(
                        field_name=self.dynamic_fields_mapping[field_name], user_meta=user_meta, dynamic_field=True
                    )
                    for field_name in self.dynamic_fields
                }
            )

        return values

    def get_user_attributes(self) -> list:
        """获取远端属性名列表"""
        user_attributes = [self.config_loader[x] for x in self.embed_fields if self.config_loader.get(x)]
        user_attributes.extend(
            [self.dynamic_fields_mapping[x] for x in self.dynamic_fields if self.dynamic_fields_mapping.get(x)]
        )

        return user_attributes


def user_adapter(
    code: str, user_meta: Dict[str, Any], field_mapper: ProfileFieldMapper, restrict_types: List[str]
) -> LdapUserProfile:
    groups = field_mapper.get_value("user_member_of", user_meta["raw_attributes"], True) or []

    return LdapUserProfile(
        **field_mapper.get_values(user_meta["raw_attributes"]),
        code=code,
        extras=field_mapper.get_dynamic_values(user_meta["raw_attributes"]),
        # TODO: 完成转换 departments 的逻辑
        departments=[
            # 根据约定, dn 中除去第一个成分以外的部分即为用户所在的部门, 因此需要取 [1:]
            list(reversed(parse_dn_value_list(user_meta["dn"], restrict_types)[1:])),
            # 用户与用户组之间的关系
            *[list(reversed(parse_dn_value_list(force_str(group), restrict_types))) for group in groups],
        ],
    )


def department_adapter(code: str, dept_meta: Dict, is_group: bool, restrict_types: List[str]) -> LdapDepartment:
    dn = dept_meta["dn"]
    dn_values = parse_dn_value_list(dn, restrict_types=restrict_types)

    parent_dept: Optional[LdapDepartment] = None
    for dept_name in reversed(dn_values):
        # 总公司 -> 部门1 -> 部门2
        # 都不带code, 没有拿dn+category生成唯一code
        parent_dept = LdapDepartment(
            name=dept_name,
            parent=parent_dept,
            is_group=is_group,
        )

    assert parent_dept is not None, "未从 dn 中提取到任何部门信息"
    # 部门2 的code
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

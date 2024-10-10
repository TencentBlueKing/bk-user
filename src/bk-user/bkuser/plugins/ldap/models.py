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

from typing import Any, Dict, Literal

from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, Field, model_validator

from bkuser.plugins.ldap.constants import (
    DEFAULT_REQ_TIMEOUT,
    LDAP_BASE_DN_REGEX,
    LDAP_BIND_DN_REGEX,
    MAX_REQ_TIMEOUT,
    MIN_REQ_TIMEOUT,
    SERVER_URL_REGEX,
    PageSizeEnum,
)
from bkuser.plugins.models import BasePluginConfig


class ServerConfig(BaseModel):
    """数据服务相关配置"""

    # LDAP 服务地址
    server_url: str = Field(pattern=SERVER_URL_REGEX)
    # Bind DN（用户名）
    bind_dn: str = Field(pattern=LDAP_BIND_DN_REGEX)
    # Bind 密码（访问密码）
    bind_password: str
    # Base DN 访问的根目录
    base_dn: str = Field(pattern=LDAP_BASE_DN_REGEX)
    # 单次分页请求数量
    page_size: PageSizeEnum = PageSizeEnum.SIZE_100
    # 单次请求超时时间
    request_timeout: int = Field(ge=MIN_REQ_TIMEOUT, le=MAX_REQ_TIMEOUT, default=DEFAULT_REQ_TIMEOUT)

    @model_validator(mode="after")
    def validate_attrs(self) -> "ServerConfig":
        if not self.bind_password:
            raise ValueError(_("LDAP 服务需要提供密码"))

        return self


class DataConfig(BaseModel):
    """数据相关配置"""

    # 用户对象类
    user_object_class: str
    # 用户过滤器
    user_search_filter: str
    # 部门对象类
    dept_object_class: str
    # 部门过滤器
    dept_search_filter: str

    @model_validator(mode="after")
    def validate_attrs(self) -> "DataConfig":
        # Q：为什么不是使用 Pydantic 的能力限制非空（比如 min_length=1）？
        # A：上面这种做法，只能使用 Pydantic 的错误提示，作为定制化的数据源之一，
        #   使用更具体的提示会更好，可以减少后续接受咨询 & 排查问题的成本 :)
        if not self.user_object_class:
            raise ValueError(_("需要提供用户对象类"))

        if not self.user_search_filter:
            raise ValueError(_("需要提供用户过滤器（DN）"))

        if not self.dept_object_class:
            raise ValueError(_("需要提供部门对象类"))

        if not self.dept_search_filter:
            raise ValueError(_("需要提供部门过滤器（DN）"))

        return self


class UserGroupConfig(BaseModel):
    """用户组配置"""

    # 是否支持用户组
    enabled: bool
    # 用户组对象类
    object_class: Literal["groupOfNames", "groupOfUniqueNames", ""] = ""
    # 用户组过滤器
    search_filter: str = ""
    # 用户组成员字段
    group_member_field: Literal["member", "uniqueMember", ""] = ""

    @model_validator(mode="after")
    def validate_attrs(self) -> "UserGroupConfig":
        if not self.enabled:
            return self

        if not self.object_class:
            raise ValueError(_("需要提供用户组对象类"))

        if not self.search_filter:
            raise ValueError(_("需要提供用户组过滤器（DN）"))

        if self.object_class == "groupOfNames" and self.group_member_field != "member":
            raise ValueError(_("用户组对象类为 groupOfNames 时，成员字段应为 member"))

        if self.object_class == "groupOfUniqueNames" and self.group_member_field != "uniqueMember":
            raise ValueError(_("用户组对象类为 groupOfUniqueNames 时，成员字段应为 uniqueMember"))

        return self


class LeaderConfig(BaseModel):
    """Leader 配置"""

    # 是否支持用户 Leader
    enabled: bool
    # Leader 字段名
    leader_field: str = ""

    @model_validator(mode="after")
    def validate_attrs(self) -> "LeaderConfig":
        if not self.enabled:
            return self

        if not self.leader_field:
            raise ValueError(_("需要提供 Leader 字段名"))

        return self


class LDAPDataSourcePluginConfig(BasePluginConfig):
    """LDAP 数据源插件配置"""

    sensitive_fields = [
        "server_config.bind_password",
    ]

    # 服务配置
    server_config: ServerConfig
    # 数据配置
    data_config: DataConfig
    # 用户组配置
    user_group_config: UserGroupConfig
    # Leader 配置
    leader_config: LeaderConfig

    @model_validator(mode="after")
    def validate_attrs(self) -> "LDAPDataSourcePluginConfig":
        """插件配置合法性检查"""
        if not self.data_config.user_search_filter.endswith(self.server_config.base_dn):
            raise ValueError(_("用户过滤器（DN）必须是 Base DN 的子节点"))

        if not self.data_config.dept_search_filter.endswith(self.server_config.base_dn):
            raise ValueError(_("部门过滤器（DN）必须是 Base DN 的子节点"))

        if self.user_group_config.enabled and not self.user_group_config.search_filter.endswith(
            self.server_config.base_dn
        ):
            raise ValueError(_("用户组过滤器（DN）必须是 Base DN 的子节点"))

        return self


class LDAPObject(BaseModel):
    """LDAP 对象"""

    dn: str
    attrs: Dict[str, Any]

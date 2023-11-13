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
from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _

# 非内置插件，必须以指定前缀开头
CUSTOM_PLUGIN_ID_PREFIX = "custom_"


class PluginTypeEnum(str, StructuredEnum):
    """认证源插件类型枚举"""

    CREDENTIAL = EnumField("credential", label=_("身份凭证认证"))
    FEDERATION = EnumField("federation", label=_("联邦认证"))


class BuiltinIdpPluginEnum(str, StructuredEnum):
    # 直接身份认证
    LOCAL = EnumField("local", label=_("本地账密"))
    LDAP = EnumField("ldap", label=_("LDAP"))
    MAD = EnumField("mad", label=_("Microsoft AD"))

    # 联邦身份认证
    # 标准协议
    OAUTH = EnumField("oauth2.0", label=_("OAuth 2.0"))
    OIDC = EnumField("oidc", label=_("OpenID Connect"))
    SAML = EnumField("saml2.0", label=_("SAML 2.0"))
    # 其他
    WECOM = EnumField("wecom", label=_("企业微信"))


BuiltinIdpPluginIDs = list(BuiltinIdpPluginEnum)  # type: ignore


class AllowedHttpMethodEnum(str, StructuredEnum):
    GET = EnumField("get")
    POST = EnumField("post")


class BuiltinActionEnum(str, StructuredEnum):
    AUTHENTICATE = EnumField("authenticate")
    LOGIN = EnumField("login")
    CALLBACK = EnumField("callback")

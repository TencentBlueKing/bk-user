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
from enum import Enum
import re


# 自定义插件，
CUSTOM_PLUGIN_ID_PREFIX = "custom_"


class PluginTypeEnum(str, Enum):
    CREDENTIAL = "credential"
    FEDERATION = "federation"


class BuiltinIdpPluginEnum(str, Enum):
    # 直接身份认证
    LOCAL = "local"
    LDAP = "ldap"
    MAD = "mad"

    # 联邦身份认证
    # 标准协议
    OAUTH = "oauth2.0"
    OIDC = "oidc"
    SAML = "saml2.0"
    # 其他
    WECOM = "wecom"


class SupportedHttpMethodEnum(str, Enum):
    GET = "get"
    POST = "post"


# IDP dispatch配置相关
SUPPORTED_HTTP_METHODS = [SupportedHttpMethodEnum.GET, SupportedHttpMethodEnum.POST]
ACTION_REGEX = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{2,31}")


class BuiltinActionEnum(str, Enum):
    AUTHENTICATE = "authenticate"
    LOGIN = "login"
    CALLBACK = "callback"

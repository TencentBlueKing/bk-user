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
from . import env

# ==============================================================================
# 应用基本信息配置 (请按照说明修改)
# ==============================================================================
# 在蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 中获取 APP_ID 和 APP_TOKEN 的值
APP_ID = env("BK_APP_CODE")
APP_TOKEN = env("BK_APP_SECRET")

# 蓝鲸域名
BK_DOMAIN = env("BK_DOMAIN", default=env("BKPAAS_BK_DOMAIN", default=""))

# 蓝鲸智云开发者中心的域名，形如：http://paas.example.com
BK_PAAS_URL = env("BK_PAAS_URL")
BK_PAAS_INNER_HOST = env("BK_PAAS_INNER_HOST", default=BK_PAAS_URL)

# 蓝鲸登录跳转页面
BK_LOGIN_URL = env("BK_LOGIN_URL", default=f"{BK_PAAS_URL}/login/")
# 蓝鲸登录 API URL
BK_LOGIN_API_URL = env("BK_LOGIN_API_URL", default=f"{BK_PAAS_URL}/login")

# ESB Api URL
BK_COMPONENT_API_URL = env("BK_COMPONENT_API_URL", default=BK_PAAS_INNER_HOST)

# 请求官方 API 默认版本号，可选值为："v2" 或 ""；其中，"v2"表示规范化API，""表示未规范化API
DEFAULT_BK_API_VER = "v2"

# ==============================================================================
# 应用运行环境配置信息
# ==============================================================================
BUILD_STATIC = "static"

# 前端页面是否独立部署，默认为非独立部署
IS_PAGES_INDEPENDENT_DEPLOYMENT = env.bool("IS_PAGES_INDEPENDENT_DEPLOYMENT", default=False)

############
# Core API #
############
BK_USER_CORE_API_HOST = env("BKAPP_BK_USER_CORE_API_HOST", default="http://usermgr.service.consul:8009")


# 特殊标记从 SaaS 请求到 Api 的 IP
CLIENT_IP_FROM_SAAS_HEADER = "Client-IP-From-SaaS"

# ==============================================================================
# 登录相关
# ==============================================================================

# for community version, maybe both 400
IFRAME_HEIGHT = env.int("IFRAME_HEIGHT", default=490)
IFRAME_WIDTH = env.int("IFRAME_WIDTH", default=460)

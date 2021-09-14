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
import urllib.parse

from . import env
from .django_basic import SITE_URL

# ==============================================================================
# 应用基本信息配置
# ==============================================================================
APP_ID = env("BK_APP_CODE")
APP_TOKEN = env("BK_APP_SECRET")

# ==============================================================================
# 蓝鲸平台相关配置
# ==============================================================================
# 蓝鲸平台 URL
BK_PAAS_URL = env("BK_PAAS_URL")

# ESB Api URL
BK_COMPONENT_API_URL = env("BK_COMPONENT_API_URL", default=BK_PAAS_URL)

# ESB API 路径前缀
BK_PAAS_API_PATH_PREFIX = env("BK_PAAS_API_PATH_PREFIX", default="/component")
# 请求 ESB API 默认版本号
DEFAULT_BK_API_VER = "v2"

# ==============================================================================
# 登陆相关
# ==============================================================================
LOGIN_REDIRECT_TO = f"{BK_PAAS_URL}/login/?c_url={SITE_URL}"

# 初始化 Admin 用户名密码
SUPERUSER_USERNAME = env("INITIAL_ADMIN_USERNAME", default="admin")
SUPERUSER_PASSWORD = env("INITIAL_ADMIN_PASSWORD", default="Blueking@2019")

# ==============================================================================
# SaaS 配置
# ==============================================================================
# SaaS 应用 Code
SAAS_CODE = "bk_user_manage"
# SaaS 请求地址，用于拼接访问地址(默认支持二进制部署)
SAAS_URL = env("SAAS_URL", default=urllib.parse.urljoin(BK_PAAS_URL, f"/o/{SAAS_CODE}/"))

# SaaS 偏好 client ip 头
CLIENT_IP_FROM_SAAS_HEADER = "HTTP_CLIENT_IP_FROM_SAAS"

# 可通过 SaaS 管理的用户目录类型
CAN_MANUAL_WRITE_LISTS = ["local"]

# ==============================================================================
# 权限中心相关配置
# ==============================================================================
# 默认启用，禁用时会跳过权限校验步骤
ENABLE_IAM = True


def get_iam_config(app_id: str, app_token: str) -> dict:
    return dict(
        api_host=env("BK_IAM_V3_INNER_HOST"),
        system_id=env("BK_IAM_SYSTEM_ID", default="bk-user"),
        # iam app 访问 url 用于回调拼接
        iam_app_host=env(
            "BK_IAM_SAAS_HOST",
            default=f"{BK_PAAS_URL}/o/{env('BK_IAM_V3_APP_CODE', default='bk_iam')}",
        ),
        apply_path="apply-custom-perm",
        # 自己的 app_id & app_token
        own_app_id=app_id,
        own_app_token=app_token,
    )


IAM_CONFIG = get_iam_config(APP_ID, APP_TOKEN)

# 与 SaaS 约定的权限校验头，未传递时跳过权限校验
NEED_IAM_HEADER = "HTTP_NEED_IAM"
ACTION_ID_HEADER = "HTTP_ACTION_ID"

# ===============================================================================
# API 访问限制（暂未开启）
# ===============================================================================
INTERNAL_AUTH_TOKENS = {"TCwCnoiuUgPccj8y0Wx187vJBqzqddfLlm": {"username": "iadmin"}}
ACCESS_APP_WHITE_LIST = {"bk-iam": "lLP3gabV8M0C9vbwHQwzSYJX3WumcJsDSdVNQtq6FJVCLqJX6o"}

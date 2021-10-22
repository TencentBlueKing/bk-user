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
from django.conf import settings


class ConfFixture(object):
    BACKEND_TYPE = "bk_token"
    USER_BACKEND = "bk_token.backends.TokenBackend"
    LOGIN_REQUIRED_MIDDLEWARE = "bk_token.middlewares.LoginRequiredMiddleware"
    USER_MODEL = "bk_token.models.UserProxy"

    CONSOLE_LOGIN_URL = settings.BK_PAAS_URL
    LOGIN_URL = settings.BK_PAAS_URL + "/login/"
    LOGIN_PLAIN_URL = settings.BK_PAAS_URL + "/login/plain/"
    VERIFY_URL = settings.BK_LOGIN_API_URL + "/accounts/is_login/"
    USER_INFO_URL = settings.BK_LOGIN_API_URL + "/accounts/get_user/"
    HAS_PLAIN = False
    ADD_CROSS_PREFIX = False
    ADD_APP_CODE = True
    APP_KEY = "app_id"
    SETTINGS_APP_KEY = "APP_ID"

    IFRAME_HEIGHT = settings.IFRAME_HEIGHT
    IFRAME_WIDTH = settings.IFRAME_WIDTH

    SMS_CLIENT_MODULE = "cmsi"
    SMS_CLIENT_FUNC = "send_sms"
    SMS_CLIENT_USER_ARGS_NAME = "receiver__username"
    SMS_CLIENT_CONTENT_ARGS_NAME = "content"

    BK_JWT_MIDDLEWARE = "bk_jwt.middlewares.BkJwtLoginRequiredMiddleware"
    BK_JWT_BACKEND = "bk_jwt.backends.BkJwtBackend"

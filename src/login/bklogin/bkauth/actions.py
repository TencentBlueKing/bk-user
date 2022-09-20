# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


import urllib.error
import urllib.parse
import urllib.request
from builtins import str

from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect

from bklogin.bkauth.constants import REDIRECT_FIELD_NAME
from bklogin.bkauth.utils import get_bk_token, is_safe_url, record_login_log, set_bk_token_invalid
from bklogin.common.log import logger

"""
actions for login success/fail
"""


BK_LOGIN_URL = str(settings.LOGIN_URL)
BK_COOKIE_NAME = settings.BK_COOKIE_NAME


def login_failed_response(request, redirect_to, app_id):
    """
    登录失败跳转，目前重定向到登录，后续可返还支持自定义的错误页面
    """
    redirect_url = BK_LOGIN_URL
    query = {}
    if redirect_to:
        query[REDIRECT_FIELD_NAME] = redirect_to
    if app_id:
        query["app_id"] = app_id

    if query:
        redirect_url = "%s?%s" % (BK_LOGIN_URL, urllib.parse.urlencode(query))

    logger.debug("login_failed_response, redirect_to=%s, app_id=%s", redirect_to, app_id)
    response = HttpResponseRedirect(redirect_url)
    response = set_bk_token_invalid(request, response)
    return response


def login_success_response(request, user_or_form, redirect_to, app_id):
    """
    用户验证成功后，登录处理
    """
    # 判读是form还是user
    if isinstance(user_or_form, AuthenticationForm):
        user = user_or_form.get_user()
        username = user.username
        # username = user_or_form.cleaned_data.get('username', '')
    else:
        user = user_or_form
        username = user.username

    # 检查回调URL是否安全，防钓鱼
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        # 调整到根目录
        redirect_to = "/console/"

    # if from logout
    if redirect_to == "/logout/":
        redirect_to = "/console/"

    logger.debug("login_success_response, username=%s, redirect_to=%s, app_id=%s", username, redirect_to, app_id)

    # 设置用户登录
    try:
        # 这个是django默认的login函数
        auth_login(request, user)
    except Exception:  # pylint: disable=broad-except
        # will raise django.db.utils.DatabaseError: Save with update_fields did not affect any rows.
        # while auth_login at the final step user_logged_in.send, but it DO NOT MATTERS!
        logger.debug("auth_login fail", exc_info=True)

    # 记录登录日志
    record_login_log(request, username, app_id)

    secure = False
    # uncomment this if you need a secure cookie;
    # the http domain will not access the bk_token in secure cookie
    # secure = (settings.HTTP_SCHEMA == "https")
    bk_token, expire_time = get_bk_token(username)
    response = HttpResponseRedirect(redirect_to)
    response.set_cookie(
        BK_COOKIE_NAME,
        urllib.parse.quote_plus(bk_token),
        expires=expire_time,
        domain=settings.BK_COOKIE_DOMAIN,
        httponly=True,
        secure=secure,
    )

    # set cookie for app or platform
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        request.user.language,
        # max_age=settings.LANGUAGE_COOKIE_AGE,
        expires=expire_time,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
    )
    return response


def login_redirect_response(request, redirect_url, is_from_logout):
    """
    登录重定向
    """
    response = HttpResponseRedirect(redirect_url)
    # 来自注销，则需清除蓝鲸bk_token
    if is_from_logout:
        response = set_bk_token_invalid(request, response)
    return response

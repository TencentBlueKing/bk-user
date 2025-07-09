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
import urllib

from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from . import settings as wecom_settings
from .utils import gen_qr_login_url
from bklogin.bkauth import actions
from bklogin.bkauth.constants import REDIRECT_FIELD_NAME
from bklogin.bkauth.views import _bk_login
from bklogin.common.log import logger


def wecom_login(request):
    """
    企业微信扫码登录处理
    """
    # 获取用户实际请求的URL, 目前account.REDIRECT_FIELD_NAME = 'c_url'
    redirect_to = request.GET.get(REDIRECT_FIELD_NAME, "")
    # 获取用户实际访问的蓝鲸应用
    app_id = request.GET.get("app_id", "")

    # 来自注销
    is_from_logout = bool(request.GET.get("is_from_logout") or 0)

    # 企业微信扫码登录回调后会自动添加code参数
    code = request.GET.get("code")

    # 若没有code参数，则表示需要显示二维码登录页面
    if code is None or is_from_logout:
        # 生成扫码登录的链接
        qr_login_url, state = gen_qr_login_url(request, {"app_id": app_id, REDIRECT_FIELD_NAME: redirect_to})
        request.session["state"] = state
        # 直接跳转到企业微信官方登录页面
        logger.debug(
            "custom_login:oauth.wechat_qr redirecting to wechat login, code=%s, is_from_logout=%s",
            code,
            is_from_logout,
        )
        return HttpResponseRedirect(qr_login_url)

    # 已经有企业认证票据参数（如code参数），表示企业登录后的回调或企业认证票据还存在
    # 处理state参数（可选验证）
    state = request.GET.get("state")
    state_dict = dict(urllib.parse.parse_qsl(state))
    app_id = state_dict.get("app_id")
    redirect_to = state_dict.get(REDIRECT_FIELD_NAME, "")

    state_in_session = request.session.get("wecom_state")

    # 校验state，防止csrf攻击
    if not state and state != state_in_session:
        logger.debug(
            "wecom_login: state != state_in_session [state=%s, state_in_session=%s]",
            state,
            state_in_session,
        )
        return actions.login_failed_response(request, redirect_to, app_id)

    logger.debug("code=%s, redirect_to=%s, app_id=%s", code, redirect_to, app_id)
    # 验证用户登录
    user = authenticate(code=code)
    if user is None:
        logger.debug("wecom_login: user is None, will redirect_to=%s", redirect_to)
        return actions.login_failed_response(request, redirect_to, app_id)

    # 成功，则调用蓝鲸登录成功的处理函数，并返回响应
    logger.debug("wecom_login: login success, will redirect_to=%s", redirect_to)
    return actions.login_success_response(request, user, redirect_to, app_id)


def login(request):
    """
    支持用户名密码登录和企业微信扫码登录
    """
    # 检查是否是企业微信登录回调
    if request.GET.get("code"):
        # 有code参数，说明是企业微信登录回调，直接处理
        return wecom_login(request)

    # 检查是否是企业微信登录跳转请求
    if request.GET.get("auth_method") == "wechat":
        return wecom_login(request)

    # 否则，调用蓝鲸登录处理
    response = _bk_login(request)

    # 如果是TemplateResponse，添加企业微信登录启用状态
    if isinstance(response, TemplateResponse):
        # 检查是否启用企业微信登录
        enable_wechat_login = _check_wechat_available()
        response.context_data.update(
            {
                "enable_wechat_login": enable_wechat_login,
            }
        )

    return response


def _check_wechat_available():
    """
    检查企业微信登录是否可用
    """
    try:
        required_configs = [
            wecom_settings.CORP_ID,
            wecom_settings.CORP_SECRET,
            wecom_settings.AGENT_ID,
        ]

        return all(config for config in required_configs)
    except Exception as e:
        logger.warning("检查企业微信配置时出错: %s", e)
        return False

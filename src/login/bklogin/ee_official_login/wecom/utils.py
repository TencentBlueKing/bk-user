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
import random
import string
import urllib
from typing import Dict
from urllib.parse import urlencode

import requests
from django.conf import settings as bk_settings
from django.http import HttpRequest

from . import settings as settings
from bklogin.common.log import logger


def gen_oauth_state_security_token(length: int = 8) -> str:
    """
    生成随机的 state，防止 csrf
    """
    allowed_chars = string.ascii_letters + string.digits
    return "".join([random.choice(allowed_chars) for _ in range(length)])


def gen_qr_login_url(request: HttpRequest, extra_param: Dict) -> tuple:
    """
    生成扫码登录的URL
    """
    redirect_uri = bk_settings.LOGIN_COMPLETE_URL
    state = gen_oauth_state_security_token()

    extra_param = {} if extra_param is None or not isinstance(extra_param, dict) else extra_param
    extra_param["security_token"] = gen_oauth_state_security_token()
    state = "&".join(["%s=%s" % (k, v) for k, v in list(extra_param.items()) if v is not None and v != ""])

    wecom_qr_login_url = "%s?%s" % (
        settings.QR_LOGIN_URL,
        urllib.parse.urlencode(
            {
                "login_type": "CorpApp",
                "appid": settings.CORP_ID,
                "agentid": settings.AGENT_ID,
                "redirect_uri": redirect_uri,
                "state": state,
            }
        ),
    )

    return wecom_qr_login_url, state


def get_access_token():
    """
    获取access_token
    """
    params = {
        "corpid": settings.CORP_ID,
        "corpsecret": settings.CORP_SECRET,
    }

    resp = requests.get(url=settings.ACCESS_TOKEN_URL, params=params)
    if resp.status_code != 200:
        logger.error(
            "get_access_token http error: status_code=%s, content=%s",
            resp.status_code,
            resp.content[:100] if resp.content else "",
        )
        return None

    data = resp.json()
    # 若 errcode 为 0 则获取成功，否则获取失败
    if data.get("errcode") == 0:
        return data.get("access_token")
    else:
        logger.error("get_access_token failed: %s", data.get("errmsg", "Unknown error"))
        return None


def get_user_id_by_code(access_token, code):
    """
    通过 code 获取用户登录身份 userid
    """
    params = {
        "access_token": access_token,
        "code": code,
    }

    resp = requests.get(url=settings.GET_USER_URL, params=params)
    if resp.status_code != 200:
        logger.error(
            "get_user_id_by_code http error: status_code=%s, content=%s",
            resp.status_code,
            resp.content[:100] if resp.content else "",
        )
        return None

    data = resp.json()
    if data.get("errcode") == 0:
        return data.get("userid")
    else:
        logger.error("get_user_id_by_code failed: %s", data.get("errmsg", "Unknown error"))
        return None


def get_user_info_by_userid(access_token, userid):
    """
    通过 userid 获取用户信息
    """
    params = {
        "access_token": access_token,
        "userid": userid,
    }

    resp = requests.get(url=settings.GET_USER_INFO_URL, params=params)
    if resp.status_code != 200:
        logger.error(
            "get_user_info_by_userid http error: status_code=%s, content=%s",
            resp.status_code,
            resp.content[:100] if resp.content else "",
        )
        return None

    data = resp.json()
    if data.get("errcode") == 0:
        return data
    else:
        logger.error("get_user_info_by_userid failed: %s", data.get("errmsg", "Unknown error"))
        return None

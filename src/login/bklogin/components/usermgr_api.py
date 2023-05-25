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


from django.conf import settings
from django.utils import translation

from bklogin.common.log import logger
from bklogin.components.esb import _call_esb_api
from bklogin.components.http import http_get, http_post
from bklogin.components.util import _remove_sensitive_info

"""
usermgr api
"""

BK_USERMGR_HOST = settings.BK_USERMGR_API_URL


def _call_usermgr_api(http_func, url, data):
    headers = {
        "Blueking-Language": translation.get_language(),
        "Content-Type": "application/json",
    }

    try:
        ok, resp_data = http_func(url, data, headers=headers)
        if not ok:
            return False, -1, "verify from usermgr server fail: %s" % resp_data.get("error"), None
    except Exception:
        logger.exception(
            "_call_usermgr_api fail: method=%s, url=%s, data=%s", http_func.__name__, url, _remove_sensitive_info(data)
        )
        return False, -1, "verify from usermgr server fail, error happended", None

    # TODO: still use the result to verify?
    if not resp_data.get("result"):
        logger.info(
            "_call_usermgr_api fail: method=%s, url=%s, header=%s, data=%s, response=%s",
            http_func.__name__,
            url,
            headers,
            _remove_sensitive_info(data),
            resp_data,
        )
        return False, resp_data.get("code", -1), resp_data.get("message", "usermgr api fail"), resp_data.get("data")

    return True, 0, "ok", resp_data.get("data")


def direct_authenticate(username, password, domain=""):
    """
    认证用户名和密码
    username: 用户名、电话号码、邮箱三选一，如果存在重名，会验证失败
    """
    path = "/api/v1/login/check/"
    url = "{host}{path}".format(host=BK_USERMGR_HOST, path=path)

    data = {
        "username": username,
        "password": password,
    }
    if domain:
        data["domain"] = domain

    ok, code, message, _data = _call_usermgr_api(
        http_post,
        url,
        data,
    )
    return ok, code, message, _data or {}


def direct_batch_query_users(username_list=[], is_complete=False):
    """
    批量获取用户，可以获取所有
    """
    path = "/api/v1/login/profile/query/"
    url = "{host}{path}".format(host=BK_USERMGR_HOST, path=path)

    data = {
        "username_list": username_list,
        "is_complete": is_complete,
    }

    ok, _, message, _data = _call_usermgr_api(http_post, url, data)
    return ok, message, _data


def direct_upsert_user(username, **kwargs):
    """
    创建或更新用户
    主要用于ee_login，企业第三方应用某些情况下需要支持将用户存储到用户管理
    """
    path = "/api/v1/login/profile/"
    url = "{host}{path}".format(host=BK_USERMGR_HOST, path=path)

    data = {
        "username": username,
    }
    data.update(kwargs)
    ok, _, message, _data = _call_usermgr_api(http_post, url, data)
    return ok, message, _data


def direct_get_categories():
    path = "/api/v2/categories/"
    url = "{host}{path}".format(host=BK_USERMGR_HOST, path=path)

    data = {
        "no_page": True,
        "fields": "domain,id,default",
        # "lookup_field": "enabled",
        # "exact_lookups": True,
    }

    ok, _, message, _data = _call_usermgr_api(http_get, url, data)
    if "results" in _data:
        _data = _data["results"]
    return ok, message, _data


def direct_get_profile_by_code(code, fields="username"):
    path = "/api/v2/profiles/{code}/".format(code=code)
    url = "{host}{path}".format(host=BK_USERMGR_HOST, path=path)

    data = {"fields": fields, "lookup_field": "code"}

    ok, _, message, _data = _call_usermgr_api(http_get, url, data)
    return ok, message, _data


def esb_authenticate(username, password, domain=""):
    """
    认证用户名和密码
    username: 用户名、电话号码、邮箱三选一，如果存在重名，会验证失败
    """
    path = "/api/c/compapi/v1/usermanage/login/check/"

    data = {
        "username": username,
        "password": password,
    }
    if domain:
        data["domain"] = domain

    ok, code, message, _data = _call_esb_api(http_post, path, data)
    return ok, code, message, _data or {}


def esb_batch_query_users(username_list=[], is_complete=False):
    """
    批量获取用户，可以获取所有
    """
    path = "/api/c/compapi/v1/usermanage/login/profile/query/"

    data = {
        "username_list": username_list,
        "is_complete": is_complete,
    }

    ok, _, message, _data = _call_esb_api(http_post, path, data)
    return ok, message, _data


def esb_upsert_user(username, **kwargs):
    """
    创建或更新用户
    主要用于ee_login，企业第三方应用某些情况下需要支持将用户存储到用户管理
    """
    path = "/api/c/compapi/v1/usermanage/login/profile/"

    data = {
        "username": username,
    }
    data.update(kwargs)
    # ok, _, message, _data = _call_usermgr_api(http_post, url, data)
    ok, _, message, _data = _call_esb_api(http_post, path, data)
    return ok, message, _data


def esb_get_categories():
    path = "/api/c/compapi/v2/usermanage/list_categories/"

    data = {
        "no_page": True,
        "fields": "domain,id,default",
        # "lookup_field": "enabled",
        # "exact_lookups": True,
    }

    ok, _, message, _data = _call_esb_api(http_get, path, data)
    return ok, message, _data


def esb_get_profile_by_code(code, fields="username"):
    path = "/api/c/compapi/v2/usermanage/retrieve_user/"

    data = {
        "id": code,
        "lookup_field": "code",
        "fields": fields,
    }

    ok, _, message, _data = _call_esb_api(http_get, path, data)
    return ok, message, _data


if settings.BK_LOGIN_API_AUTH_ENABLED:
    message = "bk_login api auth enabled=True, will call usermgr api via esb"
    print(message)
    logger.debug(message)

    authenticate = esb_authenticate
    batch_query_users = esb_batch_query_users
    upsert_user = esb_upsert_user
    get_categories = esb_get_categories
    get_profile_by_code = esb_get_profile_by_code
else:
    message = "bk_login api auth enabled=False, will call usermgr api directly"
    print(message)
    logger.debug(message)

    authenticate = direct_authenticate
    batch_query_users = direct_batch_query_users
    upsert_user = direct_upsert_user
    get_categories = direct_get_categories
    get_profile_by_code = direct_get_profile_by_code

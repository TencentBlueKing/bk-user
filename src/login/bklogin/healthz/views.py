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


import os
from builtins import str

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext as _

from bklogin.common.exceptions import LoginErrorCodes

# ====================  helpers =========================

LOGIN_MODULE_CODE = "1302000"


def _gen_json_response(ok, code, message, data):
    """
    ok: True/False
    code:  平台 1302000 / 模块 1302100 / 具体错误  1302105
    message: 报错信息
    data: dict, 内容自定义
    """
    return JsonResponse({"ok": ok, "code:": code, "message": message, "data": data}, status=200)


# ====================  check =========================


def _check_settings():
    """
    check settings, 注意不暴露密码等敏感信息
    """
    # check settings, 注意不暴露密码等敏感信息
    try:
        settings.ESB_TOKEN
        {
            "debug": settings.DEBUG,
            "env": os.getenv("BK_ENV", "unknown"),
            "cookie_domain": settings.BK_COOKIE_DOMAIN,
            "mysql": {
                "host": settings.DATABASES.get("default", {}).get("HOST"),
                "port": settings.DATABASES.get("default", {}).get("PORT"),
                "user": settings.DATABASES.get("default", {}).get("USER"),
                "database": settings.DATABASES.get("default", {}).get("NAME"),
            },
        }
    except Exception as e:
        return False, _(u"配置文件不正确, 缺失对应配置: %s") % str(e), LoginErrorCodes.E1302001_BASE_SETTINGS_ERROR.value

    return True, "ok", 0


def _check_database():
    try:
        from bklogin.bkaccount.models import BkToken

        objs = BkToken.objects.all()[:3]
        [o.token for o in objs]
    except Exception as e:
        return False, _(u"数据库连接存在问题: %s") % str(e), LoginErrorCodes.E1302002_BASE_DATABASE_ERROR.value

    return True, "ok", 0


def healthz(request):
    """
    health check
    """
    data = {}

    # 强依赖
    _check_funcs = [
        ("settings", _check_settings),
        ("database", _check_database),
    ]

    for name, func in _check_funcs:
        is_health, message, code = func()
        if is_health:
            data[name] = "ok"
        else:
            return _gen_json_response(ok=False, code=code, message=message, data={})

    return _gen_json_response(ok=True, code=LOGIN_MODULE_CODE, message="OK", data=data)


def ping(request):
    return HttpResponse("pong", content_type="text/plain")

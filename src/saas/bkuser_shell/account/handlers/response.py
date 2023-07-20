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
from django.http import HttpResponseRedirect, JsonResponse

from bkuser_shell.account.http import build_redirect_url
from bkuser_shell.common.exceptions import BkJwtVerifyError


class ResponseHandler(object):
    def __init__(self, _conf_fixture, _settings):
        """
        @param {object} confFixture Account Package Settings
        @param {object} settings Django User Settings
        """
        self._conf = _conf_fixture
        self._settings = _settings

    def build_302_response(self, request):
        _next = request.build_absolute_uri()
        if self._conf.ADD_CROSS_PREFIX:
            _next = self._conf.CROSS_PREFIX + _next

        _login_url = build_redirect_url(
            _next,
            self._conf.LOGIN_URL,
            self._conf.C_URL,
            extra_args=self._build_extra_args(),
        )
        return HttpResponseRedirect(_login_url)

    def build_401_response(self, request):
        context = {
            "login_url": self._conf.LOGIN_PLAIN_URL,
            "width": self._conf.IFRAME_WIDTH,
            "height": self._conf.IFRAME_HEIGHT,
            "extra_params": self._build_extra_args(),
        }
        return JsonResponse(context, status=401)

    def build_403_of_access_permission_response(self, request, message):
        """
        处理认证通过但无访问权限
        """
        context = {"code": -2, "message": message}
        return JsonResponse(context, status=403)

    def _build_page_401_response_to_platform(self, request):
        """
        Directly redirect to PAAS-LOGIN-PLATFORM
        """
        _next = request.build_absolute_uri()
        if self._conf.ADD_CROSS_PREFIX:
            _next = self._conf.CROSS_PREFIX + _next

        _login_url = build_redirect_url(
            _next,
            self._conf.LOGIN_URL,
            self._conf.C_URL,
            extra_args=self._build_extra_args(),
        )
        return HttpResponseRedirect(_login_url)

    def _build_extra_args(self):
        extra_args = {"size": "big"}
        if self._conf.ADD_APP_CODE:
            extra_args.update({self._conf.APP_KEY: getattr(self._settings, self._conf.SETTINGS_APP_KEY)})
        return extra_args

    def build_bk_jwt_401_response(self, request):
        """
        BK_JWT鉴权异常
        """
        context = {
            "result": False,
            "code": BkJwtVerifyError.ERROR_CODE,
            "message": u"您的登陆请求无法经BK JWT检测，请与管理人员联系",
        }
        return JsonResponse(context, status=401)

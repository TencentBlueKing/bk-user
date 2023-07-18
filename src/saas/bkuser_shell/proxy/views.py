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
import logging

from django.http import HttpResponse
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.template.response import TemplateResponse

from .proxy import BkUserApiProxy
from bkuser_shell.account.decorators import login_exempt
from bkuser_shell.common.error_codes import error_codes

logger = logging.getLogger(__name__)


class HealthzViewSet(BkUserApiProxy):
    permission_classes: list = []

    def list(self, request):
        return self.do_proxy(request)

    def pong(self, request):
        return HttpResponse(content="pong")


class LoginInfoViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        username = request.user.username
        return self.do_proxy(request, rewrite_path=f"/api/v1/web/profiles/me/?username={username}")


class CommonProxyViewSet(BkUserApiProxy):
    def request(self, request, *args, **kwargs):
        return self.do_proxy(request)


class CommonProxyNoAuthViewSet(BkUserApiProxy):
    permission_classes: list = []

    def request(self, request, *args, **kwargs):
        return self.do_proxy(request)


class WebPageViewSet(BkUserApiProxy):
    serializer_class = None
    permission_classes: list = []

    @classmethod
    def as_view(cls, actions=None, **initkwargs):
        view = super().as_view(actions, **initkwargs)
        return login_exempt(view)

    def index(self, request):
        try:
            return TemplateResponse(request=request, template=get_template("index.html"))
        except TemplateDoesNotExist:
            raise error_codes.CANNOT_FIND_TEMPLATE

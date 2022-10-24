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

from functools import wraps

from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _
from django.views.generic import View

from bklogin.bkauth.actions import login_success_response
from bklogin.bkauth.constants import REDIRECT_FIELD_NAME
from bklogin.bkauth.forms import BkAuthenticationForm
from bklogin.bkauth.utils import is_safe_url, set_bk_token_invalid
from bklogin.common.exceptions import AuthenticationError, PasswordNeedReset, UserExpiredException
from bklogin.common.log import logger
from bklogin.common.usermgr import get_categories_str


def only_plain_xframe_options_exempt(view_func):
    """
    only allow /plain/ to be opened by a iframe
    add some code: from django.views.decorators.clickjacking import xframe_options_exempt
    """

    def wrapped_view(*args, **kwargs):
        resp = view_func(*args, **kwargs)

        if not isinstance(resp, HttpResponseRedirect):
            if hasattr(resp, "_request"):
                origin_url = resp._request.META.get("HTTP_REFERER")
                login_host = resp._request.get_host()

                if resp._request.path_info == "/plain/" and is_safe_url(url=origin_url, host=login_host):
                    resp.xframe_options_exempt = True
        return resp

    return wraps(view_func)(wrapped_view)


class LoginView(View):
    """
    登录 & 登录弹窗
    """

    is_plain = False

    @only_plain_xframe_options_exempt
    def get(self, request):
        return self._login(request)

    @only_plain_xframe_options_exempt
    def post(self, request):
        return self._login(request)

    def _login(self, request):
        logger.debug(
            "login_type is %s, using custom_login: %s", settings.LOGIN_TYPE, settings.LOGIN_TYPE == "custom_login"
        )
        # 判断调用方式
        if settings.LOGIN_TYPE != "custom_login":
            return _bk_login(request)

        # 调用自定义login view
        custom_login_view = import_string(settings.CUSTOM_LOGIN_VIEW)
        return custom_login_view(request)


def _bk_login(request):
    """
    登录页面和登录动作
    """
    redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, ""))
    app_id = request.POST.get("app_id", request.GET.get("app_id", ""))

    token_set_password_url = ""
    error_message = ""
    login_redirect_to = ""
    user_expired = False

    # POST
    if request.method == "POST":
        form = BkAuthenticationForm(request, data=request.POST)
        try:
            if form.is_valid():
                return login_success_response(request, form, redirect_to, app_id)
        except AuthenticationError as e:
            login_redirect_to = e.redirect_to
            error_message = e.message
        except PasswordNeedReset as e:
            token_set_password_url = e.reset_password_url
            error_message = e.message
        except UserExpiredException as e:
            login_redirect_to = e.redirect_to
            user_expired = e.user_expired
        else:
            error_message = _("账户或者密码错误，请重新输入")
    # GET
    else:
        form = BkAuthenticationForm(request)

    # NOTE: get categories from usermgr
    categories = get_categories_str()

    current_site = get_current_site(request)
    context = {
        "form": form,
        "error_message": error_message,
        "user_expired": user_expired,
        REDIRECT_FIELD_NAME: redirect_to,
        "site": current_site,
        "site_name": current_site.name,
        "app_id": app_id,
        "token_set_password_url": token_set_password_url,
        "forget_password_url": f"{settings.BK_USERMGR_SAAS_URL}/reset_password",
        "login_redirect_to": login_redirect_to,
        "categories": categories,
        "is_plain": request.path_info == "/plain/",
    }

    # NOTE: account/login.html 为支持自适应大小的模板
    response = TemplateResponse(request, "login.html", context)
    response = set_bk_token_invalid(request, response)
    return response


class LogoutView(View):
    """
    登出并重定向到登录页面
    """

    def get(self, request):
        auth_logout(request)
        next_page = None

        if REDIRECT_FIELD_NAME in request.POST or REDIRECT_FIELD_NAME in request.GET:
            next_page = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME))
            # Security check -- don't allow redirection to a different host.
            if not is_safe_url(url=next_page, host=request.get_host()):
                next_page = request.path

        if next_page:
            # Redirect to this page until the session has been cleared.
            response = HttpResponseRedirect(next_page)
        else:
            # Redirect to login url.
            response = HttpResponseRedirect("%s?%s" % (settings.LOGIN_URL, "is_from_logout=1"))

        # 将登录票据设置为不合法
        response = set_bk_token_invalid(request, response)
        return response


def csrf_failure(request, reason=""):
    return HttpResponseForbidden(render(request, "csrf_failure.html"), content_type="text/html")

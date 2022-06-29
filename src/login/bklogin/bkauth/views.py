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
from django.contrib.auth import get_user_model
from django.contrib.auth import logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _
from django.views.generic import View

from bklogin.api.utils import APIV1FailJsonResponse, APIV1OKJsonResponse
from bklogin.bkauth.actions import login_license_fail_response, login_success_response
from bklogin.bkauth.constants import BUILTIN_USER__CONTACT, REDIRECT_FIELD_NAME
from bklogin.bkauth.forms import BkAuthenticationForm
from bklogin.bkauth.utils import is_safe_url, set_bk_token_invalid
from bklogin.common.exceptions import AuthenticationError, PasswordNeedReset
from bklogin.common.log import logger
from bklogin.common.mixins.exempt import LoginExemptMixin
from bklogin.common.usermgr import get_categories_str
from bklogin.components import usermgr_api
from bklogin.components.license import check_license


def only_plain_xframe_options_exempt(view_func):
    """
    only allow /plain/ to be opened by a iframe
    add some code: from django.views.decorators.clickjacking import xframe_options_exempt
    """

    def wrapped_view(*args, **kwargs):
        resp = view_func(*args, **kwargs)

        if not isinstance(resp, HttpResponseRedirect):
            origin_url = resp._request.META.get("HTTP_REFERER")
            login_host = resp._request.get_host()

            if resp._request.path_info == "/plain/" and is_safe_url(url=origin_url, host=login_host):
                resp.xframe_options_exempt = True

        return resp

    return wraps(view_func)(wrapped_view)


class LoginView(LoginExemptMixin, View):
    """
    登录 & 登录弹窗
    """

    is_plain = False

    @only_plain_xframe_options_exempt
    def get(self, request):
        # TODO1: from django.views.decorators.clickjacking import xframe_options_exempt
        # TODO2: should check if the request from the legal domain
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

        if settings.EDITION == "ee":
            # 校验企业正式是否有效，无效则不可登录
            is_license_ok, msg, valid_start_time, valid_end_time = check_license()
            if not is_license_ok:
                return login_license_fail_response(request)

        # 调用自定义login view
        custom_login_view = import_string(settings.CUSTOM_LOGIN_VIEW)
        return custom_login_view(request)


class CaptchaView(LoginExemptMixin, View):
    def get(self, request):
        # 获取参数
        query_params = request.GET
        request_data = {
            "username": query_params["username"],
            "domain": query_params.get("domain", "default.local"),
            "email": query_params.get("email", None),
            "telephone": query_params.get("telephone", None),
        }
        # 发送验证码
        ok, code, message, data = usermgr_api.send_captcha(request_data)
        logger.debug(
            "usermgr_api.send_captcha result: ok=%s, message=%s, data=%s",
            ok,
            message,
            data,
        )
        if not ok:
            return APIV1FailJsonResponse(code=code, message=message)
        return APIV1OKJsonResponse(_("验证码信息发送成功"), data=data)

    def post(self, request):
        app_id = request.POST.get("app_id", request.GET.get("app_id", ""))
        post_data = request.POST
        domain = "default.local" if not post_data.get("domain") else post_data["domain"]
        username = post_data["username"]
        redirect_to = post_data.get("redirect_to")

        # 构建验证码检验数据
        verify_data = {
            "token": post_data["token"],
            "captcha": post_data["captcha"],
            "username": username,
            "domain": domain,
        }
        # 调用接口校验
        ok, code, message, data = usermgr_api.verify_captcha(verify_data)

        # 认证不通过
        if not ok:
            return APIV1FailJsonResponse(code=code, message=message)

        ok, message, user_list = usermgr_api.batch_query_users(username_list=[f"{username}@{domain}"])
        # 验证成功，查看是否需要进行绑定邮箱或者手机号
        logger.debug(
            "usermgr_api.batch_query_users result: ok=%s, message=%s, user_list=%s",
            ok,
            message,
            user_list,
        )
        if not ok:
            return APIV1FailJsonResponse(code=code, message=message)

        # 查看是否绑定相应发送方法
        user_data = user_list[0]
        if data["send_method"] in BUILTIN_USER__CONTACT and not user_data.get(data["send_method"]):
            update_data = {data["send_method"]: data["authenticated_value"]}
            ok, message, data = usermgr_api.upsert_user(username, **update_data)
            if not ok:
                logger.error(
                    "fail to update user %s's bind %s = %s: %s",
                    user_data["username"],
                    data["send_method"],
                    data["authenticated_value"],
                    message,
                )
                return APIV1FailJsonResponse(message=message)

        UserModel = get_user_model()
        user = UserModel(post_data["username"])
        user.fill_with_userinfo(user_data)

        return login_success_response(request, user, redirect_to, app_id)


def _bk_login(request):
    """
    登录页面和登录动作
    """
    authentication_form = BkAuthenticationForm
    # NOTE: account/login.html 为支持自适应大小的模板
    template_name = "account/login.html"
    forget_reset_password_url = f"{settings.BK_USERMGR_SAAS_URL}/reset_password"
    token_set_password_url = ""

    redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, ""))

    app_id = request.POST.get("app_id", request.GET.get("app_id", ""))

    if settings.EDITION == "ee":
        # 校验企业证书是否有效，无效则不可登录
        is_license_ok, msg, valid_start_time, valid_end_time = check_license()
    else:
        is_license_ok = True
        template_name = "account/login_ce.html"

    error_message = ""
    login_redirect_to = ""

    # POST
    if request.method == "POST" and is_license_ok:
        form = authentication_form(request, data=request.POST)
        try:
            if form.is_valid():
                return login_success_response(request, form, redirect_to, app_id, two_refactor_authentication=True)
        except AuthenticationError as e:
            login_redirect_to = e.redirect_to
            error_message = e.message
        except PasswordNeedReset as e:
            token_set_password_url = e.reset_password_url
            error_message = e.message
        else:
            error_message = _("账户或者密码错误，请重新输入")
    # GET
    else:
        form = authentication_form(request)

    # NOTE: get categories from usermgr
    categories = get_categories_str()

    current_site = get_current_site(request)
    context = {
        "form": form,
        "error_message": error_message,
        REDIRECT_FIELD_NAME: redirect_to,
        "site": current_site,
        "site_name": current_site.name,
        "app_id": app_id,
        "is_license_ok": is_license_ok,
        "token_set_password_url": token_set_password_url,
        "forget_password_url": forget_reset_password_url,
        "login_redirect_to": login_redirect_to,
        "categories": categories,
        "is_plain": request.path_info == "/plain/",
    }

    response = TemplateResponse(request, template_name, context)
    response = set_bk_token_invalid(request, response)
    return response


class LogoutView(LoginExemptMixin, View):
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

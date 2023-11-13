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
from typing import Any, Callable, Dict, List
from urllib.parse import quote_plus, urljoin

import pydantic
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.generic import View

from bklogin.common.error_codes import error_codes
from bklogin.common.request import parse_request_body_json
from bklogin.common.response import APISuccessResponse
from bklogin.component.bk_user import api as bk_user_api
from bklogin.component.bk_user.constants import IdpStatus
from bklogin.idp_plugins.base import BaseCredentialIdpPlugin, BaseFederationIdpPlugin, get_plugin_cls
from bklogin.idp_plugins.constants import AllowedHttpMethodEnum, BuiltinActionEnum
from bklogin.idp_plugins.exceptions import (
    InvalidParamError,
    ParseRequestBodyError,
    UnexpectedDataError,
    ValidationError,
)

from .constants import ALLOWED_SIGN_IN_TENANT_USERS_SESSION_KEY, REDIRECT_FIELD_NAME, SIGN_IN_TENANT_ID_SESSION_KEY
from .manager import BkTokenManager


# 确保无论何时，响应必然有CSRFToken Cookie
@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginView(View):
    """
    登录页面
    """

    # 登录成功后默认重定向到蓝鲸桌面
    default_redirect_to = "/console/"
    template_name = "index.html"

    def _get_success_url_allowed_hosts(self, request):
        # FIXME: request.get_host()会从header获取，可能存在伪造的情况，是否修改为直接从settings读取更加安全呢？
        #  ALLOWED_REDIRECT_HOSTS 需要支持正则，参考Django Settings ALLOWED_HOST配置
        #  https://github.com/django/django/blob/main/django/http/request.py#L715
        return {request.get_host(), *settings.ALLOWED_REDIRECT_HOSTS}

    def _get_redirect_url(self, request):
        """如果安全的话，返回用户发起的重定向URL"""
        # 重定向URL
        redirect_to = request.GET.get(REDIRECT_FIELD_NAME) or self.default_redirect_to

        # 检查回调URL是否安全，防钓鱼
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self._get_success_url_allowed_hosts(request),
            # FIXME: 如果需要考虑兼容https和http，则不能由请求是否https来决定
            require_https=request.is_secure(),
        )
        return redirect_to if url_is_safe else self.default_redirect_to

    def get(self, request, *args, **kwargs):
        """登录页面"""
        # 回调到业务系统的地址
        redirect_url = self._get_redirect_url(request)
        # 存储到当前session里，待认证成功后取出后重定向
        request.session["redirect_uri"] = redirect_url

        # TODO: 【优化】当只有一个租户且该租户有且仅有一种登录方式，且该登录方式为联邦登录，则直接重定向到第三方登录
        # 返回登录页面
        return render(request, self.template_name)


class TenantGlobalSettingRetrieveApi(View):
    def get(self, request, *args, **kwargs):
        """
        租户的全局配置，即所有租户的公共配置
        """
        global_setting = bk_user_api.get_global_setting()
        return APISuccessResponse(data=global_setting.model_dump(include={"tenant_visible"}))


class TenantListApi(View):
    def get(self, request, *args, **kwargs):
        """
        查询租户列表
        """
        # 过滤参数
        tenant_ids_str = request.GET.get("tenant_ids", "")
        tenant_ids = [i for i in tenant_ids_str.split(",") if i]

        # 无tenant_ids表示需要获取全部租户，这时候需要检查租户是否可见
        global_setting = bk_user_api.get_global_setting()
        if not tenant_ids and not global_setting.tenant_visible:
            raise error_codes.NO_PERMISSION.f(_("租户信息不可见"))

        tenants = bk_user_api.list_tenant(tenant_ids)

        return APISuccessResponse(data=[t.model_dump(include={"id", "name", "logo"}) for t in tenants])


class TenantRetrieveApi(View):
    def get(self, request, *args, **kwargs):
        """
        通过租户ID，查询单个租户信息
        """
        tenant_id = kwargs["tenant_id"]
        tenant = bk_user_api.get_tenant(tenant_id)
        if tenant is None:
            raise error_codes.OBJECT_NOT_FOUND.f(f"租户 {tenant_id} 不存在", replace=True)

        return APISuccessResponse(data=tenant.model_dump(include={"id", "name", "logo"}))


class SignInTenantCreateApi(View):
    def post(self, request, *args, **kwargs):
        """
        确认选择要登录的租户
        """
        request_body = parse_request_body_json(request.body)
        tenant_id = request_body.get("tenant_id")

        # 校验参数
        if not tenant_id:
            raise error_codes.VALIDATION_ERROR.f(_("tenant_id参数必填"))

        # 校验租户是否存在
        tenants = bk_user_api.list_tenant()
        tenant_id_set = {i.id for i in tenants}
        if tenant_id not in tenant_id_set:
            raise error_codes.OBJECT_NOT_FOUND.f(_("租户({})未找到").format(tenant_id))

        # session记录登录的租户
        request.session[SIGN_IN_TENANT_ID_SESSION_KEY] = tenant_id

        return APISuccessResponse()


class TenantIdpListApi(View):
    def get(self, request, *args, **kwargs):
        """
        获取需要登录租户的认证方式列表
        """
        # Session里获取当前登录的租户
        sign_in_tenant_id = request.session.get(SIGN_IN_TENANT_ID_SESSION_KEY)
        if not sign_in_tenant_id:
            raise error_codes.NO_PERMISSION.f(_("未选择需要登录的租户"))

        # 查询本租户配置的认证源
        idps = bk_user_api.list_idp(sign_in_tenant_id)

        return APISuccessResponse(
            data=[i.model_dump(include={"id", "name", "plugin"}) for i in idps if i.status == IdpStatus.ENABLED],
        )


class IdpBasicInfo(pydantic.BaseModel):
    """认证源基础信息"""

    id: str
    name: str
    plugin_id: str
    plugin_name: str


class PluginErrorContext(pydantic.BaseModel):
    """插件异常上下文，用于打印日志时所需的上下文信息"""

    # 插件信息
    idp: IdpBasicInfo

    action: str
    http_method: str


# 先对所有请求豁免CSRF校验，由dispatch里根据需要手动执行CSRF校验
@method_decorator(csrf_exempt, name="dispatch")
class IdpPluginDispatchView(View):
    def dispatch(self, request, *args, **kwargs):
        """
        根据路径参数 idp_id 和 action 将请求路由调度到各个插件
        """
        # Session里获取当前登录的租户
        sign_in_tenant_id = request.session.get(SIGN_IN_TENANT_ID_SESSION_KEY)
        if not sign_in_tenant_id:
            raise error_codes.NO_PERMISSION.f(_("未选择需要登录的租户"))

        # 获取参数
        idp_id = kwargs["idp_id"]
        action = kwargs["action"]
        http_method = request.method.lower()

        # 获取认证源信息
        idp = bk_user_api.get_idp(idp_id)
        # 判断是否当前登录租户所属数据源
        # TODO: 后续协同租户的数据源，需要调整判断关系
        if idp.owner_tenant_id != sign_in_tenant_id:
            raise error_codes.NO_PERMISSION.f(_("非当前登录租户所配置的认证源"))

        if idp.status != IdpStatus.ENABLED:
            raise error_codes.NO_PERMISSION.f(_("当前认证源未启用，无法通过该认证源登录"))

        #  (1) 获取插件
        try:
            plugin_cls = get_plugin_cls(idp.plugin.id)
        except NotImplementedError as error:
            raise error_codes.PLUGIN_SYSTEM_ERROR.f(
                _("认证源[{}]获取插件[{}]失败, {}").format(idp.name, idp.plugin.name, error),
            )

        # （2）初始化插件
        try:
            plugin_cfg = plugin_cls.config_class(**idp.plugin_config)
            plugin = plugin_cls(cfg=plugin_cfg)
        except pydantic.ValidationError:
            logging.exception("idp(%s) init plugin(%s) config failed", idp.id, idp.plugin.id)
            # Note: 不可将error对外，因为配置信息比较敏感
            raise error_codes.PLUGIN_SYSTEM_ERROR.f(
                _("认证源[{}]初始化插件配置[{}]失败").format(idp.name, idp.plugin.name),
            )
        except Exception as error:
            logging.exception("idp(%s) load plugin(%s) failed", idp.id, idp.plugin.id)
            raise error_codes.PLUGIN_SYSTEM_ERROR.f(
                _("认证源[{}]加载插件[{}]失败, {}").format(idp.name, idp.plugin.name, error),
            )

        idp_info = IdpBasicInfo(id=idp.id, name=idp.name, plugin_id=idp.plugin.id, plugin_name=idp.plugin.name)
        # （3）dispatch
        # FIXME: 如何对身份凭证类的认证进行手动csrf校验，或者如何添加csrf_protect装饰器
        # 身份凭证类型
        if isinstance(plugin, BaseCredentialIdpPlugin):
            return self._dispatch_credential_idp_plugin(
                plugin, request, sign_in_tenant_id, idp_info, action, http_method
            )

        # 联邦身份类型
        if isinstance(plugin, BaseFederationIdpPlugin):
            return self._dispatch_federation_idp_plugin(
                plugin, request, sign_in_tenant_id, idp_info, action, http_method
            )

        return HttpResponseNotFound()

    def wrap_plugin_error(self, context: PluginErrorContext, func: Callable, *func_args, **func_kwargs):
        """统一捕获插件异常"""
        try:
            return func(*func_args, **func_kwargs)
        except ParseRequestBodyError as e:
            raise error_codes.INVALID_ARGUMENT.f(str(e), replace=True)
        except (InvalidParamError, ValidationError) as e:
            raise error_codes.VALIDATION_ERROR.f(str(e), replace=True)
        except UnexpectedDataError as e:
            raise error_codes.UNEXPECTED_DATA_ERROR.f(str(e), replace=True)
        except Exception:
            logging.exception(
                "idp(%s) request failed, when dispatch (%s, %s) to credential idp plugin(%s)",
                context.idp.id,
                context.action,
                context.http_method,
                context.idp.plugin_id,
            )
            raise error_codes.PLUGIN_SYSTEM_ERROR.f(
                _("认证源[{}]执行插件[{}]失败, {}").format(context.idp.name, context.idp.plugin_name),
            )

    def _dispatch_credential_idp_plugin(
        self,
        plugin: BaseCredentialIdpPlugin,
        request,
        sign_in_tenant_id: str,
        idp: IdpBasicInfo,
        action: str,
        http_method: str,
    ):
        """
        身份凭证类的插件执行请求分配
        """
        dispatch_cfs = (action, http_method)
        plugin_error_context = PluginErrorContext(idp=idp, action=action, http_method=http_method)
        # 对凭证进行认证
        if dispatch_cfs == (BuiltinActionEnum.AUTHENTICATE, AllowedHttpMethodEnum.POST):
            # 认证
            user_infos = self.wrap_plugin_error(plugin_error_context, plugin.authenticate_credentials, request=request)

            # 使用认证源获得的用户信息，匹配认证出对应的租户用户列表
            tenant_users = self._auth_backend(request, sign_in_tenant_id, idp.id, user_infos)
            # 记录支持登录的租户用户
            request.session[ALLOWED_SIGN_IN_TENANT_USERS_SESSION_KEY] = tenant_users
            # 身份凭证认证直接返回成功即可，由前端重定向路由到用户列表选择页面
            return APISuccessResponse()

        return self.wrap_plugin_error(
            plugin_error_context, plugin.dispatch_extension, action=action, http_method=http_method, request=request
        )

    def _dispatch_federation_idp_plugin(
        self,
        plugin: BaseFederationIdpPlugin,
        request,
        sign_in_tenant_id: str,
        idp: IdpBasicInfo,
        action: str,
        http_method: str,
    ):
        """
        联邦认证类的插件执行请求分配
        """
        dispatch_cfs = (action, http_method)
        plugin_error_context = PluginErrorContext(idp=idp, action=action, http_method=http_method)
        # 跳转到第三方登录
        if dispatch_cfs == (BuiltinActionEnum.LOGIN, AllowedHttpMethodEnum.GET):
            callback_uri = self._get_complete_action_url(idp.id, BuiltinActionEnum.CALLBACK)
            redirect_uri = self.wrap_plugin_error(
                plugin_error_context, plugin.build_login_uri, request=request, callback_uri=callback_uri
            )

            return HttpResponseRedirect(redirect_uri)

        # 第三方登录成功后回调回蓝鲸
        # Note: 大部分都是GET重定向，对于某些第三方登录，可能存在POST请求，
        #  比如SAML的传输绑定有3种: HTTP Artifact、HTTP POST、和 HTTP Redirect
        if dispatch_cfs in [
            (BuiltinActionEnum.CALLBACK, AllowedHttpMethodEnum.GET),
            (BuiltinActionEnum.CALLBACK, AllowedHttpMethodEnum.POST),
        ]:
            # 认证
            user_info = self.wrap_plugin_error(plugin_error_context, plugin.handle_callback, request=request)

            # 使用认证源获得的用户信息，匹配认证出对应的租户用户列表
            tenant_users = self._auth_backend(request, sign_in_tenant_id, idp.id, user_info)
            # 记录支持登录的租户用户
            request.session[ALLOWED_SIGN_IN_TENANT_USERS_SESSION_KEY] = tenant_users
            # 联邦认证则重定向到前端选择账号页面
            return HttpResponseRedirect(redirect_to="page/users/")

        return self.wrap_plugin_error(
            plugin_error_context, plugin.dispatch_extension, action=action, http_method=http_method, request=request
        )

    def _get_complete_action_url(self, idp_id: str, action: str) -> str:
        """获取完整"""
        return urljoin(settings.BK_LOGIN_URL, f"auth/idps/{idp_id}/actions/{action}/")

    def _auth_backend(
        self, request, sign_in_tenant_id: str, idp_id: str, user_infos: Dict[str, Any] | List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """认证：认证源数据与数据源匹配"""
        if isinstance(user_infos, dict):
            user_infos = [user_infos]

        tenant_users = bk_user_api.list_matched_tencent_user(sign_in_tenant_id, idp_id, user_infos)
        if not tenant_users:
            raise error_codes.OBJECT_NOT_FOUND.f(
                _("认证成功，但用户在租户({})下未有对应账号").format(sign_in_tenant_id),
            )

        return [i.model_dump(include={"id", "username", "full_name"}) for i in tenant_users]


class TenantUserListApi(View):
    def get(self, request, *args, **kwargs):
        """
        用户认证后，获取认证成功后的租户用户列表
        """
        # Session里获取当前登录的租户
        sign_in_tenant_id = request.session.get(SIGN_IN_TENANT_ID_SESSION_KEY)
        if not sign_in_tenant_id:
            raise error_codes.NO_PERMISSION.f(_("未选择需要登录的租户"))

        # Session里获取已认证过的租户用户
        tenant_users = request.session.get(ALLOWED_SIGN_IN_TENANT_USERS_SESSION_KEY)
        if not tenant_users:
            raise error_codes.NO_PERMISSION.f(_("未经过用户认证步骤"))

        # TODO: 查询每个租户用户的状态

        return APISuccessResponse(data=tenant_users)


class SignInTenantUserCreateApi(View):
    def post(self, request, *args, **kwargs):
        """
        确认登录的用户，生成bk_token Cookie, 返回重定向业务系统的地址
        """
        request_body = parse_request_body_json(request.body)
        user_id = request_body.get("user_id")

        # 校验参数
        if not user_id:
            raise error_codes.VALIDATION_ERROR.f(_("user_id 参数必填"))

        tenant_users = request.session.get(ALLOWED_SIGN_IN_TENANT_USERS_SESSION_KEY) or []
        tenant_user_ids = {i["id"] for i in tenant_users}
        if user_id not in tenant_user_ids:
            raise error_codes.NO_PERMISSION.f(_("该用户不可登录"))

        # TODO：支持MFA、首次登录强制修改密码登录操作
        # TODO: 首次登录强制修改密码登录 => 设置临时场景票据，类似登录态，比如bk_token_for_force_change_password

        response = APISuccessResponse({"redirect_uri": request.session.get("redirect_uri")})
        # 生成Cookie
        bk_token, expired_at = BkTokenManager().get_bk_token(user_id)
        # 设置Cookie
        response.set_cookie(
            settings.BK_TOKEN_COOKIE_NAME,
            quote_plus(bk_token),
            expires=expired_at,
            domain=settings.BK_COOKIE_DOMAIN,
            httponly=True,
            secure=False,
        )

        # 删除Session
        request.session.clear()

        return response

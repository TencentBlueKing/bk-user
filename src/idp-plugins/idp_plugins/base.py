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
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from pydantic import BaseModel

from .constants import CUSTOM_PLUGIN_ID_PREFIX, AllowedHttpMethodEnum, BuiltinIdpPluginIDs, PluginTypeEnum
from .models import DispatchConfigItem, TestConnectionResult

logger = logging.getLogger(__name__)


class BaseIdpPlugin(ABC):
    """认证源插件基类"""

    # 插件唯一标识，比如oauth2、oidc、saml2、local，自定义插件需要以custom_为前缀
    id: str
    # 插件本身的配置类，比如OAuth2.0可能需要提供ClientID/ClientSecret等等
    config_class: Type[BaseModel]

    # 扩展请求的配置
    dispatch_configs: List[DispatchConfigItem]

    @abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    def _not_found(self, request: HttpRequest) -> HttpResponse:
        allowed_dispatch_config_message = " | ".join(
            [f"{i.http_method.upper()} {i.action}" for i in self.dispatch_configs]
        )
        return HttpResponseNotFound(f"Current Idp plugin only support: {allowed_dispatch_config_message}")

    def dispatch_extension(
        self, action: str, http_method: AllowedHttpMethodEnum, request: HttpRequest
    ) -> HttpResponse:
        """
        对于某些认证源，其需要增加扩展的请求，该方法会自动分发请求到子类实现的处理方法
        """
        dispatch_config_map = {(i.action, i.http_method): i.handler_func_name for i in self.dispatch_configs}

        if (action, http_method) in dispatch_config_map:
            handler = getattr(self, dispatch_config_map[(action, http_method)], self._not_found)
        else:
            handler = self._not_found

        return handler(request)

    @abstractmethod
    def test_connection(self) -> TestConnectionResult:
        """
        连通性测试
        主要用于产品页面填写配置信息后，测试连通性来确定配置的正确
        """
        ...


class BaseCredentialIdpPlugin(BaseIdpPlugin):
    """
    身份凭证类型的认证插件基类
    一般是需要直接提供身份凭证信息(比如账号密码、验证码等等)，然后配置在蓝鲸登录页面输入的认证方式
    """

    @abstractmethod
    def authenticate_credentials(self, request: HttpRequest) -> List[Dict[str, Any]] | Dict[str, Any]:
        """
        对身份凭证进行认证，并获得用户
        凭证可能是账号&密码、账号&验证码等等，根据不同认证插件，所需要提供的凭证不一样

        :return: 根据需要，可以返回认证成功后的单个用户的信息，也可以返回多个用户的信息
          用户字段Key后续将按照插件配置的匹配数据源用户
        """
        ...


class BaseFederationIdpPlugin(BaseIdpPlugin):
    """
    联邦身份认证源插件基类
    一般是需要重定向到第三方登录后回调，比如OAuth2.0/OIDC/SAML2.0等等
    """

    @abstractmethod
    def build_login_uri(self, request: HttpRequest, callback_uri: str) -> str:
        """
        构建跳转到第三方登录的URL
        :param request: Django View的Request, 可获取Cookie/Body/QueryParam/FormParam/Header/Session 也可以设置Session
        :param callback_uri: 一般跳转到第三方登录成功后需要回跳回来，
                            callback_uri即为回跳回来的完整地址（包括http(s)协议和url路径）
        :return: 处理后的参数后重定向到第三方登录的URI
        """
        ...

    @abstractmethod
    def handle_callback(self, request: HttpRequest) -> Dict[str, Any]:
        """
        处理第三方登录后的回调，返回登录后的用户信息
        :param request: Django View的Request, 可获取Cookie/Body/QueryParam/FormParam/Header/Session 也可以设置Session
        :return: 返回认证成功后的单个用户的信息
        """
        ...


_plugin_cls_map: Dict[str, Type[BaseCredentialIdpPlugin] | Type[BaseFederationIdpPlugin]] = {}


def register_plugin(plugin_cls: Type[BaseCredentialIdpPlugin] | Type[BaseFederationIdpPlugin]):
    """注册插件"""
    plugin_id = plugin_cls.id

    if not plugin_id:
        raise RuntimeError(f"plugin {plugin_cls} not provide id")

    if not plugin_cls.config_class:
        raise RuntimeError(f"plugin {plugin_cls} not provide config_class")

    # 非内建插件，id 必须以 custom_ 为前缀
    if plugin_id not in BuiltinIdpPluginIDs and plugin_id.startswith(CUSTOM_PLUGIN_ID_PREFIX):
        raise RuntimeError(f"custom plugin's id must start with `{CUSTOM_PLUGIN_ID_PREFIX}`")

    logger.info("register idp plugin: %s", plugin_id)

    _plugin_cls_map[plugin_id] = plugin_cls


def get_plugin_cls(plugin_id: str) -> Type[BaseCredentialIdpPlugin] | Type[BaseFederationIdpPlugin]:
    """获取指定插件类"""
    if plugin_id not in _plugin_cls_map:
        raise NotImplementedError(f"plugin {plugin_id} not implement or register")

    return _plugin_cls_map[plugin_id]


def get_plugin_cfg_cls(plugin_id: str) -> Type[BaseModel]:
    """获取指定插件的配置类"""
    return get_plugin_cls(plugin_id).config_class


def get_plugin_type(plugin_id: str) -> PluginTypeEnum:
    """获取插件类型"""
    plugin_cls = get_plugin_cls(plugin_id)

    # 身份凭证类型
    if issubclass(plugin_cls, BaseCredentialIdpPlugin):
        return PluginTypeEnum.CREDENTIAL

    # 联邦身份类型
    if issubclass(plugin_cls, BaseFederationIdpPlugin):
        return PluginTypeEnum.FEDERATION

    raise ValueError(
        f"the implementation of plugin[{plugin_id}] is wrong, "
        f"plugin class({plugin_cls.__name__}) must is a subclass of "
        f"{BaseCredentialIdpPlugin.__name__} or {BaseFederationIdpPlugin.__name__}"
    )

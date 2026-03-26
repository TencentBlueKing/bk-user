# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from typing import Any, Dict
from urllib.parse import urlencode

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from idp_plugins.base import BaseFederationIdpPlugin, BasePluginConfig
from idp_plugins.exceptions import InvalidParamError
from idp_plugins.models import TestConnectionResult
from idp_plugins.utils import generate_random_str

from .client import WeComAPIClient
from .settings import WECOM_OAUTH_URL


class WecomIdpPluginConfig(BasePluginConfig):
    sensitive_fields = ["secret"]

    corp_id: str
    agent_id: str
    secret: str


class WecomIdpPlugin(BaseFederationIdpPlugin):
    """企业微信（自建应用）认证源插件"""

    id = "wecom"

    config_class = WecomIdpPluginConfig

    def __init__(self, cfg: WecomIdpPluginConfig):
        self.cfg = cfg
        self.client = WeComAPIClient(self.cfg.corp_id, self.cfg.agent_id, self.cfg.secret)

    def test_connection(self) -> TestConnectionResult:
        # TODO: 测试调用企业微信网络是否 OK
        # TODO：测试配置信息是否正确
        raise NotImplementedError(_("不支持连通性测试"))

    @property
    def state_session_key(self) -> str:
        return f"{self.id}_state"

    def build_login_uri(self, request: HttpRequest, callback_uri: str) -> str:
        """构建跳转到企业微信地址"""
        # 防止 CSRF 攻击
        state = generate_random_str()

        params = {
            "login_type": "CorpApp",
            "appid": self.cfg.corp_id,
            "agentid": self.cfg.agent_id,
            "state": state,
            "redirect_uri": callback_uri,
        }

        # 设置 state 到 Session 里，用于回调时校验
        # FIXME: 不同认证源插件、相同认证源插件不同认证源是否会出现 SessionKey 冲突问题？？
        #  是否不应该直接提供 Django HttpRequest 呢？session set 放到外层，session key 统一前缀等等
        #  以文档方式告知插件开发者，必须自行保证长且唯一的前缀，比如可以以 {plugin_id}_xxx 为前缀
        request.session[self.state_session_key] = state

        return f"{WECOM_OAUTH_URL}?{urlencode(params)}"

    def handle_callback(self, request: HttpRequest) -> Dict[str, Any]:
        """处理第三方登录后的回调，返回登录后的用户信息"""
        # 校验 Session
        state_in_session = request.session.get(self.state_session_key)
        state = request.GET.get("state")
        if not state or state != state_in_session:
            raise InvalidParamError(_("state 参数校验不通过"))

        code = request.GET.get("code")
        if not code:
            raise InvalidParamError(_("code 参数不能为空"))

        # 通过 code 获取用户信息
        user_id = self.client.get_user_id_by_code(code)

        return {"user_id": user_id}

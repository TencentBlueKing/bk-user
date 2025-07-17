# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
import hashlib
import logging
import time
from typing import Any, Callable, Dict
from urllib.parse import urlencode

from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _

from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.weixin.constants import (
    QRCODE_EXPIRE_SECONDS,
    STATE_EXPIRE_SECONDS,
    WECHAT_API_SUCCESS_CODE,
    WECHAT_EVENT_SCAN,
    WECHAT_EVENT_SUBSCRIBE,
    WECHAT_MESSAGE_TEMPLATE,
    WECHAT_QRCODE_CREATE_URL,
    WECHAT_QRCODE_SHOW_URL,
    WECOM_LOGIN_URL,
    WECOM_USERINFO_URL,
)
from bkuser.biz.weixin.utils import WeixinUtil
from bkuser.common.error_codes import error_codes
from bkuser.component.cmsi import get_notification_client
from bkuser.component.http import http_get, http_post

logger = logging.getLogger(__name__)


class WeixinBindHandler:
    """微信绑定处理器"""

    def __init__(self, tenant_user: TenantUser, build_absolute_uri: Callable[[str], str], session: Dict):
        self.tenant_user = tenant_user
        self.build_absolute_uri = build_absolute_uri
        self.session = session
        self.weixin_config_service = WeixinConfigService(self.tenant_id)

    @property
    def tenant_id(self) -> str:
        return self.tenant_user.tenant_id

    @property
    def state_session_key(self) -> str:
        return WeixinUtil.get_state_session_key(self.tenant_user.id)

    @property
    def weixin_settings(self) -> Dict:
        return self.weixin_config_service.get_weixin_settings()

    def get_bind_info(self) -> Dict[str, Any]:
        """获取绑定微信所需的信息 - 根据微信类型返回不同的绑定信息"""
        if self.weixin_settings["wx_type"] in ["qy", "qywx"]:
            return self._get_wecom_bind_info()
        if self.weixin_settings["wx_type"] == "mp":
            return self._get_weixin_bind_info()
        raise error_codes.WEIXIN_CONFIG_NOT_FOUND.f(_("不支持的微信类型"))

    def _get_wecom_bind_info(self) -> Dict[str, Any]:
        """获取企业微信绑定信息"""
        redirect_uri = self.build_absolute_uri(
            reverse(
                "personal_center.tenant_users.wecom.login_callback", kwargs={"tenant_id": self.tenant_user.tenant_id}
            )
        )

        state = self._generate_and_store_state()
        param_dict = {
            "login_type": "CorpApp",
            "appid": self.weixin_settings.get("corp_id"),
            "agentid": self.weixin_settings.get("agent_id"),
            "redirect_uri": redirect_uri,
            "state": state,
        }

        bind_url = "%s?%s" % (WECOM_LOGIN_URL, urlencode(param_dict))

        return {
            "bind_type": "wecom",
            "bind_url": bind_url,
        }

    def _get_weixin_bind_info(self) -> Dict[str, Any]:
        """获取微信公众号绑定信息"""
        return {
            "bind_type": "weixin",
            "bind_url": self._get_mp_qrcode_url(),
        }

    def _generate_and_store_state(self) -> str:
        """生成并存储 state 到 session"""
        # 生成唯一的 state
        state = WeixinUtil.generate_state()

        state_data = WeixinUtil.create_state_data(state, self.tenant_user.id)
        session_key = self.state_session_key
        self.session[session_key] = state_data

        return state

    def check_state(self, state: str) -> bool:
        """检查 state 是否合法，state 有效期为 5 分钟"""
        session_key = self.state_session_key
        # 从 session 中获取 state 数据
        state_data = self.session.get(session_key)
        current_time = int(time.time())

        if not state_data:
            return False
        if state_data.get("state") != state:
            return False
        if current_time - state_data.get("timestamp", 0) >= STATE_EXPIRE_SECONDS:
            return False

        # 清理 state 数据
        self._cleanup_state()
        return True

    def _cleanup_state(self):
        """清理 session 中的 state 数据"""
        session_key = self.state_session_key
        if session_key in self.session:
            del self.session[session_key]

    def get_wecom_userid(self, code: str) -> str:
        access_token = self.weixin_config_service.get_access_token()

        params = {"access_token": access_token, "code": code}

        success, data = http_get(WECOM_USERINFO_URL, params=params)
        if not success:
            logger.exception("Failed to get wecom userid: %s", data.get("error"))
            raise error_codes.WEIXIN_API_ERROR.f(_("获取企业微信用户信息失败"))

        # 检查企业微信 API 返回的错误码
        if data.get("errcode") != WECHAT_API_SUCCESS_CODE:
            logger.exception("Wecom API error: %s (errcode: %s)", data.get("errmsg"), data.get("errcode"))
            raise error_codes.WEIXIN_API_ERROR.f(_("企业微信 API 调用失败：{}").format(data.get("errmsg")))
        return data.get("userid")

    def bind_user(self, wx_userid: str) -> None:
        """绑定用户"""
        self.tenant_user.wx_userid = wx_userid
        self.tenant_user.save(update_fields=["wx_userid", "updated_at"])

    def _get_mp_qrcode_url(self) -> str:
        """创建微信临时二维码"""
        params = {"access_token": self.weixin_config_service.get_access_token()}
        data = {
            "action_name": "QR_SCENE",
            "expire_seconds": QRCODE_EXPIRE_SECONDS,  # 5 分钟
            "action_info": {
                "scene": {
                    "scene_id": 1,
                }
            },
        }
        success, data = http_post(WECHAT_QRCODE_CREATE_URL, params=params, data=data)
        if not success:
            logger.exception("Failed to create wecom temporary QR code")
            raise error_codes.WEIXIN_QRCODE_CREATE_FAILED.f(_("创建微信临时二维码失败"))

        if data.get("errcode") != WECHAT_API_SUCCESS_CODE:
            logger.exception("WeChat API error: %s (errcode: %s)", data.get("errmsg"), data.get("errcode"))
            raise error_codes.WEIXIN_API_ERROR.f(_("微信公众号 API 调用失败：{}").format(data.get("errmsg")))

        # 获取 ticket
        ticket = str(data.get("ticket"))

        # 将用户信息与 ticket 关联存储到缓存中
        # 默认缓存过期时间为 300 秒（与二维码过期时间保持一致)
        WeixinUtil.store_qrcode_user_info(ticket, self.tenant_user.id)
        logger.info("Successfully created WeCom temporary QR code, ticket: %s", ticket)
        return "%s?%s" % (
            WECHAT_QRCODE_SHOW_URL,
            urlencode({"ticket": ticket}),
        )

    def handle_qrcode_event(self, data: Dict) -> str:
        """处理微信公众号 扫码/订阅 事件"""
        msg_type = data.get("MsgType")
        from_user = data.get("FromUserName")
        to_user = data.get("ToUserName")
        event = data.get("Event")
        if not all([msg_type, from_user, event, to_user]):
            return ""
        if msg_type != "event" or event not in (WECHAT_EVENT_SUBSCRIBE, WECHAT_EVENT_SCAN):
            return ""
        self.bind_user(str(from_user))

        return WECHAT_MESSAGE_TEMPLATE.format(
            to_user=to_user, from_user=from_user, create_time=int(time.time()), content=_("绑定成功")
        )


class WeixinConfigService:
    """微信配置服务"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.client = get_notification_client(self.tenant_id)

    def get_weixin_settings(self) -> Dict:
        return self.client.get_weixin_settings()

    def get_access_token(self) -> str:
        return self.client.get_weixin_token()["access_token"]

    def check_sign(self, signature: str, timestamp: str, nonce: str) -> bool:
        """
        微信服务器回调后的签名认证
        """
        # 获取 token
        settings = self.get_weixin_settings()
        token = settings.get("wx_token")
        if not token:
            return False

        # 1. 字典序排序
        params = [token, timestamp, nonce]
        params.sort()
        # 2. 拼接字符串
        s = "".join(params)
        # 3. 使用 sha1 加密
        hashcode = hashlib.sha1(force_bytes(s)).hexdigest()

        return hashcode == signature

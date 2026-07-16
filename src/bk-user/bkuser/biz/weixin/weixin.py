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
import hashlib
import logging
import time
from typing import Dict, Tuple
from urllib.parse import urlencode

from defusedxml import ElementTree
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel

from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.weixin.constants import (
    MP_EVENT_SCAN,
    MP_EVENT_SUBSCRIBE,
    MP_MESSAGE_TEMPLATE,
    MP_QRCODE_CREATE_URL,
    MP_QRCODE_EXPIRE_SECONDS,
    MP_QRCODE_SHOW_URL,
    WECOM_LOGIN_URL,
    WECOM_USERINFO_URL,
    WeixinTypeEnum,
)
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum
from bkuser.common.error_codes import error_codes
from bkuser.component.cmsi import get_notification_client
from bkuser.component.http import http_get, http_post
from bkuser.utils.url import urljoin
from bkuser.utils.uuid import generate_uuid

logger = logging.getLogger(__name__)


class WeComConfig(BaseModel):
    """企业微信配置"""

    corp_id: str
    corp_secret: str
    agent_id: str


class MpConfig(BaseModel):
    """微信公众号配置"""

    wx_app_id: str
    wx_secret: str
    wx_token: str


class WeixinConfigProvider:
    """微信配置提供者"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.client = get_notification_client(self.tenant_id)

    def _get_weixin_config(self) -> WeComConfig | MpConfig | None:
        cfg = self.client.get_weixin_settings()
        wx_type = cfg["wx_type"]

        # 校验企业微信配置的完整性
        if wx_type in ["qy", "qywx"] and all([cfg.get("corp_id"), cfg.get("corp_secret"), cfg.get("agent_id")]):
            return WeComConfig(**cfg)

        # 校验微信公众号配置的完整性
        if wx_type == "mp" and all([cfg.get("wx_app_id"), cfg.get("wx_secret"), cfg.get("wx_token")]):
            return MpConfig(**cfg)

        return None

    def get_wx_type(self) -> str:
        cfg = self._get_weixin_config()

        if isinstance(cfg, WeComConfig):
            return WeixinTypeEnum.WeCom.value

        if isinstance(cfg, MpConfig):
            return WeixinTypeEnum.MP.value

        return ""

    def get_wecom_config(self) -> WeComConfig:
        cfg = self._get_weixin_config()
        # Note: 调用方只有明确是企业微信后，才能获取到对应的配置
        assert isinstance(cfg, WeComConfig)
        return cfg

    def get_mp_config(self) -> MpConfig:
        cfg = self._get_weixin_config()
        # Note: 调用方只有明确是微信公众号后，才能获取到对应的配置
        assert isinstance(cfg, MpConfig)
        return cfg

    def get_access_token(self) -> str:
        """获取 access_token"""
        return self.client.get_weixin_token()["access_token"]


class WecomBindHandler:
    """企业微信绑定处理器"""

    def __init__(self, tenant_user: TenantUser):
        self.tenant_user = tenant_user
        self.tenant_id = tenant_user.tenant_id

        self.cfg_provider = WeixinConfigProvider(self.tenant_id)
        self.cfg = self.cfg_provider.get_wecom_config()

        self.state_session_key = f"wecom_bind_state_{self.tenant_user.id}"

    def get_authorization_url(self, session: Dict) -> str:
        """获取企业微信授权地址"""
        redirect_uri = urljoin(
            settings.BK_USER_URL, f"/api/v3/web/personal-center/weixin/tenants/{self.tenant_id}/wecom/bind-callback/"
        )

        # 生成唯一的 state
        state = generate_uuid()
        # 存储 state 到 session
        session[self.state_session_key] = state

        params = {
            "login_type": "CorpApp",
            "appid": self.cfg.corp_id,
            "agentid": self.cfg.agent_id,
            "redirect_uri": redirect_uri,
            "state": state,
        }

        return "%s?%s" % (WECOM_LOGIN_URL, urlencode(params))

    def check_state(self, state: str, session: Dict) -> bool:
        """检查 state 是否合法"""
        # 从 session 中获取 state 数据并对比
        if session.get(self.state_session_key) != state:
            return False

        # 清理 state 数据
        del session[self.state_session_key]

        return True

    def get_wecom_userid(self, code: str) -> str:
        """获取企业微信用户 ID"""
        params = {"access_token": self.cfg_provider.get_access_token(), "code": code}

        ok, data = http_get(WECOM_USERINFO_URL, params=params)
        if not ok:
            logger.error("get wecom userid api failed, user: %s, error: %s", self.tenant_user.id, data.get("error"))
            raise error_codes.WEIXIN_API_ERROR.f(_("获取企业微信用户信息失败"))

        # 检查企业微信 API 返回的错误码
        if data.get("errcode") != 0:
            logger.error(
                "get wecom userid api error, user: %s, errmsg: %s, errcode: %s",
                self.tenant_user.id,
                data.get("errmsg"),
                data.get("errcode"),
            )
            raise error_codes.WEIXIN_API_ERROR.f(_("企业微信 API 调用失败：{}").format(data.get("errmsg")))

        return data["userid"]


class MpBindHandler:
    """微信公众号绑定处理器"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

        self.cfg_provider = WeixinConfigProvider(self.tenant_id)
        self.cfg = self.cfg_provider.get_mp_config()

        self.qrcode_cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.MP_QRCODE)

    def get_mp_qrcode_url(self, tenant_user: TenantUser) -> str:
        """创建微信临时二维码"""
        params = {"access_token": self.cfg_provider.get_access_token()}
        data = {
            "action_name": "QR_SCENE",
            "expire_seconds": MP_QRCODE_EXPIRE_SECONDS,  # 5 分钟
            "action_info": {
                "scene": {
                    "scene_id": 1,
                }
            },
        }
        ok, data = http_post(MP_QRCODE_CREATE_URL, params=params, data=data)
        if not ok:
            logger.error(
                "create wecom temporary qrcode api failed, user: %s, error: %s", tenant_user.id, data.get("error")
            )
            raise error_codes.WEIXIN_QRCODE_CREATE_FAILED.f(_("创建微信临时二维码失败"))

        if data.get("errcode") != 0:
            logger.error(
                "create wecom temporary qrcode api failed, user: %s, errmsg:%s, errcode: %s",
                tenant_user.id,
                data.get("errmsg"),
                data.get("errcode"),
            )
            raise error_codes.WEIXIN_API_ERROR.f(_("微信公众号 API 调用失败：{}").format(data.get("errmsg")))

        # 获取 ticket
        ticket = str(data.get("ticket") or "")

        # 将用户信息与 ticket 关联存储到缓存中
        # 缓存过期时间为 300 秒（与二维码过期时间保持一致)
        self.qrcode_cache.set(ticket, {"tenant_user_id": tenant_user.id}, 300)

        logger.info("successfully created mp temporary qrcode, ticket: %s", ticket)
        return "%s?%s" % (MP_QRCODE_SHOW_URL, urlencode({"ticket": ticket}))

    def check_mp_signature(self, signature: str, timestamp: str, nonce: str) -> bool:
        if not all([signature, timestamp, nonce]):
            return False

        # 获取微信 token
        wx_token = self.cfg.wx_token
        if not wx_token:
            return False

        # 1. 字典序排序
        params = [wx_token, timestamp, nonce]
        params.sort()
        # 2. 拼接字符串
        s = "".join(params)
        # 3. 使用 sha1 加密
        hashcode = hashlib.sha1(force_bytes(s)).hexdigest()

        return hashcode == signature

    def process_mp_callback_event(self, event_content: str) -> Tuple[TenantUser | None, str, str]:
        """从事件内容中解析并获取租户用户

        Returns:
            Tuple: 包含以下字段的元组：
                - tenantUser (TenantUser): 租户用户
                - wx_userid (str): 微信 ID
                - response (str): 需要返回给微信公众号的 XML 数据
        """
        # 解析微信公众号推送的 XML 消息
        data = self._xml_to_dict(event_content)

        msg_type = data.get("MsgType")
        from_user = data.get("FromUserName")
        to_user = data.get("ToUserName")
        event = data.get("Event")
        # 检查必要的字段
        if not all([msg_type, from_user, event, to_user]):
            return None, "", ""
        # 检查事件类型
        if msg_type != "event" or event not in (MP_EVENT_SUBSCRIBE, MP_EVENT_SCAN):
            return None, "", ""

        # 根据 ticket 获取租户用户
        ticket = str(data.get("Ticket") or "")
        tenant_user = self._get_tenant_user_by_ticket(ticket)
        response = MP_MESSAGE_TEMPLATE.format(
            from_user=from_user, to_user=to_user, create_time=int(time.time()), content=_("绑定成功")
        )
        return tenant_user, str(from_user), response

    def _get_tenant_user_by_ticket(self, ticket: str) -> TenantUser:
        """通过 ticket 获取到对应的 tenant_user 对象"""
        user_info = self.qrcode_cache.get(ticket)
        if not user_info:
            logger.warning("tenant user not found for ticket: %s", ticket)
            raise error_codes.WEIXIN_QRCODE_TICKET_INVALID.f(_("微信二维码 ticket 无效或已过期"))

        tenant_user_id = user_info["tenant_user_id"]
        # 获取成功后删除缓存，避免重复使用
        self.qrcode_cache.delete(ticket)

        logger.info("successfully retrieved tenant_user by ticket: %s", tenant_user_id)

        return TenantUser.objects.get(id=tenant_user_id)

    @staticmethod
    def _xml_to_dict(xml_data: str) -> Dict:
        """xml 数据转为 dict 数据"""
        try:
            root = ElementTree.fromstring(xml_data)
            return {child.tag: child.text for child in root}
        except ElementTree.ParseError:
            logger.exception("XML parse failed, xml_data: %s", xml_data)
            raise error_codes.WEIXIN_XML_PARSE_FAILED

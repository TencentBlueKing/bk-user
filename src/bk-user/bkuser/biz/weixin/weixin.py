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
from typing import Dict, Tuple
from urllib.parse import urlencode

from defusedxml import ElementTree
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _

from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.weixin.constants import (
    MP_EVENT_SCAN,
    MP_EVENT_SUBSCRIBE,
    MP_MESSAGE_TEMPLATE,
    MP_QRCODE_CREATE_URL,
    MP_QRCODE_EXPIRE_SECONDS,
    MP_QRCODE_SHOW_URL,
    WECOM_LOGIN_URL,
    WECOM_STATE_EXPIRE_SECONDS,
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


class WecomBindHandler:
    """企业微信绑定处理器"""

    def __init__(self, tenant_user: TenantUser):
        self.tenant_user = tenant_user
        self.weixin_config_service = WeixinConfigService(self.tenant_id)

    @property
    def state_session_key(self) -> str:
        """获取 state session key"""
        return f"wecom_bind_state_{self.tenant_user.id}"

    @property
    def tenant_id(self) -> str:
        return self.tenant_user.tenant_id

    def get_authorization_url(self, session: Dict) -> str:
        """获取企业微信授权地址"""
        redirect_uri = urljoin(
            settings.BK_USER_URL, f"/api/v1/web/personal-center/weixin/tenants/{self.tenant_id}/wecom/bind-callback/"
        )

        state = self._generate_and_store_state(session)
        corp_id = self.weixin_config_service.get_corp_id()
        if not corp_id:
            logger.exception("Failed to get corp_id for tenant %s", self.tenant_id)
            raise error_codes.WEIXIN_CONFIG_NOT_FOUND.f(_("无法获取企业微信配置中的 corp_id"))
        param_dict = {
            "login_type": "CorpApp",
            "appid": self.weixin_config_service.get_corp_id(),
            "redirect_uri": redirect_uri,
            "state": state,
        }

        return "%s?%s" % (WECOM_LOGIN_URL, urlencode(param_dict))

    def check_state(self, state: str, session: Dict) -> bool:
        """检查 state 是否合法，state 有效期为 5 分钟"""
        session_key = self.state_session_key
        # 从 session 中获取 state 数据
        state_data = session.get(session_key)
        current_time = int(time.time())

        if not state_data:
            return False
        if state_data.get("state") != state:
            return False
        if current_time - state_data.get("timestamp", 0) >= WECOM_STATE_EXPIRE_SECONDS:
            return False

        # 清理 state 数据
        self._cleanup_state(session)
        return True

    def get_wecom_userid(self, code: str) -> str:
        """获取企业微信用户ID"""
        access_token = self.weixin_config_service.get_access_token()

        params = {"access_token": access_token, "code": code}

        success, data = http_get(WECOM_USERINFO_URL, params=params)
        if not success:
            logger.exception("Failed to get wecom userid: %s", data.get("error"))
            raise error_codes.WEIXIN_API_ERROR.f(_("获取企业微信用户信息失败"))

        # 检查企业微信 API 返回的错误码
        if data.get("errcode") != 0:
            logger.exception("Wecom API error: %s (errcode: %s)", data.get("errmsg"), data.get("errcode"))
            raise error_codes.WEIXIN_API_ERROR.f(_("企业微信 API 调用失败：{}").format(data.get("errmsg")))
        return data.get("userid")

    def _generate_and_store_state(self, session: Dict) -> str:
        """生成并存储 state 到 session"""
        # 生成唯一的 state
        state = self._generate_state()

        state_data = self._create_state_data(state, self.tenant_user.id)
        session_key = self.state_session_key
        session[session_key] = state_data

        return state

    def _cleanup_state(self, session: Dict):
        """清理 session 中的 state 数据"""
        session_key = self.state_session_key
        if session_key in session:
            del session[session_key]

    @staticmethod
    def _generate_state() -> str:
        """生成唯一的 state"""
        return generate_uuid()

    @staticmethod
    def _create_state_data(state: str, tenant_user_id: str) -> Dict:
        """创建 state 数据"""
        return {"state": state, "tenant_user_id": tenant_user_id, "timestamp": int(time.time())}


class MpBindHandler:
    """微信公众号绑定处理器"""

    def __init__(self, tenant_user: TenantUser):
        self.tenant_user = tenant_user
        self.weixin_config_service = WeixinConfigService(self.tenant_id)

    @property
    def tenant_id(self) -> str:
        return self.tenant_user.tenant_id

    def get_mp_qrcode_url(self) -> str:
        """创建微信临时二维码"""
        params = {"access_token": self.weixin_config_service.get_access_token()}
        data = {
            "action_name": "QR_SCENE",
            "expire_seconds": MP_QRCODE_EXPIRE_SECONDS,  # 5 分钟
            "action_info": {
                "scene": {
                    "scene_id": 1,
                }
            },
        }
        success, data = http_post(MP_QRCODE_CREATE_URL, params=params, data=data)
        if not success:
            logger.exception("Failed to create wecom temporary QR code")
            raise error_codes.WEIXIN_QRCODE_CREATE_FAILED.f(_("创建微信临时二维码失败"))

        if data.get("errcode") != 0:
            logger.exception("WeChat API error: %s (errcode: %s)", data.get("errmsg"), data.get("errcode"))
            raise error_codes.WEIXIN_API_ERROR.f(_("微信公众号 API 调用失败：{}").format(data.get("errmsg")))

        # 获取 ticket
        ticket = str(data.get("ticket"))

        # 将用户信息与 ticket 关联存储到缓存中
        user_info = {"tenant_user_id": self.tenant_user.id}
        qrcode_cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.MP_QRCODE)
        # 缓存过期时间为 300 秒（与二维码过期时间保持一致)
        qrcode_cache.set(ticket, user_info, 300)

        logger.info("Successfully created MP temporary QR code, ticket: %s", ticket)
        return "%s?%s" % (
            MP_QRCODE_SHOW_URL,
            urlencode({"ticket": ticket}),
        )

    @staticmethod
    def check_mp_signature(tenant_id: str, signature: str, timestamp: str, nonce: str) -> bool:
        if not all([signature, timestamp, nonce]):
            return False

        # 获取微信 token
        wx_token = WeixinConfigService(tenant_id).get_wx_token()
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

    @staticmethod
    def process_mp_callback_event(event_content: str) -> Tuple[TenantUser | None, str, str]:
        """从事件内容中解析并获取租户用户

        Returns:
            Tuple: 包含以下字段的元组：
                - tenantUser (TenantUser): 租户用户
                - wx_userid (str): 微信 ID
                - response (str): 需要返回给微信公众号的 XML 数据
        """
        # 解析微信公众号推送的 XML 消息
        data = MpBindHandler._xml_to_dict(event_content)

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
        ticket = str(data.get("Ticket"))
        tenant_user = MpBindHandler._get_tenant_user_by_ticket(ticket)
        response = MP_MESSAGE_TEMPLATE.format(
            from_user=from_user, to_user=to_user, createtime=int(time.time()), content=_("绑定成功")
        )
        return tenant_user, str(from_user), response

    @staticmethod
    def _get_tenant_user_by_ticket(ticket: str) -> TenantUser:
        """通过 ticket 获取到对应的 tenant_user 对象"""
        qrcode_cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.MP_QRCODE)
        user_info = qrcode_cache.get(ticket)
        if not user_info:
            logger.warning("Tenant User not found for ticket: %s", ticket)
            raise error_codes.WEIXIN_QRCODE_TICKET_INVALID.f(_("微信二维码 ticket 无效或已过期"))

        tenant_user_id = user_info.get("tenant_user_id")

        try:
            tenant_user = TenantUser.objects.get(id=tenant_user_id)
        except TenantUser.DoesNotExist:
            logger.exception("TenantUser with id %s does not exist", tenant_user_id)
            qrcode_cache.delete(ticket)
            raise error_codes.WEIXIN_QRCODE_TICKET_INVALID.f(_("微信二维码对应的用户不存在"))

        # 获取成功后删除缓存，避免重复使用
        qrcode_cache.delete(ticket)
        logger.info("Successfully retrieved tenant_user by ticket: %s", tenant_user_id)
        return tenant_user

    @staticmethod
    def _xml_to_dict(xml_data: str) -> Dict:
        """xml 数据转为 dict 数据"""
        try:
            root = ElementTree.fromstring(xml_data)
            result = {}
            for child in root:
                result[child.tag] = child.text
            return result
        except ElementTree.ParseError:
            logger.exception("XML parse failed")
            raise error_codes.WEIXIN_XML_PARSE_FAILED


class WeixinConfigService:
    """微信配置服务"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.client = get_notification_client(self.tenant_id)

    def _get_weixin_settings(self) -> Dict | None:
        weixin_settings = self.client.get_weixin_settings()
        wx_type = weixin_settings["wx_type"]

        if not wx_type:
            logger.warning("wx_type is missing in weixin settings")
            return None
        if wx_type not in [WeixinTypeEnum.QY, WeixinTypeEnum.QYWX, WeixinTypeEnum.MP]:
            logger.warning("wx_type is not correct in weixin settings")
            return None

        if wx_type in [WeixinTypeEnum.QY, WeixinTypeEnum.QYWX] and not self._validate_wecom_config(weixin_settings):
            return None
        if wx_type == WeixinTypeEnum.MP and not self._validate_mp_config(weixin_settings):
            return None

        return weixin_settings

    @staticmethod
    def _validate_wecom_config(weixin_settings: Dict) -> bool:
        """校验企业微信配置的完整性"""
        required_fields = ["corp_id", "corp_secret"]
        return all(weixin_settings.get(field) for field in required_fields)

    @staticmethod
    def _validate_mp_config(weixin_settings: Dict) -> bool:
        """校验微信公众号配置的完整性"""
        required_fields = ["wx_app_id", "wx_secret", "wx_token"]
        return all(weixin_settings.get(field) for field in required_fields)

    def get_wx_type(self) -> WeixinTypeEnum | None:
        weixin_settings = self._get_weixin_settings()
        if weixin_settings is None:
            return None
        return WeixinTypeEnum(weixin_settings["wx_type"])

    def get_wx_token(self) -> str | None:
        """获取微信公众号配置的 token"""
        weixin_settings = self._get_weixin_settings()
        if weixin_settings is None:
            return None
        if weixin_settings["wx_type"] != WeixinTypeEnum.MP:
            return None
        return weixin_settings["wx_token"]

    def get_corp_id(self) -> str | None:
        weixin_settings = self._get_weixin_settings()
        if weixin_settings is None or self.get_wx_type() not in [WeixinTypeEnum.QY, WeixinTypeEnum.QYWX]:
            return None
        return weixin_settings["corp_id"]

    def get_access_token(self) -> str:
        """获取 access_token"""
        return self.client.get_weixin_token()["access_token"]

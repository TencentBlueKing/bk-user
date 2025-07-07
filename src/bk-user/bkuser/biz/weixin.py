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
import uuid
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from bkuser.apps.tenant.models import TenantUser
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum
from bkuser.common.error_codes import error_codes
from bkuser.component.cmsi import NotificationClient, get_notification_client
from bkuser.component.http import http_get, http_post

logger = logging.getLogger(__name__)

# 企业微信扫码登录 state 过期时间，单位：秒
STATE_EXPIRE_SECONDS = 300


class WeixinBindHandler:
    """微信绑定处理器"""

    def __init__(self, tenant_user: TenantUser, request: HttpRequest):
        self.tenant_user = tenant_user
        self.request = request
        self.weixin_config_service = WeixinConfigService(self.tenant_id)

    @property
    def tenant_id(self) -> str:
        return self.tenant_user.tenant_id

    @property
    def state_session_key(self) -> str:
        """state 的 session 键名"""
        return f"wecom_bind_state_{self.tenant_id}_{self.tenant_user.id}"

    @property
    def weixin_settings(self) -> Dict:
        return self.weixin_config_service.get_weixin_settings()

    @property
    def wx_type(self) -> str:
        return self.weixin_settings.get("wx_type", "")

    def get_bind_info(self) -> Dict[str, Any]:
        """获取绑定微信所需的信息 - 根据微信类型返回不同的绑定方式"""
        if self.wx_type in ["qy", "qywx"]:
            return self._get_wecom_bind_info()
        if self.wx_type == "mp":
            return self._get_mp_bind_info()
        raise error_codes.WEIXIN_CONFIG_NOT_FOUND.f(_("不支持的微信类型"))

    def _get_wecom_bind_info(self) -> Dict[str, Any]:
        """获取企业微信绑定信息"""
        redirect_uri = self.request.build_absolute_uri(
            reverse(
                "personal_center.tenant_users.wecom.login_callback", kwargs={"tenant_id": self.tenant_user.tenant_id}
            )
        )

        state = self._generate_and_store_state()
        param_dict = {
            "login_type": "CorpApp",
            "appid": self.weixin_settings.get("corp_id"),
            "agentid": self.weixin_settings.get("agentid"),
            "redirect_uri": redirect_uri,
            "state": state,
        }

        login_url = "%s?%s" % ("https://login.work.weixin.qq.com/wwlogin/sso/login", urlencode(param_dict))

        return {
            "bind_type": "wecom",
            "login_url": login_url,
        }

    def _get_mp_bind_info(self) -> Dict[str, Any]:
        """获取微信公众号绑定信息"""
        return {
            "bind_type": "mp",
            "login_url": self._get_mp_qrcode_url(),
        }

    def _generate_and_store_state(self) -> str:
        """生成并存储 state 到 session"""
        # 生成唯一的 state
        state = str(uuid.uuid4())

        state_data = {"state": state, "tenant_user_id": self.tenant_user.id, "timestamp": int(time.time())}
        session_key = self.state_session_key
        self.request.session[session_key] = state_data

        return state

    def check_state(self, state: str) -> bool:
        """检查 state 是否合法，state 有效期为 5 分钟"""
        session_key = self.state_session_key
        # 从 session 中获取 state 数据
        state_data = self.request.session.get(session_key)
        if not state_data:
            return False
        if state_data.get("state") != state:
            return False
        if int(time.time()) - state_data.get("timestamp") >= STATE_EXPIRE_SECONDS:
            return False

        # 清理 state 数据
        self._cleanup_state()
        return True

    def _cleanup_state(self):
        """清理 session 中的 state 数据"""
        session_key = self.state_session_key
        if session_key in self.request.session:
            del self.request.session[session_key]

    def get_wecom_userid(self, code: str) -> str:
        url = "https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo"
        access_token = self.weixin_config_service.get_access_token()

        params = {"access_token": access_token, "code": code}

        success, data = http_get(url, params=params)
        if not success:
            logger.exception("Failed to get wecom userid: %s", data.get("error"))
            raise error_codes.WEIXIN_API_ERROR.f(_("获取企业微信用户信息失败"))

        # 检查企业微信 API 返回的错误码
        if data.get("errcode") != 0:
            logger.exception("Wecom API error: %s (errcode: %s)", data.get("errmsg"), data.get("errcode"))
            raise error_codes.WEIXIN_API_ERROR.f(_("企业微信 API 调用失败：{}").format(data.get("errmsg")))
        return data.get("userid")

    def bind_user(self, wx_userid: str) -> None:
        """绑定用户"""
        self.tenant_user.wx_userid = wx_userid
        self.tenant_user.save(update_fields=["wx_userid", "updated_at"])

    def _get_mp_qrcode_url(self) -> str:
        """创建微信临时二维码"""
        url = "https://api.weixin.qq.com/cgi-bin/qrcode/create"
        params = {"access_token": self.weixin_config_service.get_access_token()}
        data = {
            "action_name": "QR_SCENE",
            "expire_seconds": 7200,  # 2 小时
            "action_info": {
                "scene": {
                    "scene_id": 1,
                }
            },
        }
        success, data = http_post(url, params=params, data=data)
        if not success:
            logger.exception("Failed to create wecom temporary QR code")
            raise error_codes.WEIXIN_QRCODE_CREATE_FAILED.f(_("创建微信临时二维码失败"))

        if data.get("errcode") != 0:
            logger.exception("WeChat API error: %s (errcode: %s)", data.get("errmsg"), data.get("errcode"))
            raise error_codes.WEIXIN_API_ERROR.f(_("微信公众号 API 调用失败：{}").format(data.get("errmsg")))

        # 获取 ticket
        ticket = str(data.get("ticket"))

        # 将用户信息与 ticket 关联存储到缓存中
        # 默认缓存过期时间为 7200 秒（与二维码过期时间保持一致)
        WeixinConfigService.store_qrcode_user_info(ticket, self.tenant_user.id)
        logger.info("Successfully created WeCom temporary QR code, ticket: %s", ticket)
        return "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s" % ticket

    def handle_qrcode_event(self, data: Dict) -> str:
        """处理微信公众号扫码事件"""
        tpl = """
                <xml>
                <ToUserName><![CDATA[{to_user}]]></ToUserName>
                <FromUserName><![CDATA[{from_user}]]></FromUserName>
                <CreateTime>{create_time}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{content}]]></Content>
                </xml>"""
        msg_type = data.get("MsgType")
        from_user = data.get("FromUserName")
        to_user = data.get("ToUserName")
        event = data.get("Event")
        if not any([msg_type, from_user, event, to_user]):
            return ""
        if msg_type != "event" or event not in ("subscribe", "SCAN"):
            return ""
        self.bind_user(str(from_user))

        return tpl.format(to_user=to_user, from_user=from_user, create_time=int(time.time()), content=_("绑定成功"))


class WeixinConfigService:
    """微信配置服务"""

    qrcode_cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.WEIXIN_QRCODE)

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self._client: Optional[NotificationClient] = None

    @property
    def client(self) -> NotificationClient:
        if not self._client:
            self._client = get_notification_client(self.tenant_id)
        return self._client

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
        hashcode = hashlib.sha1(s.encode("utf-8")).hexdigest()

        return hashcode == signature

    @staticmethod
    def xml_to_dict(xml_data: str) -> Dict:
        """纯工具方法，保持静态或者抽离出来🤔"""
        try:
            root = ET.fromstring(xml_data)
            result = {}
            for child in root:
                result[child.tag] = child.text
            return result
        except ET.ParseError:
            logger.exception("XML parse failed")
            raise error_codes.WEIXIN_XML_PARSE_FAILED.f(_("XML 解析失败"))

    @classmethod
    def get_tenant_user_by_ticket(cls, ticket: str) -> TenantUser:
        """通过 ticket 获取到对应的 tenant_user 对象"""
        user_info = cls.qrcode_cache.get(ticket)
        if not user_info:
            logger.warning("Tenant User not found for ticket: %s", ticket)
            raise error_codes.WEIXIN_QRCODE_TICKET_INVALID.f(_("微信二维码 ticket 无效或已过期"))

        tenant_user_id = user_info.get("tenant_user_id")
        tenant_user = TenantUser.objects.get(id=tenant_user_id)
        # 获取成功后删除缓存，避免重复使用
        cls.qrcode_cache.delete(ticket)
        logger.info("Successfully retrieved tenant_user by ticket: %s", tenant_user_id)
        return tenant_user

    @classmethod
    def store_qrcode_user_info(cls, ticket: str, tenant_user_id: str, timeout: int = 7200) -> None:
        """存储二维码用户信息到缓存"""
        user_info = {"tenant_user_id": tenant_user_id, "created_at": int(time.time())}
        cls.qrcode_cache.set(ticket, user_info, timeout=timeout)

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
from typing import Dict

from defusedxml import ElementTree
from django.utils.translation import gettext_lazy as _

from bkuser.apps.tenant.models import TenantUser
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum
from bkuser.common.error_codes import error_codes
from bkuser.utils.uuid import generate_uuid

logger = logging.getLogger(__name__)


class WeixinUtil:
    qrcode_cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.WEIXIN_QRCODE)

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
    def store_qrcode_user_info(cls, ticket: str, tenant_user_id: str, timeout: int = 300) -> None:
        """存储二维码用户信息到缓存"""
        user_info = {"tenant_user_id": tenant_user_id}
        cls.qrcode_cache.set(ticket, user_info, timeout)

    @staticmethod
    def xml_to_dict(xml_data: str) -> Dict:
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

    @staticmethod
    def check_weixin_signature(token: str, signature: str, timestamp: str, nonce: str) -> bool:
        """
        微信服务器回调后的签名认证
        """
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
    def generate_state() -> str:
        """生成唯一的 state"""
        return generate_uuid()

    @staticmethod
    def get_state_session_key(tenant_user_id: str) -> str:
        """获取 state session key"""
        return f"wecom_bind_state_{tenant_user_id}"

    @staticmethod
    def create_state_data(state: str, tenant_user_id: str) -> Dict:
        """创建 state 数据"""
        return {"state": state, "tenant_user_id": tenant_user_id, "timestamp": int(time.time())}

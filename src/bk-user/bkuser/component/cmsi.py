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
from datetime import datetime
from typing import Dict, List, Protocol

from django.conf import settings
from django.utils import timezone

from bkuser.component.apigw import _call_apigw_api
from bkuser.component.esb import _call_esb_api
from bkuser.component.http import http_get, http_post
from bkuser.utils.url import urljoin


def validate_email_params(email: str, receiver: str):
    """
    校验邮件发送参数
    :param email: 邮箱地址
    :param receiver: 租户用户 ID
    """
    if not (email or receiver):
        raise ValueError("params `email`(email address) or `receiver`(tenant_user_id) must be provided")


def validate_sms_params(phone: str, phone_country_code: str, receiver: str):
    """
    校验短信发送参数
    :param phone: 手机号
    :param phone_country_code: 手机国际区号
    :param receiver: 租户用户 ID
    """
    if not ((phone and phone_country_code) or receiver):
        raise ValueError("params `phone` and `phone_country_code` or `receiver`(tenant_user_id) must be provided")


def validate_weixin_params(wx_userid: str, receiver: str):
    """
    校验微信发送参数
    :param wx_userid: 微信用户 ID
    :param receiver: 租户用户 ID
    """
    if not (wx_userid or receiver):
        raise ValueError("params `wx_userid` or `receiver`(tenant_user_id) must be provided")


class NotificationClient(Protocol):
    """通知客户端基类"""

    def send_mail(
        self,
        sender: str,
        title: str,
        content: str,
        email: str = "",
        receiver: str = "",
    ) -> None:
        """
        发送邮件
        支持通过接收者的邮箱地址 或 租户用户 ID 发送通知，当两者都存在时，优先使用邮箱地址
        :param sender: 发件人，例如："蓝鲸智云"
        :param title: 邮件标题
        :param content: 邮件内容（HTML 格式）
        :param email: 接收者邮箱地址
        :param receiver: 接收者的租户用户 ID(tenant_user_id)，与 email 参数二选一
        """

    def send_sms(
        self,
        content: str,
        phone: str = "",
        phone_country_code: str = "",
        receiver: str = "",
    ) -> None:
        """
        发送短信
        支持通过接收者的手机号码信息（国际区号 + 手机号）或 租户用户 ID 发送通知，当两者都存在时，优先使用手机号码信息
        :param content: 短信内容
        :param phone: 接收者手机号
        :param phone_country_code: 接收者手机国际区号
        :param receiver: 接收者的租户用户 ID (tenant_user_id)，与 手机号信息（phone、phone_country_code）参数二选一
        """

    def get_weixin_settings(self) -> Dict:
        """获取微信配置"""

    def get_weixin_token(self) -> Dict:
        """获取微信 token"""


def get_notification_client(tenant_id: str) -> NotificationClient:
    """
    选择对应消息通知 API（ESB 或 API 网关）
    :param tenant_id: 租户 ID
    """
    # 有单独部署 bk-cmsi 网关 或 开启多租户模式，使用 bk-cmsi 网关提供的消息通知 API
    if settings.HAS_BK_CMSI_APIGW or settings.ENABLE_MULTI_TENANT_MODE:
        return BkApigwCmsiClient(tenant_id)
    # 否则使用 ESB 提供的消息通知 API
    return BkEsbCmsiClient()


class BkEsbCmsiClient:
    """由 ESB 提供的消息通知 API"""

    ESB_CMSI_URL_PATH = "/api/c/compapi/v2/cmsi/"

    def send_mail(
        self,
        sender: str,
        title: str,
        content: str,
        email: str = "",
        receiver: str = "",
    ):
        """发送邮件"""
        validate_email_params(email, receiver)

        # 当两者都存在时，优先使用邮箱号
        params: Dict[str, str] = {
            "sender": sender,
            "title": title,
            "content": content,
        }
        if email:
            params["receiver"] = email
        else:
            params["receiver__username"] = receiver

        # NOTE: ESB 调用无需要传递 tenant_id，下同
        return _call_esb_api(
            http_post,
            urljoin(self.ESB_CMSI_URL_PATH, "send_mail/"),
            json=params,
        )

    def send_sms(
        self,
        content: str,
        phone: str = "",
        phone_country_code: str = "",
        receiver: str = "",
    ):
        """发送短信"""
        validate_sms_params(phone, phone_country_code, receiver)

        # 当两者都存在时，优先使用手机号信息
        params: Dict[str, str] = {"content": content}
        if phone and phone_country_code:
            params["receiver"] = phone
        else:
            params["receiver__username"] = receiver

        return _call_esb_api(
            http_post,
            urljoin(self.ESB_CMSI_URL_PATH, "send_sms/"),
            json=params,
        )

    def get_weixin_settings(self) -> Dict:
        """获取微信配置"""
        return _call_esb_api(http_get, "/api/c/compapi/esb/get_weixin_config/")

    def get_weixin_token(self) -> Dict:
        return _call_esb_api(http_get, "/api/c/compapi/weixin/get_token/")


class BkApigwCmsiClient:
    """由 API 网关提供的消息通知 API"""

    APIGW_NAME = "bk-cmsi"

    def __init__(self, tenant_id: str):
        """
        初始化客户端
        :param tenant_id: 租户 ID
        """
        self.tenant_id = tenant_id

    def send_mail(
        self,
        sender: str,
        title: str,
        content: str,
        email: str = "",
        receiver: str = "",
    ):
        """发送邮件"""
        validate_email_params(email, receiver)

        # 当两者都存在时，优先使用 email
        params: Dict[str, str | List[str]] = {
            "sender": sender,
            "title": title,
            "content": content,
        }
        if email:
            params["receiver"] = [email]
        else:
            params["receiver__username"] = [receiver]

        # NOTE: API 网关调用需要收件人所属租户 ID，下同
        return _call_apigw_api(
            http_post,
            self.APIGW_NAME,
            "/v1/send_mail/",
            self.tenant_id,
            json=params,
        )

    def send_sms(
        self,
        content: str,
        phone: str = "",
        phone_country_code: str = "",
        receiver: str = "",
    ):
        """发送短信"""
        validate_sms_params(phone, phone_country_code, receiver)

        # 当两者都存在时，优先使用手机号信息
        params: Dict[str, str | List[str]] = {"content": content}
        if phone and phone_country_code:
            params["receiver"] = [self._format_phone(phone, phone_country_code)]
        else:
            params["receiver__username"] = [receiver]

        return _call_apigw_api(
            http_post,
            self.APIGW_NAME,
            "/v1/send_sms/",
            self.tenant_id,
            json=params,
        )

    def _format_phone(self, phone: str, phone_country_code: str) -> str:
        """
        格式化手机号
        :param phone: 手机号
        :param phone_country_code: 手机国际区号
        :return: 格式化后的手机号（"+手机区号 手机号"）
        """
        return f"+{phone_country_code} {phone}"

    def get_weixin_settings(self) -> Dict:
        return _call_apigw_api(http_get, self.APIGW_NAME, "/v1/channels/weixin/settings/", self.tenant_id)

    def get_weixin_token(self) -> Dict:
        return _call_apigw_api(http_get, self.APIGW_NAME, "/v1/channels/weixin/token/", self.tenant_id)

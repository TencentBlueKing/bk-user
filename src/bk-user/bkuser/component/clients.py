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
from typing import Dict, List, Protocol

from django.conf import settings

from bkuser.component.apigw import _call_apigw_api
from bkuser.component.esb import _call_esb_api
from bkuser.component.http import http_post
from bkuser.utils.url import urljoin


class NotificationClient(Protocol):
    """通知客户端基类"""

    def send_mail(
        self,
        sender: str,
        title: str,
        content: str,
        receiver: str | None,
        receiver__username: str | None,
    ) -> None:
        """发送邮件
        :param receiver: 接收者邮箱
        :param receiver__username: 接收者用户名，与 receiver 二选一
        :param sender: 发件人
        :param title: 邮件标题
        :param content: 邮件内容（HTML格式）
        """

    def send_sms(
        self,
        content: str,
        receiver: Dict[str, str] | None,
        receiver__username: str | None,
    ) -> None:
        """发送短信
        :param receiver: 接收者手机号码信息，格式：{"phone": "xxx", "phone_country_code": "xxx"}
        :param receiver__username: 接收者用户名，与 receiver 二选一
        :param content: 短信内容
        """


def get_notification_client() -> NotificationClient:
    """
    选择对应消息通知 API（ESB 或 API 网关）
    """
    # 有单独部署 bk-cmsi  或 开启多租户
    if settings.HAS_BK_CMSI_APIGW or settings.ENABLE_MUTIL_TENANT_MODE:
        return BkApigwCmsiClient()
    return BkEsbCmsiClient()


def validate_notification_params(receiver: str | Dict[str, str] | None, receiver__username: str | None):
    """
    验证通知参数，receiver 和 receiver__username 必须提供一个
    :param receiver: 接收者手机号或邮箱
    :param receiver__username: 接收者用户名
    """
    if not (receiver or receiver__username):
        raise ValueError(
            "Param `receiver`(phone_info & email) or param `receiver__username`(tenant_user_id) must be provided"
        )


class BkEsbCmsiClient:
    """由 ESB 提供的消息通知 API"""

    ESB_CMSI_URL_PATH = "/api/c/compapi/v2/cmsi/"

    def send_mail(
        self,
        sender: str,
        title: str,
        content: str,
        receiver: str | None,
        receiver__username: str | None,
    ):
        """发送邮件"""
        validate_notification_params(receiver, receiver__username)

        # 当两者都存在时，优先使用 receiver
        params: Dict[str, str] = {
            "sender": sender,
            "title": title,
            "content": content,
        }
        if receiver:
            params["receiver"] = receiver
        else:
            params["receiver__username"] = receiver__username  # type: ignore

        return _call_esb_api(
            http_post,
            urljoin(self.ESB_CMSI_URL_PATH, "send_mail/"),
            json=params,
        )

    def send_sms(
        self,
        content: str,
        receiver: Dict[str, str] | None,
        receiver__username: str | None,
    ):
        """发送短信"""
        validate_notification_params(receiver, receiver__username)

        # 当两者都存在时，优先使用 receiver
        params: Dict[str, str] = {"content": content}
        if receiver:
            params["receiver"] = receiver["phone"]
        else:
            params["receiver__username"] = receiver__username  # type: ignore

        return _call_esb_api(
            http_post,
            urljoin(self.ESB_CMSI_URL_PATH, "send_sms/"),
            json=params,
        )


class BkApigwCmsiClient:
    """由 API 网关提供的消息通知 API"""

    APIGW_NAME = "bk-cmsi"

    def send_mail(
        self,
        sender: str,
        title: str,
        content: str,
        receiver: str | None,
        receiver__username: str | None,
    ):
        """发送邮件"""
        validate_notification_params(receiver, receiver__username)

        # 当两者都存在时，优先使用 receiver
        params: Dict[str, str | List[str]] = {
            "sender": sender,
            "title": title,
            "content": content,
        }
        if receiver:
            params["receiver"] = [receiver]
        else:
            params["receiver__username"] = [receiver__username]  # type: ignore

        return _call_apigw_api(
            http_post,
            self.APIGW_NAME,
            "/v1/send_mail/",
            json=params,
        )

    def send_sms(
        self,
        content: str,
        receiver: Dict[str, str] | None,
        receiver__username: str | None,
    ) -> None:
        """发送短信"""
        validate_notification_params(receiver, receiver__username)

        # 当两者都存在时，优先使用 receiver
        params: Dict[str, str | List[str]] = {"content": content}
        if receiver:
            params["receiver"] = [self._format_phone(receiver)]
        else:
            params["receiver__username"] = [receiver__username]  # type: ignore

        return _call_apigw_api(
            http_post,
            self.APIGW_NAME,
            "/v1/send_sms/",
            json=params,
        )

    def _format_phone(self, phone_info: Dict[str, str]) -> str:
        """
        格式化手机号
        :param phone_info: 手机号信息
        :return: 格式化后的手机号（"+手机区号 手机号"）
        """
        return f"+{phone_info['phone_country_code']} {phone_info['phone']}"

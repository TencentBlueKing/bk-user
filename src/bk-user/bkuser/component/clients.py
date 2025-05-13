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
from abc import ABC, abstractmethod
from typing import Dict

from django.conf import settings

from bkuser.component.apigw import _call_apigw_api
from bkuser.component.esb import _call_esb_api
from bkuser.component.http import http_post


class NotificationClient(ABC):
    """
    通知通知基类
    """

    @abstractmethod
    def send_mail(self, receiver: str, email: str, sender: str, title: str, content: str) -> None:
        pass

    @abstractmethod
    def send_sms(self, receiver: str, phone_info: Dict[str, str], content: str) -> None:
        pass


def get_notification_client() -> NotificationClient:
    """
    根据是否为多租户模式选择对应消息通知 API
    """
    return BkApigwCmsiClient() if settings.ENABLE_MUTIL_TENANT_MODE else BkEsbCmsiClient()


class BkEsbCmsiClient(NotificationClient):
    """
    由 ESB 提供的消息通知 API
    """

    def send_mail(self, receiver: str, email: str, sender: str, title: str, content: str):
        """
        发送邮件（目前未支持抄送，附件等参数，如有需要可以添加）

        :param receiver: 接收者租户用户 ID（用户管理理论上没有向多个用户发送相同邮件的需求）
        :param email: 接收者邮箱
        :param sender: 发件人
        :param title: 邮件标题
        :param content: 邮件内容（HTML 格式）
        """
        url_path = "/api/c/compapi/v2/cmsi/send_mail/"
        return _call_esb_api(
            http_post,
            url_path,
            data={"receiver__username": receiver, "sender": sender, "title": title, "content": content},
        )

    def send_sms(self, receiver: str, phone_info: Dict[str, str], content: str):
        """
        发送短信

        :param receiver: 接收者租户用户 ID（用户管理理论上没有向多个用户发送相同短信的需求）
        :param phone_info: 接收者手机号信息
        :param content: 短信内容
        """
        url_path = "/api/c/compapi/v2/cmsi/send_msg/"
        return _call_esb_api(
            http_post, url_path, data={"msg_type": "sms", "receiver__username": receiver, "content": content}
        )


class BkApigwCmsiClient(NotificationClient):
    """
    由 API 网关提供的消息通知 API
    """

    apigw_name = "bk-cmsi"

    def send_mail(self, receiver: str, email: str, sender: str, title: str, content: str):
        """
        发送邮件

        :param receiver: 接收者租户用户 ID
        :param email: 接收者邮箱地址
        :param sender: 发件人
        :param title: 邮件标题
        :param content: 邮件内容（HTML 格式）
        """
        url_path = "/v1/send_mail/"
        return _call_apigw_api(
            http_post,
            self.apigw_name,
            url_path,
            json={"receiver": [email], "sender": sender, "title": title, "content": content},
        )

    def send_sms(self, receiver: str, phone_info: Dict[str, str], content: str) -> None:
        """
        发送短信

        :param receiver: 接收者租户用户 ID
        :param phone_info: 接收者手机号信息
        :param content: 短信内容
        """
        url_path = "/v1/send_sms/"
        # TODO: 拼接手机国际区号与手机号码以向国际手机号发送短信，需待 bk-cmsi 提供支持，目前只能向国内手机号发送短信
        # phone = "+" + phone_info["phone_country_code"] + phone_info["phone"]
        phone = phone_info["phone"]
        return _call_apigw_api(http_post, self.apigw_name, url_path, json={"receiver": [phone], "content": content})

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
    """
    通知通知基类
    """

    def send_mail(self, email: str, sender: str, title: str, content: str):
        pass

    def send_sms(self, phone_info: Dict[str, str], content: str):
        pass


def get_notification_client() -> NotificationClient:
    """
    选择对应消息通知 API（ESB 或 API 网关）
    """
    # 有单独部署 bk-cmsi  或 开启多租户
    if settings.HAS_BK_CMSI_APIGW or settings.ENABLE_MUTIL_TENANT_MODE:
        return BkApigwCmsiClient()
    return BkEsbCmsiClient()


class BkEsbCmsiClient:
    """
    由 ESB 提供的消息通知 API
    """

    ESB_CMSI_URL_PATH = "/api/c/compapi/v2/cmsi/"

    def send_mail(self, email: str, sender: str, title: str, content: str):
        """
        发送邮件（目前未支持抄送，附件等参数，如有需要可以添加）

        :param email: 接收者邮箱
        :param sender: 发件人
        :param title: 邮件标题
        :param content: 邮件内容（HTML 格式）
        """
        return _call_esb_api(
            http_post,
            urljoin(self.ESB_CMSI_URL_PATH, "send_mail/"),
            json={"receiver": email, "sender": sender, "title": title, "content": content},
        )

    def send_sms(self, phone_info: Dict[str, str], content: str):
        """
        发送短信

        :param phone_info: 接收者手机号信息
        :param content: 短信内容
        """
        return _call_esb_api(
            http_post,
            urljoin(self.ESB_CMSI_URL_PATH, "send_sms/"),
            json={"receiver": phone_info["phone"], "content": content},
        )


class BkApigwCmsiClient:
    """
    由 API 网关提供的消息通知 API
    """

    APIGW_NAME = "bk-cmsi"

    def send_mail(self, email: str, sender: str, title: str, content: str):
        """
        发送邮件

        :param email: 接收者邮箱地址
        :param sender: 发件人
        :param title: 邮件标题
        :param content: 邮件内容（HTML 格式）
        """
        return _call_apigw_api(
            http_post,
            self.APIGW_NAME,
            "/v1/send_mail/",
            json={"receiver": [email], "sender": sender, "title": title, "content": content},
        )

    def send_sms(self, phone_info: Dict[str, str], content: str):
        """
        发送短信

        :param phone_info: 接收者手机号信息
        :param content: 短信内容
        """
        # TODO: 拼接手机国际区号与手机号码以向国际手机号发送短信，需待 bk-cmsi 提供支持，目前只能向国内手机号发送短信
        return _call_apigw_api(
            http_post,
            self.APIGW_NAME,
            "/v1/send_sms/",
            json={"receiver": self._format_phone(phone_info), "content": content},
        )

    def _format_phone(self, phone_info: Dict[str, str]) -> List[str]:
        """
        格式化手机号
        :param phone_info: 手机号信息
        :return: 格式化后的手机号
        """
        # TODO : 拼接手机国际区号与手机号码以向国际手机号发送短信，需待 bk-cmsi 提供支持，目前只能向国内手机号发送短信
        return [phone_info["phone"]]

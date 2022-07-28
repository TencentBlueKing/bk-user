# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import base64
import logging
from typing import List

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from bkuser_core.esb_sdk.shortcuts import get_client_by_raw_username

logger = logging.getLogger(__name__)

DEFAULT_EMAIL_SENDER = "bk-user-core-api"


class ReceiversCouldNotBeEmpty(Exception):
    """收件人不能为空"""


class SendMailFailed(Exception):
    """发送邮件失败"""


def send_mail(receivers: List[str], message: str, sender: str = None, title: str = None):
    """发邮件"""
    if not receivers:
        raise ReceiversCouldNotBeEmpty(_("收件人不能为空"))

    receivers_str = ",".join(receivers)

    title = title or _("[用户管理] 通知邮件")

    client = get_client_by_raw_username(user=sender or DEFAULT_EMAIL_SENDER)

    message_encoded = force_text(base64.b64encode(message.encode("utf-8")))
    logger.info(
        "going to send email to %s, title: %s, via %s",
        receivers_str,
        title,
        DEFAULT_EMAIL_SENDER,
    )

    # email_type 并非是所有系统共有的内容，只在特定版本生效
    send_mail_params = {
        "title": title,
        "content": message_encoded,
        "receiver": receivers_str,
        "is_content_base64": True,
        "email_type": "SEND_TO_INTERNET",
    }
    if not settings.FAKE_SEND_EMAIL:
        ret = client.cmsi.send_mail(**send_mail_params)
    else:
        logger.info("fake send email: %s", send_mail_params)
        return

    if not ret.get("result", False):
        logger.error(
            "Failed to send email notification %s for %s",
            receivers_str,
            ret.get("message", "unknown error"),
        )
        raise SendMailFailed(ret.get("message", "unknown error"))

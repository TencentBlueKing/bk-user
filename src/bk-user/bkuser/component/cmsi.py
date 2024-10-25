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
from .esb import _call_esb_api
from .http import http_post


def send_mail(receiver: str, sender: str, title: str, content: str):
    """
    发送邮件（目前未支持抄送，附件等参数，如有需要可以添加）

    :param receiver: 接收者租户用户 ID（用户管理理论上没有向多个用户发送相同邮件的需求）
    :param sender: 发件人
    :param title: 邮件标题
    :param content: 邮件内容（HTML 格式）
    """
    url_path = "/api/c/compapi/cmsi/send_mail/"
    return _call_esb_api(
        http_post,
        url_path,
        data={"receiver__username": receiver, "sender": sender, "title": title, "content": content},
    )


def send_sms(receiver: str, content: str):
    """
    发送短信

    :param receiver: 接收者租户用户 ID（用户管理理论上没有向多个用户发送相同短信的需求）
    :param content: 短信内容
    """
    url_path = "/api/c/compapi/cmsi/send_sms/"
    return _call_esb_api(http_post, url_path, data={"receiver__username": receiver, "content": content})

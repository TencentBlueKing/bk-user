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
from typing import List

from .esb import _call_esb_api
from .http import http_get


def send_mail(receivers: List[str], sender: str, title: str, content: str):
    """
    发送邮件（目前未支持抄送，附件等参数，如有需要可以添加）

    :param receivers: 接收者邮箱列表
    :param sender: 发件人
    :param title: 邮件标题
    :param content: 邮件内容（HTML 格式）
    """
    url_path = "/api/c/compapi/cmsi/send_mail/"
    return _call_esb_api(
        http_get,
        url_path,
        data={"receiver": ",".join(receivers), "sender": sender, "title": title, "content": content},
    )


def send_sms(receivers: List[str], content: str):
    """
    发送短信

    :param receivers: 接收者手机号列表
    :param content: 短信内容
    """
    url_path = "/api/c/compapi/cmsi/send_sms/"
    return _call_esb_api(
        http_get,
        url_path,
        data={"receiver": ",".join(receivers), "content": content},
    )

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
from blue_krill.data_types.enum import EnumField, StrStructuredEnum
from django.utils.translation import gettext_lazy as _


class WeixinTypeEnum(StrStructuredEnum):
    """微信类型枚举"""

    QY = EnumField("qy", label=_("企业微信"))
    QYWX = EnumField("qywx", label=_("企业微信(旧版)"))
    MP = EnumField("mp", label=_("微信公众号"))


# 企业微信扫码登录 state 过期时间，单位：秒
WECOM_STATE_EXPIRE_SECONDS = 300

# 企业微信 API 相关常量
WECOM_LOGIN_URL = "https://login.work.weixin.qq.com/wwlogin/sso/login"
WECOM_USERINFO_URL = "https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo"

# 微信公众号 API 相关常量
MP_QRCODE_CREATE_URL = "https://api.weixin.qq.com/cgi-bin/qrcode/create"
MP_QRCODE_SHOW_URL = "https://mp.weixin.qq.com/cgi-bin/showqrcode"

# 微信公众号事件类型
MP_EVENT_SUBSCRIBE = "subscribe"
MP_EVENT_SCAN = "SCAN"

# 二维码过期时间，单位：秒
MP_QRCODE_EXPIRE_SECONDS = 300

# 微信公众号消息模板
MP_MESSAGE_TEMPLATE = """<xml>
                <ToUserName><![CDATA[{to_user}]]></ToUserName>
                <FromUserName><![CDATA[{from_user}]]></FromUserName>
                <CreateTime>{create_time}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{content}]]></Content>
                </xml>"""

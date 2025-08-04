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

# 微信绑定类型使用示例：
# 1. 在审计记录中区分微信类型：
#    auditor.record_bind(tenant_user, bind_type=WECHAT_BIND_TYPE_WECOM)  # 企业微信
#    auditor.record_bind(tenant_user, bind_type=WECHAT_BIND_TYPE_WEIXIN)  # 微信公众号
#
# 2. 根据微信类型获取绑定类型：
#    bind_type = WECHAT_TYPE_TO_BIND_TYPE.get(wx_type, WECHAT_BIND_TYPE_WEIXIN)
#
# 3. 在审计记录的 extras 中会包含：
#    {"bind_type": "wecom"}  # 企业微信
#    {"bind_type": "weixin"} # 微信公众号

# 企业微信扫码登录 state 过期时间，单位：秒
STATE_EXPIRE_SECONDS = 300

# 微信 API 相关常量
WECOM_LOGIN_URL = "https://login.work.weixin.qq.com/wwlogin/sso/login"
WECOM_USERINFO_URL = "https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo"
WECHAT_QRCODE_CREATE_URL = "https://api.weixin.qq.com/cgi-bin/qrcode/create"
WECHAT_QRCODE_SHOW_URL = "https://mp.weixin.qq.com/cgi-bin/showqrcode"

# 微信事件类型
WECHAT_EVENT_SUBSCRIBE = "subscribe"
WECHAT_EVENT_SCAN = "SCAN"

# 二维码过期时间（秒）
QRCODE_EXPIRE_SECONDS = 300

# 微信 API 成功状态码
WECHAT_API_SUCCESS_CODE = 0

# 微信绑定类型常量
WECHAT_BIND_TYPE_WECOM = "wecom"  # 企业微信
WECHAT_BIND_TYPE_WEIXIN = "weixin"  # 微信公众号

# 微信类型映射到绑定类型
WECHAT_TYPE_TO_BIND_TYPE = {
    "qy": WECHAT_BIND_TYPE_WECOM,  # 企业微信
    "qywx": WECHAT_BIND_TYPE_WECOM,  # 企业微信
    "mp": WECHAT_BIND_TYPE_WEIXIN,  # 微信公众号
}

# 微信消息模板
WECHAT_MESSAGE_TEMPLATE = """<xml>
                <ToUserName><![CDATA[{to_user}]]></ToUserName>
                <FromUserName><![CDATA[{from_user}]]></FromUserName>
                <CreateTime>{create_time}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{content}]]></Content>
                </xml>"""

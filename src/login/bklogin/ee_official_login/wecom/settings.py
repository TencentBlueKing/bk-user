# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.conf import settings

# 企业微信扫码登录相关配置
CORP_ID = settings.WECOM_CORP_ID
CORP_SECRET = settings.WECOM_CORP_SECRET
AGENT_ID = settings.WECOM_AGENT_ID

# 企微扫码登陆 Base URL
QR_LOGIN_URL = "https://login.work.weixin.qq.com/wwlogin/sso/login"

# 获取企业微信 access_token 的 API URL
ACCESS_TOKEN_URL = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"

# 获取企业微信用户登录身份的 API URL
GET_USER_URL = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo"

# 获取企业微信用户详细信息的 API URL
GET_USER_INFO_URL = "https://qyapi.weixin.qq.com/cgi-bin/user/get"

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
ACCESS_TOKEN_URL = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}"
DEPARTMENT_LIST_URL = "https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token={}"
USER_LIST_URL = "https://qyapi.weixin.qq.com/cgi-bin/user/simplelist?access_token={}&department_id={}&fetch_child=1"
USER_LIST_DETAIL = "https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token={}&department_id={}&fetch_child={}"
# USER_LIST_DETAIL = "https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token={}&department_id={}&fetch_child=1"


class WeComStatus:
    """WeCom用户状态类型
    1=已激活，2=已禁用，4=未激活，5=退出企业。
    """
    ACTIVE = 1
    DISABLED = 2
    INACTIVE = 4
    EXIT_ENTERPRISE = 5


class WeComEnabled:
    ENABLE = 1
    DISABLE = 0

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


class NoKeyItemAvailable(Exception):
    """没有可找到的对象"""


class CustomAPIRequestFailed(Exception):
    """拉取自定义 API 失败"""


class WeComAPIRequestFailed(Exception):
    """WeCom API 失败"""


class WeComAPIRequestStatusCodeError(Exception):
    """WeCom API 返回码非200"""


class WeComAPIRequestJsonLoadError(Exception):
    """WeCom API json load 失败"""


class WeComAPIGetAccessTokenError(Exception):
    """WeCom API 获取 accesstoken 失败"""


class WeComAPIGetDepartmentError(Exception):
    """WeCom API 获取部门信息失败"""


class WeComAPIGetUserListError(Exception):
    """WeCom API 获取用户信息失败"""


class WeComLoginError(Exception):
    """WeCom 登录直接返回"""

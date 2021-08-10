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


class SearchResultsNotComplete(Exception):
    """搜索返回值不完整"""


class LdapCannotBeInitialized(Exception):
    """Ldap 初始化失败"""


class DbSyncManagerNotReady(Exception):
    """DB 同步管理器未就绪"""


class LDAPSettingNotReady(Exception):
    """配置未就绪"""


class SearchFailed(Exception):
    """配置未就绪"""


class LoginCheckFailed(Exception):
    """登陆校验失败"""


class FetchUserMetaInfoFailed(Exception):
    """获取用户基本信息失败"""

# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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


class OpenWebApiEnum(StrStructuredEnum):
    """OpenWeb API 枚举"""

    RETRIEVE_USER_DISPLAY_INFO = EnumField("retrieve_user_display_info", label="查询用户展示信息")
    BATCH_QUERY_USER_DISPLAY_INFO = EnumField("batch_query_user_display_info", label="批量查询用户展示信息")
    SEARCH_USER = EnumField("search_user", label="搜索用户信息")
    BATCH_LOOKUP_USER = EnumField("batch_lookup_user", label="批量匹配用户")
    SEARCH_DEPARTMENT = EnumField("search_department", label="搜索部门信息")
    BATCH_LOOKUP_DEPARTMENT = EnumField("batch_lookup_department", label="批量匹配部门")
    LIST_DEPARTMENT_CHILD = EnumField("list_department_child", label="查询部门子部门信息")
    LIST_DEPARTMENT_USER = EnumField("list_department_user", label="查询部门所属用户信息")
    SEARCH_VIRTUAL_USER = EnumField("search_virtual_user", label="搜索虚拟用户信息")
    BATCH_LOOKUP_VIRTUAL_USER = EnumField("batch_lookup_virtual_user", label="批量匹配虚拟用户")
    LIST_VIRTUAL_USER = EnumField("list_virtual_user", label="查询虚拟用户信息")

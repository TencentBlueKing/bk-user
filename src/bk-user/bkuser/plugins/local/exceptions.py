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
from bkuser.plugins.exceptions import BaseDataSourcePluginError


class LocalDataSourcePluginError(BaseDataSourcePluginError):
    """本地数据源插件基础异常"""


class UserSheetNotExists(LocalDataSourcePluginError):
    """待导入文件中不存在用户表"""


class SheetColumnsNotMatch(LocalDataSourcePluginError):
    """待导入文件中用户表列不匹配"""


class CustomColumnNameInvalid(LocalDataSourcePluginError):
    """待导入文件中自定义字段列名不合法"""


class DuplicateColumnName(LocalDataSourcePluginError):
    """待导入文件中存在重复列名"""


class RequiredFieldIsEmpty(LocalDataSourcePluginError):
    """待导入文件中必填字段为空"""


class InvalidLeader(LocalDataSourcePluginError):
    """待导入的用不上级信息不合法"""


class InvalidUsername(LocalDataSourcePluginError):
    """待导入的用户名非法"""


class DuplicateUsername(LocalDataSourcePluginError):
    """待导入文件中存在重复用户"""

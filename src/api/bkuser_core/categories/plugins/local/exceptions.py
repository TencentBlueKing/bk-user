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
from django.utils.translation import ugettext_lazy as _


class RequiredINfoMissing(Exception):
    """关键信息丢失"""


class FileFormatError(Exception):
    """文件格式不正确"""


class ParseFailedException(Exception):
    """字段解析失败"""

    def __init__(
        self,
        field_name: str,
        reason: str,
        *args,
    ):
        self.field_name = field_name
        self.reason = reason
        super().__init__(*args)

    def __str__(self):
        return _("解析字段 {} 失败: {}").format(self.field_name, self.reason)


class DataFormatError(Exception):
    """文件内容格式不正确"""


class ColumnNotFound(Exception):
    """查找的列不存在"""


class LoginCheckFailed(Exception):
    """登陆校验失败"""


class DepartmentNotFoundByName(Exception):
    """通过部门名称无法找到对应部门"""

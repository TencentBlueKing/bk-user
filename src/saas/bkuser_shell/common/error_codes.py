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
import copy

from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import APIException


class APIError(APIException):
    """A common API Error"""

    delimiter = ": "

    def __init__(self, code):
        self.code = code
        super(APIError, self).__init__(str(self))

    def __str__(self):
        return "APIError %s-%s>" % (self.code.status_code, self.code.code_name)

    def format(self, message=None, replace=False, **kwargs):
        """Using a customized message for this ErrorCode

        :param str message: if not given, default message will be used
        :param bool replace: relace default message if true
        """
        self.code = copy.copy(self.code)
        if message:
            if replace:
                self.code.message = message
            else:
                self.code.message += u"%s%s" % (self.delimiter, message)

        # Render message string
        if kwargs:
            self.code.message = self.code.message.format(**kwargs)

        return self

    def f(self, message=None, **kwargs):
        return self.format(message=message, **kwargs)

    @property
    def message(self):
        return self.code.message

    @property
    def code_num(self):
        return self.code.code_num


class ErrorCode:
    """Error code"""

    def __init__(self, code_name, message, code_num=-1, status_code=400):
        self.code_name = code_name
        self.message = message
        self.code_num = code_num
        self.status_code = status_code


class ErrorCodeCollection:
    """A collection of ErrorCodes"""

    def __init__(self):
        self._error_codes_dict = {}

    def add_code(self, error_code):
        self._error_codes_dict[error_code.code_name] = error_code

    def add_codes(self, code_list):
        for error_code in code_list:
            self._error_codes_dict[error_code.code_name] = error_code

    def __getattr__(self, code_name):
        error_code = self._error_codes_dict[code_name]
        return APIError(error_code)


error_codes = ErrorCodeCollection()
error_codes.add_codes(
    [
        # 用户字段
        ErrorCode("CANNOT_CREATE_DYNAMIC_FIELD", _("无法创建用户字段")),
        ErrorCode("CANNOT_UPDATE_DYNAMIC_FIELD", _("无法更新用户字段")),
        ErrorCode("CANNOT_GET_DYNAMIC_FIELD", _("无法获取用户字段")),
        ErrorCode("CANNOT_DELETE_DYNAMIC_FIELD", _("无法删除用户字段")),
        ErrorCode("UNKNOWN_FIELD", _("未知自定义字段")),
        # 用户目录
        ErrorCode("CANNOT_FIND_DEFAULT_CATEGORY", _("无法找到默认目录")),
        ErrorCode("CATEGORY_CREATE_FAILED", _("用户目录创建失败")),
        ErrorCode("CATEGORY_UPDATE_FAILED", _("用户目录更新失败")),
        ErrorCode("CATEGORY_DELETE_FAILED", _("用户目录删除失败")),
        ErrorCode("CANNOT_FIND_CATEGORY", _("无法找到目录")),
        ErrorCode("CATEGORY_EXPORT_FAILED", _("用户目录导出失败")),
        ErrorCode("SYNC_CATEGORY_FAILED", _("用户目录同步失败")),
        ErrorCode("TEST_CATEGORY_FAILED", _("用户目录测试连接失败")),
        ErrorCode("CATEGORY_CANNOT_TEST_CONNECTION", _("该类型用户目录不能测试连接")),
        ErrorCode("LOCAL_CATEGORY_NEEDS_EXCEL_FILE", _("本地目录需要Excel文件同步数据")),
        ErrorCode("ONLY_LOCAL_CATEGORY_CAN_EXPORT", _("只有本地目录支持导出数据")),
        ErrorCode("ONLY_SUPERUSER_CAN_EXPORT", _("只有超级用户可以导出数据")),
        # 配置
        ErrorCode("CANNOT_CREATE_SETTINGS", _("无法创建配置")),
        ErrorCode("CANNOT_GET_SETTINGS", _("无法获取配置")),
        ErrorCode("CANNOT_UPDATE_SETTINGS", _("无法更新配置")),
        ErrorCode("CANNOT_DELETE_SETTINGS", _("无法更新配置")),
        # 组织架构
        ErrorCode("CANNOT_DELETE_DEPARTMENT", _("无法删除组织")),
        ErrorCode("CANNOT_FETCH_PROFILES_FROM_DEPARTMENT", _("无法获取组织下用户")),
        ErrorCode("CANNOT_GET_DEPARTMENT", _("无法获取组织")),
        ErrorCode("CANNOT_UPDATE_DEPARTMENT", _("无法更新组织")),
        ErrorCode("CANNOT_CREATE_DEPARTMENT", _("无法创建组织")),
        ErrorCode("CANNOT_UPDATE_PROFILE", _("无法更新用户")),
        ErrorCode("CANNOT_GET_PROFILE", _("无法获取用户")),
        ErrorCode("CANNOT_CREATE_PROFILE", _("无法创建用户")),
        # 审计
        ErrorCode("CANNOT_GET_AUDIT_LOG", _("无法获取审计日志")),
        ErrorCode("CANNOT_EXPORT_EMPTY_LOG", _("审计日志为空，无法导出")),
        # 密码重置
        ErrorCode("CANNOT_GENERATE_TOKEN", _("无法生成重置链接")),
        ErrorCode("CANNOT_GET_PROFILE_BY_TOKEN", _("链接已失效，请重新申请")),
        ErrorCode("USER_MISS_AUTH", _("用户身份未通过校验")),
        ErrorCode("CANNOT_MODIFY_PASSWORD", _("无法修改密码")),
        # 通用
        ErrorCode("CANNOT_FIND_TEMPLATE", _("无法找到页面模版")),
        # 权限中心
        ErrorCode("NO_PERMISSION_MANAGE_CATEGORY", _("没有权限管理用户目录，请在权限中心申请"), status_code=403),
        # 版本日志
        ErrorCode("FAILED_TO_LOAD_RELEASE_INFO", _("版本日志列表字段校验错误")),
        ErrorCode("VERSION_DETAIL_TYPE_ERROR", _("版本日志详情类型错误")),
        ErrorCode("EMPTY_LOG_DETAILS_ERROR", _("版本日志详情空错误")),
        ErrorCode("VERSION_FORMAT_ERROR", _("版本日志格式错误")),
        ErrorCode("UNKNOWN_VERSION_NUMBER", _("版本号未知")),
    ]
)

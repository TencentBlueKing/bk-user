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

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT


class CoreAPIError(APIException):
    """A common API Error"""

    delimiter = ", "

    def __init__(self, code):
        self.code = code
        super().__init__(str(self))

    def __str__(self):
        return f"CoreAPIError {self.code.status_code}-{self.code.code_name}"

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
                self.code.message += "%s%s" % (self.delimiter, message)

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


class ErrorCode(object):
    """Error code"""

    def __init__(self, code_name, message, code_num=-1, status_code=HTTP_400_BAD_REQUEST):
        self.code_name = code_name
        self.message = message
        self.code_num = code_num
        self.status_code = status_code


class ErrorCodeCollection(object):
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
        return CoreAPIError(error_code)


error_codes = ErrorCodeCollection()
error_codes.add_codes(
    [
        # 通用
        ErrorCode("FIELDS_NOT_SUPPORTED_YET", _("存在不支持动态返回的字段")),
        ErrorCode("QUERY_PARAMS_ERROR", _("查询参数错误，请检查")),
        ErrorCode("RESOURCE_ALREADY_ENABLED", _("资源数据未被删除"), status_code=HTTP_400_BAD_REQUEST),
        # 登陆相关
        ErrorCode("USER_DOES_NOT_EXIST", _("账号不存在"), 3210010),
        ErrorCode("USERNAME_FORMAT_ERROR", _("账户名格式错误"), 3210012),
        ErrorCode("DOMAIN_UNKNOWN", _("未知登陆域"), 3210017),
        ErrorCode("USER_EXIST_MANY", _("存在多个同名账号，请联系管理员"), 3210014),
        ErrorCode("USER_IS_DISABLED", _("账号已被管理员禁用，请联系管理员"), 3210016),
        ErrorCode("USER_IS_LOCKED", _("账号长时间未登录，已被冻结，请联系管理员"), 3210015),
        ErrorCode("PASSWORD_ERROR", _("账户名和密码不匹配"), 3210013),
        ErrorCode(
            "PASSWORD_DUPLICATED",
            _("新密码不能与最近{}次密码相同").format(settings.MAX_PASSWORD_HISTORY),
        ),
        ErrorCode("PASSWORD_EXPIRED", _("该账户密码已到期，请修改密码后登录"), 3210018),
        ErrorCode("TOO_MANY_TRY", _("密码输入错误次数过多，已被锁定"), 3210011),
        ErrorCode("CATEGORY_NOT_ENABLED", _("用户目录未启用"), 3210019),
        ErrorCode("ERROR_FORMAT", _("传入参数错误"), 3210019),
        # 用户相关
        ErrorCode("EMAIL_NOT_PROVIDED", _("该用户没有提供邮箱，发送邮件失败")),
        ErrorCode("USER_ALREADY_EXISTED", _("该目录下此用户名已存在"), status_code=HTTP_409_CONFLICT),
        ErrorCode("SAVE_USER_INFO_FAILED", _("保存用户信息失败")),
        # 上传文件相关
        ErrorCode("FILE_IMPORT_TOO_LARGE", _("上传文件过大")),
        ErrorCode("FILE_IMPORT_FORMAT_ERROR", _("上传文件格式错误")),
        # 用户目录相关
        ErrorCode("CANNOT_FIND_CATEGORY", _("找不到对应的用户目录")),
        ErrorCode("CANNOT_UPDATE_DOMAIN", _("用户目录不能更新域字段")),
        ErrorCode("CANNOT_DISABLE_DOMAIN", _("默认用户目录不能被禁用")),
        ErrorCode("CANNOT_DELETE_DEFAULT_CATEGORY", _("不能删除默认用户目录")),
        ErrorCode("LOCAL_CATEGORY_CANNOT_SYNC", _("本地目录需要上传文件进行同步")),
        ErrorCode("CATEGORY_CANNOT_IMPORT_BY_FILE", _("该目录不能够通过文件同步数据")),
        ErrorCode("LOAD_DATA_FAILED", _("同步数据失败")),
        ErrorCode("LOAD_LDAP_CLIENT_FAILED", _("加载 LDAP Client 失败")),
        ErrorCode("LOAD_LOGIN_HANDLER_FAILED", _("登陆校验失败")),
        ErrorCode("SYNC_DATA_FAILED", _("同步数据失败")),
        ErrorCode("LOAD_DATA_ADAPTER_FAILED", _("加载数据同步模块失败")),
        ErrorCode("SAVE_DATA_FAILED", _("存储同步数据失败")),
        ErrorCode("TEST_CONNECTION_UNSUPPORTED", _("用户目录不支持测试连接")),
        ErrorCode("TEST_CONNECTION_FAILED", _("测试连接失败")),
        ErrorCode("TEST_FETCH_DATA_FAILED", _("测试获取数据失败")),
        ErrorCode("CANNOT_MANUAL_WRITE_INTO", _("该用户目录不能够手动写入数据")),
        ErrorCode("CATEGORY_TYPE_NOT_SUPPORTED", _("当前运行版本不支持此用户目录类型")),
        ErrorCode("PLUGIN_NOT_FOUND", _("找不到指定名称的插件")),
        # 配置相关
        ErrorCode("CANNOT_FIND_SETTING_META", _("找不到对应的配置元信息")),
        ErrorCode("CANNOT_CREATE_SETTING", _("无法创建配置")),
        # 组织架构相关
        ErrorCode("DEPARTMENT_NAME_CONFLICT", _("同一个部门下子部门命名冲突")),
        # 用户字段相关
        ErrorCode("FIELD_IS_NOT_EDITABLE", _("字段不能被编辑")),
        ErrorCode("BUILTIN_FIELD_CANNOT_BE_DELETED", _("内置字段不能被删除")),
        # 用户 token 相关
        ErrorCode("PROFILE_TOKEN_EXPIRED", _("用户Token已过期，请重新申请")),
        ErrorCode("CANNOT_GET_TOKEN_HOLDER", _("无法获取有效的用户 Token")),
        # 权限相关
        ErrorCode("ACTION_UNKNOWN", _("未知权限项")),
        ErrorCode("ACTION_ID_MISSING", _("权限项缺失")),
    ]
)

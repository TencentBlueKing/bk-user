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
from typing import Optional

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT


class CoreAPIError(APIException):
    """A common API Error"""

    delimiter = ", "

    def __init__(self, code):
        self.code = code
        self.data = {}
        super().__init__(str(self))

    def __str__(self):
        return f"CoreAPIError {self.code.status_code}-{self.code.code_name}"

    def format(self, message: Optional[str] = None, replace: bool = False, data: Optional[dict] = None, **kwargs):
        """Using a customized message for this ErrorCode

        :param data: exception body
        :param str message: if not given, default message will be used
        :param bool replace: replace default message if true
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

        if data:
            self.data = data

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

    def __init__(self, code_name, message, code_num=-1, status_code=HTTP_400_BAD_REQUEST):
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
        return CoreAPIError(error_code)


error_codes = ErrorCodeCollection()
error_codes.add_codes(
    [
        # 通用
        ErrorCode("FIELDS_NOT_SUPPORTED_YET", _("存在不支持动态返回的字段")),
        ErrorCode("QUERY_PARAMS_ERROR", _("查询参数错误，请检查")),
        ErrorCode("QUERY_TOO_LONG", _("查询参数过长")),
        ErrorCode("USERNAME_MISSING", _("用户名信息缺失")),
        ErrorCode("RESOURCE_ALREADY_ENABLED", _("资源数据未被删除")),
        ErrorCode("RESOURCE_RESTORATION_FAILED", _("资源恢复失败")),
        # 登陆相关
        ErrorCode("USER_DOES_NOT_EXIST", _("账号不存在"), 3210010),
        ErrorCode("TOO_MANY_TRY", _("密码输入错误次数过多，已被锁定"), 3210011),
        ErrorCode("USERNAME_FORMAT_ERROR", _("账户名格式错误"), 3210012),
        ErrorCode("PASSWORD_ERROR", _("账户或者密码错误，请重新输入"), 3210013),
        ErrorCode("USER_EXIST_MANY", _("存在多个同名账号，请联系管理员"), 3210014),
        ErrorCode("USER_IS_LOCKED", _("账号长时间未登录，已被冻结，请联系管理员"), 3210015),
        ErrorCode("USER_IS_DISABLED", _("账号已被管理员禁用，请联系管理员"), 3210016),
        ErrorCode("DOMAIN_UNKNOWN", _("未知登陆域"), 3210017),
        ErrorCode("PASSWORD_EXPIRED", _("该账户密码已到期"), 3210018),
        ErrorCode("CATEGORY_NOT_ENABLED", _("用户目录未启用"), 3210019),
        ErrorCode("ERROR_FORMAT", _("传入参数错误"), 3210020),
        ErrorCode("SHOULD_CHANGE_INITIAL_PASSWORD", _("平台分配的初始密码未修改"), 3210021),
        ErrorCode("USER_IS_DELETED", _("账号已被删除，请联系管理员"), 3210022),
        ErrorCode("CATEGORY_PLUGIN_LOAD_FAIL", _("目录登录插件加载失败"), 3210023),
        ErrorCode("USER_IS_EXPIRED", _("该用户账号已过期"), 3210024),
        ErrorCode("USER_IS_RESIGNED", _("该用户账号已离职"), 3210025),
        ErrorCode("USER_IS_ABNORMAL", _("用户处于异常状态:{status}，请联系管理员")),
        # 用户相关
        ErrorCode("PASSWORD_DUPLICATED", _("新密码不能与最近{max_password_history}次密码相同")),
        ErrorCode("EMAIL_NOT_PROVIDED", _("该用户没有提供邮箱，发送邮件失败")),
        ErrorCode("USER_ALREADY_EXISTED", _("该目录下此用户名已存在"), status_code=HTTP_409_CONFLICT),
        ErrorCode("SAVE_USER_INFO_FAILED", _("保存用户信息失败, 失败原因:{exception_message}")),
        ErrorCode("PASSWORD_DUPLICATED", _("新密码不能与最近{max_password_history}次密码相同")),
        ErrorCode("TELEPHONE_NOT_PROVIDED", _("该用户没有绑定手机号，发送短信失败")),
        ErrorCode("TELEPHONE_BOUND_TO_MULTI_PROFILE", _("该手机号被多个用户绑定，请输入具体的用户名或联系管理员处理")),
        ErrorCode("VERIFICATION_CODE_REPEAT_SENDING_REQUIRE", _("验证码已发送，有效时间为{effective_minutes}分钟，请勿重复发送")),
        ErrorCode("VERIFICATION_CODE_SEND_REACH_LIMIT", _("该手机号已超过当日重置密码短信发送限制次数")),
        ErrorCode("VERIFICATION_CODE_INVALID", _("验证码失效，请重新发送")),
        ErrorCode("VERIFICATION_CODE_WRONG", _("你所输入验证码错误，请重新输入")),
        ErrorCode("VERIFICATION_CODE_WRONG_REACH_LIMIT", _("你所输入验证码错误，验证次数已达上限，请验证码过期后重试")),
        ErrorCode("OLD_PASSWORD_ERROR", _("原密码校验失败")),
        # 上传文件相关
        ErrorCode("FILE_IMPORT_TOO_LARGE", _("上传文件过大")),
        ErrorCode("FILE_IMPORT_FORMAT_ERROR", _("上传文件格式错误")),
        # 用户目录相关
        ErrorCode("CANNOT_FIND_CATEGORY", _("找不到对应的用户目录")),
        ErrorCode("CANNOT_UPDATE_DOMAIN", _("用户目录不能更新域字段")),
        ErrorCode("CANNOT_DISABLE_DOMAIN", _("默认用户目录不能被禁用")),
        ErrorCode("CANNOT_DELETE_DEFAULT_CATEGORY", _("不能删除默认用户目录")),
        ErrorCode("CANNOT_DELETE_ACTIVE_CATEGORY", _("不能删除未停用用户目录")),
        ErrorCode("LOCAL_CATEGORY_CANNOT_SYNC", _("本地目录需要上传文件进行同步")),
        ErrorCode("CATEGORY_CANNOT_IMPORT_BY_FILE", _("该目录不能够通过文件同步数据")),
        ErrorCode("LOAD_DATA_FAILED", _("同步数据失败")),
        ErrorCode("LOAD_LDAP_CLIENT_FAILED", _("加载 LDAP Client 失败")),
        ErrorCode("LOAD_LOGIN_HANDLER_FAILED", _("登陆校验失败")),
        ErrorCode("SYNC_DATA_FAILED", _("同步数据失败")),
        ErrorCode("CREATE_SYNC_TASK_FAILED", _("创建同步任务失败")),
        ErrorCode("LOAD_DATA_ADAPTER_FAILED", _("加载数据同步模块失败")),
        ErrorCode("SAVE_DATA_FAILED", _("存储同步数据失败")),
        ErrorCode("TEST_CONNECTION_UNSUPPORTED", _("用户目录不支持测试连接")),
        ErrorCode("TEST_CONNECTION_FAILED", _("测试连接失败")),
        ErrorCode("TEST_FETCH_DATA_FAILED", _("测试获取数据失败")),
        ErrorCode("CANNOT_MANUAL_WRITE_INTO", _("该用户目录不能够手动写入数据")),
        ErrorCode("CATEGORY_TYPE_NOT_SUPPORTED", _("当前运行版本不支持此用户目录类型")),
        ErrorCode("PLUGIN_NOT_FOUND", _("找不到指定名称的插件")),
        ErrorCode("LOCAL_CATEGORY_NEEDS_EXCEL_FILE", _("本地目录需要Excel文件同步数据")),
        ErrorCode("REVERT_CATEGORY_CONFLICT", _("用户目录还原冲突")),
        # 配置相关
        ErrorCode("CANNOT_FIND_SETTING_META", _("找不到对应的配置元信息")),
        ErrorCode("CANNOT_CREATE_SETTING", _("无法创建配置")),
        ErrorCode("CANNOT_UPDATE_SETTING", _("无法更新配置")),
        # 组织架构相关
        ErrorCode("CANNOT_FIND_DEPARTMENT", _("找不到对应的部门")),
        ErrorCode("DEPARTMENT_NAME_CONFLICT", _("同一个部门下子部门命名冲突")),
        # 用户字段相关
        ErrorCode("FIELD_IS_NOT_EDITABLE", _("字段不能被编辑")),
        ErrorCode("BUILTIN_FIELD_CANNOT_BE_DELETED", _("内置字段不能被删除")),
        # 用户 token 相关
        ErrorCode("PROFILE_TOKEN_EXPIRED", _("用户Token已过期，请重新申请")),
        ErrorCode("CANNOT_GET_TOKEN_HOLDER", _("无法获取有效的用户 Token")),
        # 权限相关
        # ErrorCode("ACTION_UNKNOWN", _("未知权限项")),
        # ErrorCode("ACTION_ID_MISSING", _("权限项缺失")),
        ErrorCode("CANNOT_DELETE_DEPARTMENT", _("不能删除部门")),
        ErrorCode("CANNOT_EXPORT_EMPTY_LOG", _("审计日志为空，无法导出")),
        # 用户字段
        ErrorCode("UNKNOWN_FIELD", _("未知自定义字段")),
        ErrorCode("CANNOT_FIND_PROFILE", _("无法找到用户")),
        # 回收站相关
        ErrorCode("CANNOT_FIND_CATEGORY_IN_RECYCLE_BIN", _("回收站中无法找到目录：{category_id}")),
    ]
)

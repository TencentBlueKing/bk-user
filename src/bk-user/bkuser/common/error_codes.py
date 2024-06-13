# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from http import HTTPStatus

from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _

from bkuser.utils.std_error import ErrorCode


class ErrorCodeCategoryEnum(str, StructuredEnum):
    # 400
    INVALID_ARGUMENT = EnumField("INVALID_ARGUMENT", label=_("参数不符合格式"))
    INVALID_REQUEST = EnumField("INVALID_REQUEST", label=_("参数符合格式但不符合业务规则"))
    OUT_OF_RANGE = EnumField("OUT_OF_RANGE", label=_("客户端指定的范围无效"))
    FAILED_PRECONDITION = EnumField("FAILED_PRECONDITION", label=_("当前系统状态无法执行请求"))
    # 401
    UNAUTHENTICATED = EnumField("UNAUTHENTICATED", label=_("未提供身份认证凭证"))
    # 403
    IAM_NO_PERMISSION = EnumField("IAM_NO_PERMISSION", label=_("权限中心没有相关权限"))
    NO_PERMISSION = EnumField("NO_PERMISSION", label=_("没有相关权限"))
    # 404
    NOT_FOUND = EnumField("NOT_FOUND", label=_("资源不存在"))
    # 409
    ALREADY_EXISTS = EnumField("ALREADY_EXISTS", label=_("客户端尝试创建的资源已存在"))
    ABORTED = EnumField("ABORTED", label=_("并发冲突（读取/修改/写入冲突）"))
    # 429
    RATE_LIMIT_EXCEED = EnumField("RATE_LIMIT_EXCEED", label=_("超过频率限制"))
    RESOURCE_EXHAUSTED = EnumField("RESOURCE_EXHAUSTED", label=_("资源配额不足"))
    # 500
    INTERNAL = EnumField("INTERNAL", label=_("服务器内部错误"))
    UNKNOWN = EnumField("UNKNOWN", label=_("服务器未知错误"))
    # 501
    NOT_IMPLEMENTED = EnumField("NOT_IMPLEMENTED", label=_("功能未实现"))


class ErrorCodes:
    # 通用
    INVALID_ARGUMENT = ErrorCode(_("参数非法"))
    UNAUTHENTICATED = ErrorCode(
        _("未认证"),
        code_category=ErrorCodeCategoryEnum.UNAUTHENTICATED,
        status_code=HTTPStatus.UNAUTHORIZED,
    )
    NO_PERMISSION = ErrorCode(
        _("无权限"),
        code_category=ErrorCodeCategoryEnum.NO_PERMISSION,
        status_code=HTTPStatus.FORBIDDEN,
    )
    OBJECT_NOT_FOUND = ErrorCode(
        _("对象未找到"),
        code_category=ErrorCodeCategoryEnum.NOT_FOUND,
        status_code=HTTPStatus.NOT_FOUND,
    )
    VALIDATION_ERROR = ErrorCode(_("参数校验不通过"))
    SYSTEM_ERROR = ErrorCode(
        _("系统异常"),
        code_category=ErrorCodeCategoryEnum.INTERNAL,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )
    TOO_FREQUENTLY = ErrorCode(
        _("操作过于频繁"),
        code_category=ErrorCodeCategoryEnum.RATE_LIMIT_EXCEED,
        status_code=HTTPStatus.TOO_MANY_REQUESTS,
    )
    # 调用外部系统API
    REMOTE_REQUEST_ERROR = ErrorCode(_("调用外部系统API异常"))

    # 用户账密
    USERNAME_OR_PASSWORD_WRONG_ERROR = ErrorCode(_("用户名或密码错误"))

    # 数据源插件
    DATA_SOURCE_PLUGIN_NOT_DEFAULT_CONFIG = ErrorCode(_("当前数据源插件未提供默认配置"))

    # 数据源
    DATA_SOURCE_OPERATION_UNSUPPORTED = ErrorCode(_("当前数据源不支持该操作"))
    DATA_SOURCE_NOT_EXIST = ErrorCode(_("数据源不存在"))
    DATA_SOURCE_IMPORT_FAILED = ErrorCode(_("数据源导入失败"))
    DATA_SOURCE_SYNC_TASK_CREATE_FAILED = ErrorCode(_("创建数据源同步任务失败"))

    # 认证源
    IDP_PLUGIN_NOT_LOAD = ErrorCode(_("认证源插件未加载"))
    IDP_CREATE_FAILED = ErrorCode(_("创建认证源失败"))
    CANNOT_UPDATE_IDP = ErrorCode(_("该认证源不允许更新配置"))

    # 租户
    TENANT_UPDATE_FAILED = ErrorCode(_("租户更新失败"))
    TENANT_DELETE_FAILED = ErrorCode(_("租户删除失败"))
    GET_CURRENT_TENANT_FAILED = ErrorCode(_("无法找到当前用户所在租户"))

    # 协同策略
    COLLABORATION_STRATEGY_DISABLED_BY_SOURCE = ErrorCode(_("协同策略被分享方禁用"))
    COLLABORATION_STRATEGY_UPDATE_FAILED = ErrorCode(_("协同策略更新失败"))
    COLLABORATION_STRATEGY_DELETE_FAILED = ErrorCode(_("协同策略删除失败"))

    # 租户部门
    TENANT_DEPARTMENT_CREATE_FAILED = ErrorCode(_("租户部门创建失败"))
    TENANT_DEPARTMENT_UPDATE_FAILED = ErrorCode(_("租户部门更新失败"))
    TENANT_DEPARTMENT_DELETE_FAILED = ErrorCode(_("租户部门删除失败"))
    # 租户用户
    TENANT_USER_NOT_EXIST = ErrorCode(_("无法找到对应租户用户"))
    TENANT_USER_CREATE_FAILED = ErrorCode(_("租户用户创建失败"))
    TENANT_USER_UPDATE_FAILED = ErrorCode(_("租户用户更新失败"))
    TENANT_USER_DELETE_FAILED = ErrorCode(_("租户用户删除失败"))

    # 验证码
    INVALID_VERIFICATION_CODE = ErrorCode(_("验证码无效"))
    SEND_VERIFICATION_CODE_FAILED = ErrorCode(_("发送验证码失败"))
    SEND_RESET_PASSWORD_EMAIL_FAILED = ErrorCode(_("发送重置密码邮件失败"))


# 实例化一个全局对象
error_codes = ErrorCodes()

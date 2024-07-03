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
import logging
import re
from typing import Any, Dict

from django.conf import settings
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DATA_SOURCE_USERNAME_REGEX
from bkuser.apps.data_source.models import (
    DataSourceUser,
    DataSourceUserDeprecatedPasswordRecord,
    LocalDataSourceIdentityInfo,
)
from bkuser.apps.tenant.constants import TENANT_USER_CUSTOM_FIELD_NAME_REGEX, UserFieldDataType
from bkuser.apps.tenant.models import Tenant, TenantUserCustomField
from bkuser.common.hashers import check_password
from bkuser.common.passwd import PasswordValidator
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

logger = logging.getLogger(__name__)


def validate_data_source_user_username(value: str):
    if not re.fullmatch(DATA_SOURCE_USERNAME_REGEX, value):
        raise ValidationError(
            _(
                "{} 不符合 用户名 的命名规范: 由3-32位字母、数字、下划线(_)、点(.)、连接符(-)字符组成，以字母或数字开头及结尾",  # noqa: E501
            ).format(value),
        )


def validate_tenant_custom_field_name(value: str):
    if not re.fullmatch(TENANT_USER_CUSTOM_FIELD_NAME_REGEX, value):
        raise ValidationError(
            _(
                "{} 不符合 自定义字段 的命名规范: 由3-32位字母、数字、下划线(_)字符组成，以字母开头，字母或数字结尾",  # noqa: E501
            ).format(value),
        )


def validate_logo(value: str):
    if not value:
        return

    # 限制 Logo 格式为 png 或者 jpg
    if not re.match(r'^data:image\/(png|jpeg|jpg)', value):
        raise ValidationError(_("Logo 文件只能为 png 或 jpg 格式"))

    # Logo 使用 Base64 编码，编码后长度 ≈ 原始图片字节长度 // 3 * 4
    if len(value) > (settings.MAX_LOGO_SIZE * 1024) // 3 * 4:
        raise ValidationError(_("Logo 文件大小不可超过 {} KB").format(settings.MAX_LOGO_SIZE))


def validate_user_new_password(
    password: str, data_source_user_id: int, plugin_config: LocalDataSourcePluginConfig
) -> str:
    """校验新密码是否是可用的"""

    # 密码规则校验
    ret = PasswordValidator(plugin_config.password_rule.to_rule()).validate(password)  # type: ignore
    if not ret.ok:
        raise ValidationError(_("密码不符合规则：{}").format(ret.exception_message))

    # 不限制不能使用之前用过的密码，则不需要进行后续的检查
    if not plugin_config.password_initial.cannot_use_previous_password:  # type: ignore
        return password

    # 限制了不能与之前使用过的密码相同，则优先判断是否与当前密码相同
    identify_info = LocalDataSourceIdentityInfo.objects.get(user_id=data_source_user_id)
    if check_password(password, identify_info.password):
        raise ValidationError(_("新密码不能与当前密码相同"))

    # 根据配置的前面次数，进一步判断
    reserved_cnt = plugin_config.password_initial.reserved_previous_password_count  # type: ignore
    if reserved_cnt <= 1:
        # 当历史密码保留数量小于等于 1 时，只需要检查不与当前密码相同即可
        return password

    used_passwords = (
        DataSourceUserDeprecatedPasswordRecord.objects.filter(
            user_id=data_source_user_id,
        )
        .order_by("-id")[: reserved_cnt - 1]
        .values_list("password", flat=True)
    )

    for used_pwd in used_passwords:
        if check_password(password, used_pwd):
            raise ValidationError(_("新密码不能与近 {} 次使用的密码相同".format(reserved_cnt)))

    return password


def validate_duplicate_tenant_name(name: str, tenant_id: str = "") -> str:
    """检查租户是否重名"""
    queryset = Tenant.objects.filter(name=name)
    # 过滤掉自身名称
    if tenant_id:
        queryset = queryset.exclude(id=tenant_id)

    if queryset.exists():
        raise ValidationError(_("租户名 {} 已存在").format(name))

    return name


def _validate_type_and_convert_field_data(field: TenantUserCustomField, value: Any) -> Any:  # noqa: C901
    """对自定义字段的值进行类型检查 & 做必要的类型转换"""
    if value is None:
        # 必填性在后续进行检查，这里直接跳过即可
        return value

    opt_ids = [opt["id"] for opt in field.options]

    # 数字类型，转换成整型不丢精度就转，不行就浮点数
    if field.data_type == UserFieldDataType.NUMBER:
        try:
            value = float(value)  # type: ignore
            value = int(value) if int(value) == value else value  # type: ignore
        except ValueError:
            raise ValidationError(_("字段 {} 的值 {} 不是合法数字").format(field.display_name, value))

        return value

    # 枚举类型，值（id）必须是字符串，且是可选项中的一个
    if field.data_type == UserFieldDataType.ENUM:
        if value not in opt_ids:
            raise ValidationError(_("字段 {} 的值 {} 不是可选项之一").format(field.display_name, value))

        return value

    # 多选枚举类型，值必须是字符串列表，且是可选项的子集
    if field.data_type == UserFieldDataType.MULTI_ENUM:
        if not (value and isinstance(value, list)):
            raise ValidationError(_("多选枚举类型自定义字段值必须是非空列表"))

        if set(value) - set(opt_ids):
            raise ValidationError(_("字段 {} 的值 {} 不是可选项的子集").format(field.display_name, value))

        if len(value) != len(set(value)):
            raise ValidationError(_("字段 {} 的值 {} 中存在重复值").format(field.display_name, value))

        return value

    # 字符串类型，不需要做转换
    if field.data_type == UserFieldDataType.STRING:
        if not isinstance(value, str):
            raise ValidationError(_("字段 {} 的值 {} 不是字符串类型").format(field.display_name, value))

        return value.strip()

    raise ValidationError(_("字段类型 {} 不被支持").format(field.data_type))


def _validate_unique_and_required(
    field: TenantUserCustomField, data_source_id: int, data_source_user_id: int | None, value: Any
) -> Any:
    """对自定义字段的值进行唯一性检查 & 必填性检查"""
    if field.required and value in ["", None]:
        raise ValidationError(_("字段 {} 必须填值").format(field.display_name))

    if field.unique:
        # 唯一性检查，由于添加 / 修改用户一般不会有并发操作，因此这里没有对并发的情况进行预防
        queryset = DataSourceUser.objects.filter(data_source_id=data_source_id, **{f"extras__{field.name}": value})
        if data_source_user_id:
            queryset = queryset.exclude(id=data_source_user_id)

        if queryset.exists():
            raise ValidationError(_("字段 {} 的值 {} 不满足唯一性要求").format(field.display_name, value))

    return value


def validate_user_extras(
    extras: Dict[str, Any],
    custom_fields: QuerySet[TenantUserCustomField],
    data_source_id: int,
    data_source_user_id: int | None = None,
) -> Dict[str, Any]:
    """校验 extras 中的键，值是否合法"""
    if not custom_fields.exists() and extras:
        raise ValidationError(_("当前用户无可编辑的租户自定义字段"))

    if set(extras.keys()) != {field.name for field in custom_fields}:
        # Q：这里为什么不抛出具体的错误字段信息
        # A：这个校验是用于序列化器的，在前端逻辑正确的情况下，不会触发该异常，因此不暴露过多的错误信息
        raise ValidationError(_("提供的自定义字段数据与租户自定义字段不匹配"))

    for field in custom_fields:
        value = _validate_type_and_convert_field_data(field, extras[field.name])
        value = _validate_unique_and_required(field, data_source_id, data_source_user_id, value)
        extras[field.name] = value

    return extras

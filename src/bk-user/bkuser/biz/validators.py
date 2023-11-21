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
import logging
import re

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DATA_SOURCE_USERNAME_REGEX
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.plugins.local.constants import CUSTOM_FIELD_NAME_REGEX

logger = logging.getLogger(__name__)


def validate_data_source_user_username(value):
    if not re.fullmatch(DATA_SOURCE_USERNAME_REGEX, value):
        raise ValidationError(
            _(
                "{} 不符合 用户名 的命名规范: 由3-32位字母、数字、下划线(_)、点(.)、连接符(-)字符组成，以字母或数字开头及结尾"  # noqa: E501
            ).format(value),
        )


def validate_custom_field_exist(extras, custom_fields):
    # 非法自定义字段
    if set(extras.keys()) - set(custom_fields.values_list("name", flat=True)):
        raise ValidationError(_("存在非法自定义字段"))


def validate_custom_field_required(extras, custom_fields):
    # 必填检查
    required_fields = custom_fields.filter(required=True).values_list("name", flat=True)
    not_filled_fields = set(required_fields) - set(extras.keys())
    if not_filled_fields:
        raise ValidationError(_(f"必填字段未填写: {not_filled_fields}"))


def validate_custom_enum_field_value(extras, custom_fields):
    # 枚举类型，非法枚举值
    type_enum_fields = custom_fields.filter(data_type__in=[UserFieldDataType.ENUM, UserFieldDataType.MULTI_ENUM])
    for field in type_enum_fields:
        if field.name not in extras:
            continue

        value = extras[field.name]
        option_ids_list = [option["id"] for option in field.options]
        if field.data_type == UserFieldDataType.ENUM and value not in option_ids_list:
            raise ValidationError(_(f"非法单选枚举值: {value}"))

        if field.data_type == UserFieldDataType.MULTI_ENUM:
            if not isinstance(value, list):
                raise ValidationError(_(f"非法多选枚举值: 数据格式有问题 {value}"))

            if not set(value) - set(option_ids_list):
                raise ValidationError(_(f"非法多选枚举值: {value}"))


def validate_tenant_custom_field_name(value):
    if not re.fullmatch(CUSTOM_FIELD_NAME_REGEX, value):
        raise ValidationError(
            _(
                "{} 不符合 自定义字段 的命名规范: 由3-32位字母、数字、下划线(_)字符组成，以字母开头，字母或数字结尾"  # noqa: E501
            ).format(value),
        )

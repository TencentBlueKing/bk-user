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

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DATA_SOURCE_USERNAME_REGEX
from bkuser.apps.data_source.models import DataSourceUserDeprecatedPasswordRecord, LocalDataSourceIdentityInfo
from bkuser.apps.tenant.constants import TENANT_USER_CUSTOM_FIELD_NAME_REGEX
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

    # Logo 使用 Base64 编码，编码后长度 ≈ 原始图片字节长度 // 3 * 4
    if len(value) > (settings.MAX_LOGO_SIZE * 1024) // 3 * 4:
        raise ValidationError(_("Logo 文件大小不可超过 {} KB").format(settings.MAX_LOGO_SIZE))


def validate_user_password(password: str, data_source_user_id: int, plugin_config: LocalDataSourcePluginConfig) -> str:
    """校验新密码是否是可用的"""

    # 密码规则校验
    ret = PasswordValidator(plugin_config.password_rule.to_rule()).validate(password)  # type: ignore
    if not ret.ok:
        raise ValidationError(_("密码不符合规则：{}").format(ret.exception_message))

    # 不限制不能使用之前用过的密码，则不需要进行后续的检查
    if not plugin_config.password_initial.cannot_use_previous_password:  # type: ignore
        return password

    reserved_cnt = plugin_config.password_initial.reserved_previous_password_count  # type: ignore
    if reserved_cnt <= 1:
        # 当历史密码保留数量小于等于 1 时，只需要检查不与当前密码相同即可
        identify_info = LocalDataSourceIdentityInfo.objects.get(user_id=data_source_user_id)
        if check_password(password, identify_info.password):
            raise ValidationError(_("新密码不能与当前密码相同"))

        return password

    used_passwords = (
        DataSourceUserDeprecatedPasswordRecord.objects.filter(
            user_id=data_source_user_id,
        )
        .order_by("-created_at")[: reserved_cnt - 1]
        .values_list("password", flat=True)
    )

    for used_pwd in used_passwords:
        if check_password(password, used_pwd):
            raise ValidationError(_("新密码不能与近 {} 次使用的密码相同".format(reserved_cnt)))

    return password

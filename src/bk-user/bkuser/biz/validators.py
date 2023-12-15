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
import base64
import logging
import re

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DATA_SOURCE_USERNAME_REGEX
from bkuser.apps.tenant.constants import TENANT_USER_CUSTOM_FIELD_NAME_REGEX

logger = logging.getLogger(__name__)


def validate_data_source_user_username(value):
    if not re.fullmatch(DATA_SOURCE_USERNAME_REGEX, value):
        raise ValidationError(
            _(
                "{} 不符合 用户名 的命名规范: 由3-32位字母、数字、下划线(_)、点(.)、连接符(-)字符组成，以字母或数字开头及结尾"  # noqa: E501
            ).format(value),
        )


def validate_tenant_custom_field_name(value):
    if not re.fullmatch(TENANT_USER_CUSTOM_FIELD_NAME_REGEX, value):
        raise ValidationError(
            _(
                "{} 不符合 自定义字段 的命名规范: 由3-32位字母、数字、下划线(_)字符组成，以字母开头，字母或数字结尾"  # noqa: E501
            ).format(value),
        )


def validate_logo(value):
    if not value:
        return

    try:
        decoded_data = base64.b64decode(value)
    except Exception:
        # Decoding failed or invalid Base64-encoded image
        logger.exception("invalid image")
        raise ValidationError(_("无效logo文件"))

    # Check if the size exceeds the specified limit
    if len(decoded_data) > settings.MAX_LOGO_SIZE * 1024:
        raise ValidationError(_("logo 文件大小，不可超过{}KB").format(settings.MAX_LOGO_SIZE))

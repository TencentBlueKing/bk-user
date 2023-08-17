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

import phonenumbers
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from phonenumbers import region_code_for_country_code
from rest_framework import serializers

from bkuser.biz.validators import (
    validate_data_source_department_ids,
    validate_data_source_leader_ids,
    validate_data_source_user_username,
)

logger = logging.getLogger(__name__)
CHINESE_REGION = "CN"
CHINESE_PHONE_LENGTH = 11


class UserCreateInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名", validators=[validate_data_source_user_username])
    full_name = serializers.CharField(help_text="姓名")
    email = serializers.EmailField(help_text="邮箱")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )
    phone = serializers.CharField(help_text="手机号")
    logo = serializers.CharField(help_text="用户 Logo", required=False)
    department_ids = serializers.ListField(
        help_text="部门ID列表",
        child=serializers.IntegerField(),
        default=[],
        validators=[validate_data_source_department_ids],
    )
    leader_ids = serializers.ListField(
        help_text="上级ID列表",
        child=serializers.IntegerField(),
        default=[],
        validators=[validate_data_source_leader_ids],
    )

    def validate(self, data):
        # 根据国家码获取对应地区码
        try:
            region = region_code_for_country_code(int(data["phone_country_code"]))

        except Exception:
            logger.debug("failed to parse phone_country_code: %s, ", data["phone_country_code"])  # noqa: E501
            raise serializers.ValidationError(_("手机地区码 {} 不符合解析规则").format(data["phone_country_code"]))  # noqa: E501

        else:
            # phonenumbers库在验证号码的时：过短会解析为有效号码，超过250的字节才算超长
            # =》所以这里需要显式做中国号码的长度校验
            if region == CHINESE_REGION and len(data["phone"]) != CHINESE_PHONE_LENGTH:
                raise serializers.ValidationError(_("手机号 {} 不符合长度要求").format(data["phone"]))

            try:
                # 按照指定地区码解析手机号
                phonenumbers.parse(data["phone"], region)

            except Exception:  # pylint: disable=broad-except
                logger.debug("failed to parse phone number: %s", data["phone"])
                raise serializers.ValidationError(_("手机号 {} 不符合规则").format(data["phone"]))

        return data


class UserCreateOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="数据源用户ID")

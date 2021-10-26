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
import re

from bkuser_core.profiles.constants import DynamicFieldTypeEnum
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

USERNAME_REGEX = r"^(\d|[a-zA-Z])([a-zA-Z0-9._-]){0,31}"
DOMAIN_REGEX = r"^(\d|[a-zA-Z])([a-zA-Z0-9-.]){0,15}"
# for part domain which is not start with
DOMAIN_PART_REGEX = r"(\d|[a-zA-Z])([a-zA-Z0-9-.]){0,15}"


def validate_username(value):
    if not re.fullmatch(re.compile(USERNAME_REGEX), value):
        raise ValidationError(_("{} 不符合 username 命名规范: 由1-32位字母、数字、下划线(_)、点(.)、减号(-)字符组成，以字母或数字开头").format(value))


def validate_domain(value):
    if not re.fullmatch(re.compile(DOMAIN_REGEX), value):
        raise ValidationError(_("{} 不符合 domain 命名规范: 由1-16位字母、数字、点(.)、减号(-)字符组成，以字母或数字开头").format(value))


def validate_extras_value_unique(value: dict, category_id: int, profile_id: int = None):
    """
    检测 extras 中 value 是否是目录级别唯一
    非标准 validator，需要额外传入 category_id，且需要在 DB 实例创建前调用（若已创建，则必定抛出 ValidationError
    """
    from bkuser_core.profiles.models import DynamicFieldInfo, Profile

    fields = DynamicFieldInfo.objects.filter(
        name__in=value.keys(),
        unique=True,
        type__in=[DynamicFieldTypeEnum.STRING.value, DynamicFieldTypeEnum.NUMBER.value],
    )
    for f in fields:
        target_value = value.get(f.name)
        if not target_value:
            continue

        # extra() 需要注意 SQL 注入 https://docs.djangoproject.com/en/1.11/ref/models/querysets/#extra
        # 这里只检测该用户所处的目录中是否唯一
        # 同时这里需要保证 mysql 版本 >= 5.7
        queryset = Profile.objects.filter(enabled=True, category_id=category_id)
        if profile_id:
            queryset = queryset.exclude(pk=profile_id)

        for s in queryset.only("pk", "extras").extra(
            where=["JSON_SEARCH(extras, 'one', %s) is not null"], params=[target_value]
        ):
            # 防御: 可能存在部分旧数据并未添加所有 extra key
            if f.name not in s.extras:
                continue

            if s.extras[f.name] == target_value:
                raise ValidationError(
                    _("自定义字段 {} 需要保证唯一，而目录<id:{}>中已经存在值为 {} 的记录").format(f.display_name, category_id, target_value)
                )


BLACK_FIELD_NAMES = ["extras"]


def validate_dynamic_field_name(value: str):
    if value in BLACK_FIELD_NAMES:
        raise ValidationError(_("抱歉，{} 是系统字段保留字，请修改").format(value))

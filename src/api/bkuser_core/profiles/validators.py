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
import datetime
import logging
import re
from typing import Any, ClassVar, Dict, Tuple, Type

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from typing_extensions import Protocol

from bkuser_core.profiles.constants import DynamicFieldTypeEnum

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
                logging.info(
                    "profile<%s@%s> has the same value<%s> of field<%s-%s>",
                    s.username,
                    s.domain,
                    target_value,
                    f.name,
                    f.display_name,
                )
                raise ValidationError(
                    _("自定义字段 {} 需要保证唯一，而目录<id:{}>中已经存在值为 {} 的记录").format(f.display_name, category_id, target_value)
                )


class ExtrasValidator(Protocol):
    """自定义字段格式校验"""

    target_types: ClassVar[Tuple]
    transform_types: ClassVar[Tuple]

    @classmethod
    def validate(cls, value: Any, field_info):
        raise NotImplementedError


class ExtrasNumberValidator:
    target_types: ClassVar[Tuple] = (int, float)
    transform_types: ClassVar[Tuple] = (str,)

    @classmethod
    def validate(cls, value: Any, field_info):
        if isinstance(value, cls.target_types):
            return

        if isinstance(value, cls.transform_types):
            try:
                value = cls.transform(value)
                return value
            except Exception:
                raise ValidationError(_("{}不符合格式要求，无法转换".format(value)))

    @classmethod
    def transform(cls, value):
        """格式转换"""
        return float(value)


class ExtrasStringValidator:
    target_types: ClassVar[Tuple] = (str,)
    transform_types: ClassVar[Tuple] = ()

    @classmethod
    def validate(cls, value: Any, field_info):
        if isinstance(value, cls.target_types):
            return

        try:
            value = cls.transform(value)
            return value
        except Exception:
            raise ValidationError(_("{}不符合格式要求，无法转换".format(value)))

    @classmethod
    def transform(cls, value):
        """格式转换"""
        return str(value)


class ExtrasOneEnumValidator:
    target_types: ClassVar[Tuple] = (int,)
    transform_types: ClassVar[Tuple] = (str,)

    @classmethod
    def validate(cls, value: Any, field_info):
        enums = [enum[0] for enum in field_info.options]
        if isinstance(value, cls.target_types) and (value in enums):
            return

        if isinstance(value, cls.transform_types):
            try:
                value = cls.transform(value)
            except Exception:
                raise ValidationError(_("{}不符合格式要求，无法转换".format(value)))

            if value in enums:
                return value
            raise ValidationError(_("{}不在枚举范围内".format(value)))

    @classmethod
    def transform(cls, value):
        """格式转换"""
        return int(value)


class ExtrasMultiEnumValidator:
    target_types: ClassVar[Tuple] = (list,)
    transform_types: ClassVar[Tuple] = (str, set, tuple)

    @classmethod
    def validate(cls, value: Any, field_info):
        enums = [enum[0] for enum in field_info.options]
        if isinstance(value, cls.target_types) and (set(value) <= set(enums)):
            return
        if isinstance(value, cls.transform_types):
            try:
                value = cls.transform(value)
            except Exception:
                raise ValidationError(_("{} 不符合格式要求，无法转换".format(value)))

            if set(value) <= set(enums):
                return value
            raise ValidationError(_("{} 不在枚举范围内".format(value)))

    @classmethod
    def transform(cls, value):
        return list(value)


class ExtrasTimerValidator:
    target_types: ClassVar[Tuple] = (str,)
    transform_types: ClassVar[Tuple] = ()

    @classmethod
    def validate(cls, value: Any, field_info):
        if isinstance(value, cls.target_types):
            try:
                datetime.datetime.strptime(value, "%Y-%m-%d")
                return
            except Exception:
                raise ValidationError(_("{} 不符合格式要求".format(value)))
        raise ValidationError(_("{} 不符合格式要求".format(value)))


EXTRAS_VALIDATOR_MAP: Dict[DynamicFieldTypeEnum, Type[ExtrasValidator]] = {
    DynamicFieldTypeEnum.NUMBER.value: ExtrasNumberValidator,
    DynamicFieldTypeEnum.STRING.value: ExtrasStringValidator,
    DynamicFieldTypeEnum.ONE_ENUM.value: ExtrasOneEnumValidator,
    DynamicFieldTypeEnum.MULTI_ENUM.value: ExtrasMultiEnumValidator,
    DynamicFieldTypeEnum.TIMER.value: ExtrasTimerValidator,
}


def validate_extras_value_type(value: dict):
    """检测 extras 中 value 是否自定义字段规定的格式是否一致：不一致尝试进行转换"""
    from bkuser_core.profiles.models import DynamicFieldInfo

    dynamic_fields = DynamicFieldInfo.objects.filter(name__in=value.keys())
    for field in dynamic_fields:
        logging.info("going format dynamic field:{}, origin value:{}".format(field.name, value[field.name]))

        try:
            EXTRAS_VALIDATOR_MAP[field.type].validate(value=value[field.name], field_info=field)
        except Exception:
            logging.info("fail to format dynamic field:{}".format(field.name))
            value[field.name] = ""

    return value


BLACK_FIELD_NAMES = ["extras"]


def validate_dynamic_field_name(value: str):
    if value in BLACK_FIELD_NAMES:
        raise ValidationError(_("抱歉，{} 是系统字段保留字，请修改").format(value))

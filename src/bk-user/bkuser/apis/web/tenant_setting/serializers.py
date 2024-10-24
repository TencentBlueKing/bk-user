# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
import logging
from collections import Counter
from typing import Dict, List

from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError as PDValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.tenant.constants import NotificationMethod, NotificationScene, UserFieldDataType
from bkuser.apps.tenant.data_models import TenantUserCustomFieldOption
from bkuser.apps.tenant.models import TenantUserCustomField, UserBuiltinField
from bkuser.biz.validators import validate_tenant_custom_field_name

logger = logging.getLogger(__name__)


def _validate_options(options: List[Dict[str, str]]):
    """租户自定义字段，枚举类型字段<选项>设置校验"""
    if not options:
        raise ValidationError(_("需要提供至少一个枚举选项"))

    try:
        opts = [TenantUserCustomFieldOption(**opt) for opt in options]
    except PDValidationError as e:
        raise ValidationError(_("枚举选项不合法：{}".format(e)))

    # 判断重复枚举id
    option_ids = [obj.id for obj in opts]
    if duplicate_opt_ids := [opt_id for opt_id, cnt in Counter(option_ids).items() if cnt > 1]:
        raise ValidationError(_("存在重复枚举 ID：{}").format(duplicate_opt_ids))

    # 判断重复枚举值
    option_values = [obj.value for obj in opts]
    if duplicate_opt_vals := [opt_val for opt_val, cnt in Counter(option_values).items() if cnt > 1]:
        raise ValidationError(_("存在重复枚举值：{}").format(duplicate_opt_vals))


def _validate_enum_default(default: str, opt_ids: List[str]):
    """用户自定义字段：枚举类型的 <默认值> 字段校验"""
    if default not in opt_ids:
        raise ValidationError(_("枚举默认值 {} 需要是可选值 {} 之一").format(default, opt_ids))


def _validate_multi_enum_default(default: List[str], opt_ids: List[str]):
    """用户自定义字段：多选枚举类型的 <默认值> 字段校验"""
    if not isinstance(default, List):
        raise ValidationError(_("多选枚举类型自定义字段 默认值 必须是 列表类型"))

    if not (default and set(default).issubset(opt_ids)):
        raise ValidationError(_("多选枚举默认值 {} 不是可选值 {} 的子集").format(default, opt_ids))


class BuiltinFieldOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="字段ID", read_only=True)
    name = serializers.CharField(help_text="英文标识")
    display_name = serializers.CharField(help_text="展示用名称")
    data_type = serializers.ChoiceField(help_text="字段类型", choices=UserFieldDataType.get_choices())
    required = serializers.BooleanField(help_text="是否必填")
    unique = serializers.BooleanField(help_text="是否唯一")
    default = serializers.JSONField(help_text="默认值")
    options = serializers.JSONField(help_text="选项")


class TenantUserCustomFieldOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="字段ID", read_only=True)
    name = serializers.CharField(help_text="英文标识")
    display_name = serializers.CharField(help_text="展示用名称")
    data_type = serializers.ChoiceField(help_text="字段类型", choices=UserFieldDataType.get_choices())
    required = serializers.BooleanField(help_text="是否必填")
    unique = serializers.BooleanField(help_text="是否唯一")
    personal_center_visible = serializers.BooleanField(help_text="是否在个人中心可见")
    personal_center_editable = serializers.BooleanField(help_text="是否在个人中心可编辑")
    manager_editable = serializers.BooleanField(help_text="租户管理员是否可重复编辑")
    default = serializers.JSONField(help_text="默认值")
    options = serializers.JSONField(help_text="选项")


class TenantUserFieldOutputSLZ(serializers.Serializer):
    builtin_fields = serializers.ListField(help_text="内置字段", child=BuiltinFieldOutputSLZ())
    custom_fields = serializers.ListField(help_text="自定义字段", child=TenantUserCustomFieldOutputSLZ())


class OptionInputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="枚举ID")
    value = serializers.CharField(help_text="枚举值")


class TenantUserCustomFieldCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="英文标识", max_length=128, validators=[validate_tenant_custom_field_name])
    display_name = serializers.CharField(help_text="字段名称", max_length=128)
    data_type = serializers.ChoiceField(help_text="字段类型", choices=UserFieldDataType.get_choices())
    required = serializers.BooleanField(help_text="是否必填", default=False)
    unique = serializers.BooleanField(help_text="是否唯一", default=False)
    personal_center_visible = serializers.BooleanField(help_text="是否在个人中心可见", default=False)
    personal_center_editable = serializers.BooleanField(help_text="是否在个人中心可编辑", default=False)
    manager_editable = serializers.BooleanField(help_text="租户管理员是否可重复编辑", default=True)
    default = serializers.JSONField(help_text="默认值", required=False)
    options = serializers.ListField(
        help_text="选项", required=False, child=OptionInputSLZ(help_text="枚举字段选项设置"), default=list
    )

    def validate_display_name(self, display_name):
        if TenantUserCustomField.objects.filter(
            tenant_id=self.context["tenant_id"], display_name=display_name
        ).exists():
            raise ValidationError(_("字段名称 {} 已存在").format(display_name))

        if UserBuiltinField.objects.filter(display_name=display_name).exists():
            raise ValidationError(_("字段名称 {} 与内置字段冲突").format(display_name))

        return display_name

    def validate_name(self, name):
        if TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"], name=name).exists():
            raise ValidationError(_("英文标识 {} 已存在").format(name))

        if UserBuiltinField.objects.filter(name=name).exists():
            raise ValidationError(_("英文标识 {} 与内置字段冲突").format(name))

        return name

    def validate(self, attrs):
        data_type = attrs.get("data_type")
        options = attrs.get("options")
        default = attrs.get("default")

        if attrs["unique"] and data_type in [UserFieldDataType.ENUM, UserFieldDataType.MULTI_ENUM]:
            raise ValidationError(_("枚举类型字段不支持设置唯一性"))

        if data_type == UserFieldDataType.NUMBER:
            # 目前字段编辑，数字类型没有支持填写默认值，而模型默认是 ""
            # 无法在后续流程中做类型转换，因此这里修改默认值为 0
            attrs["default"] = 0

        opt_ids = [opt["id"] for opt in options]
        if data_type == UserFieldDataType.ENUM:
            _validate_options(options)
            _validate_enum_default(default, opt_ids)

        elif data_type == UserFieldDataType.MULTI_ENUM:
            _validate_options(options)
            _validate_multi_enum_default(default, opt_ids)

        if attrs["personal_center_editable"] and not attrs["personal_center_visible"]:
            raise ValidationError(_("设置为在个人中心可编辑的字段必须也设置可见"))

        return attrs


def _validate_mapping(mapping: Dict, current_options: List[Dict], new_options: List[Dict]):
    """校验数据迁移策略"""
    if not isinstance(mapping, Dict):
        raise ValidationError(_("字段迁移映射必须是字典类型，格式为：{被删除的枚举 ID: 迁移目标值枚举 ID}"))

    cur_opt_ids, new_opt_ids = {opt["id"] for opt in current_options}, {opt["id"] for opt in new_options}
    if (cur_opt_ids == new_opt_ids) and mapping:
        raise ValidationError(_("枚举选项没有修改，无需配置字段迁移映射"))

    # 对于被删除的枚举选项，需要确保已经配置了字段迁移映射
    if deleted_opt_ids := cur_opt_ids - new_opt_ids:  # noqa: SIM102 nested if is necessary
        if deleted_opt_ids != set(mapping.keys()):
            raise ValidationError(_("被删除的枚举项 {} 均需要配置字段迁移映射").format(deleted_opt_ids))

    # 对于字段迁移映射的目标值，需要确保都在新的枚举选项中
    if not_exists_target_ids := set(mapping.values()) - new_opt_ids:
        raise ValidationError(_("字段迁移映射的目标值 {} 不在新的枚举选项中").format(not_exists_target_ids))


class TenantUserCustomFieldUpdateInputSLZ(serializers.Serializer):
    display_name = serializers.CharField(help_text="展示用名称", max_length=128)
    default = serializers.JSONField(help_text="默认值", required=False)
    options = serializers.ListField(
        help_text="选项", required=False, child=OptionInputSLZ(help_text="枚举字段选项设置"), default=list
    )
    mapping = serializers.JSONField(help_text="字段迁移映射", required=False)

    def validate_display_name(self, display_name):
        if (
            TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"], display_name=display_name)
            .exclude(id=self.context["custom_field_id"])
            .exists()
        ):
            raise ValidationError(_("展示用名称 {} 已存在").format(display_name))

        if UserBuiltinField.objects.filter(display_name=display_name).exists():
            raise ValidationError(_("展示用名称 {} 与内置字段冲突").format(display_name))

        return display_name

    def validate(self, attrs):
        custom_field = TenantUserCustomField.objects.get(id=self.context["custom_field_id"])
        data_type = custom_field.data_type
        mapping = attrs.get("mapping")
        options = attrs.get("options")
        default = attrs.get("default")

        opt_ids = [opt["id"] for opt in options]
        if data_type == UserFieldDataType.ENUM:
            _validate_options(options)
            _validate_enum_default(default, opt_ids)
            _validate_mapping(mapping, custom_field.options, options)

        elif data_type == UserFieldDataType.MULTI_ENUM:
            _validate_options(options)
            _validate_multi_enum_default(default, opt_ids)
            _validate_mapping(mapping, custom_field.options, options)

        else:
            # 非枚举类型的，更新时候不需要字段迁移映射
            attrs["mapping"] = {}

        # NOTE: 对于历史迁移的数据，必须保证即使修改，选项 ID 也是可以转换回整数的（向前兼容）
        if custom_field.use_digit_option_id and options:
            for opt in options:
                if not opt["id"].isdigit():
                    raise ValidationError(_("枚举选项 ID 必须是数字，值 {} 不合法").format(opt["id"]))

        return attrs


class NotificationTemplatesInputSLZ(serializers.Serializer):
    method = serializers.ChoiceField(help_text="通知方式", choices=NotificationMethod.get_choices())
    scene = serializers.ChoiceField(help_text="通知场景", choices=NotificationScene.get_choices())
    title = serializers.CharField(help_text="通知标题", allow_null=True)
    sender = serializers.CharField(help_text="发送人")
    content = serializers.CharField(help_text="通知内容")
    content_html = serializers.CharField(help_text="通知内容，页面展示使用")


class TenantUserValidityPeriodConfigInputSLZ(serializers.Serializer):
    enabled = serializers.BooleanField(help_text="是否启用账户有效期")
    validity_period = serializers.IntegerField(help_text="账户有效期，单位：天")
    remind_before_expire = serializers.ListField(
        help_text="临过期提醒时间",
        child=serializers.IntegerField(min_value=1),
    )
    enabled_notification_methods = serializers.ListField(
        help_text="通知方式",
        child=serializers.ChoiceField(choices=NotificationMethod.get_choices()),
        allow_empty=False,
    )
    notification_templates = serializers.ListField(
        help_text="通知模板", child=NotificationTemplatesInputSLZ(), allow_empty=False
    )


class TenantUserValidityPeriodConfigOutputSLZ(TenantUserValidityPeriodConfigInputSLZ):
    pass

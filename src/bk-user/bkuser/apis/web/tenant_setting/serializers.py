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
from typing import List

from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError as PDValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.tenant.constants import NotificationMethod, NotificationScene, UserFieldDataType
from bkuser.apps.tenant.data_models import TenantUserCustomFieldOptions
from bkuser.apps.tenant.models import TenantUserCustomField, UserBuiltinField

logger = logging.getLogger(__name__)


def _validate_options(options):
    """用户自定义字段：<选项> 字段校验"""
    if not options:
        raise serializers.ValidationError(_("枚举类型的自定义字段需要传递非空的<选项>字段"))
    try:
        TenantUserCustomFieldOptions(options=options)
    except PDValidationError as e:
        raise serializers.ValidationError(_("<选项>字段不合法: {}".format(e)))


def _validate_enum_default(default: int, opt_ids: List[int]):
    """用户自定义字段：单枚举类型的 <默认值> 字段校验"""
    if not isinstance(default, int):
        raise ValidationError(_("枚举类型自定义字段的 default 值要传递整数类型"))

    # 单枚举类型要求 default 的值为 options 其中一个对象的 ID 值
    if not (default is None or default in opt_ids):
        raise serializers.ValidationError(_("默认值必须是 options 中对象的其中一个 id 值"))


def _validate_multi_enum_default(default: List[int], opt_ids: List[int]):
    """用户自定义字段：多选枚举类型的 <默认值> 字段校验"""
    if not isinstance(default, List):
        raise ValidationError(_("多选枚举类型自定义字段的 default 值需要传递列表类型"))

    # 多选枚举类型要求 default 中的值都为 options 其中任一对象的 ID 值
    if not (default is None or set(default).issubset(opt_ids)):
        raise serializers.ValidationError(_("默认值必须属于 options 中对象的 id 值"))


class BuiltinFieldOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="字段ID", read_only=True)
    name = serializers.CharField(help_text="字段名称")
    display_name = serializers.CharField(help_text="展示用名称")
    data_type = serializers.CharField(help_text="字段类型")
    required = serializers.BooleanField(help_text="是否必填")
    unique = serializers.BooleanField(help_text="是否唯一")
    default = serializers.JSONField(help_text="默认值")
    options = serializers.JSONField(help_text="选项")


class TenantUserCustomFieldOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="字段ID", read_only=True)
    name = serializers.CharField(help_text="字段名称")
    display_name = serializers.CharField(help_text="展示用名称")
    data_type = serializers.CharField(help_text="字段类型")
    required = serializers.BooleanField(help_text="是否必填")
    default = serializers.JSONField(help_text="默认值")
    options = serializers.JSONField(help_text="选项")


class TenantUserFieldOutputSLZ(serializers.Serializer):
    builtin_fields = serializers.ListField(help_text="内置字段", child=BuiltinFieldOutputSLZ())
    custom_fields = serializers.ListField(help_text="自定义字段", child=TenantUserCustomFieldOutputSLZ())


class TenantUserCustomFieldCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="字段名称", max_length=128)
    display_name = serializers.CharField(help_text="展示用名称", max_length=128)
    data_type = serializers.ChoiceField(help_text="字段类型", choices=UserFieldDataType.get_choices())
    required = serializers.BooleanField(help_text="是否必填")
    default = serializers.JSONField(help_text="默认值", required=False)
    options = serializers.JSONField(help_text="选项", required=False, default=list)

    def validate_display_name(self, display_name):
        if TenantUserCustomField.objects.filter(
            tenant_id=self.context["tenant_id"], display_name=display_name
        ).exists():
            raise serializers.ValidationError(_("展示用名称 {} 已存在").format(display_name))

        if UserBuiltinField.objects.filter(display_name=display_name).exists():
            raise serializers.ValidationError(_("展示用名称 {} 与内置字段冲突").format(display_name))

        return display_name

    def validate_name(self, name):
        if TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"], name=name).exists():
            raise serializers.ValidationError(_("字段名称 {} 已存在").format(name))

        if UserBuiltinField.objects.filter(name=name).exists():
            raise serializers.ValidationError(_("字段名称 {} 与内置字段冲突").format(name))

        return name

    def validate(self, attrs):
        data_type = attrs.get("data_type")
        options = attrs.get("options")
        default = attrs.get("default")

        opt_ids = [opt["id"] for opt in options]
        if data_type == UserFieldDataType.ENUM.value:
            _validate_options(options)
            _validate_enum_default(default, opt_ids)

        elif data_type == UserFieldDataType.MULTI_ENUM.value:
            _validate_options(options)
            _validate_multi_enum_default(default, opt_ids)

        return attrs


class TenantUserCustomFieldCreateOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField()


class TenantUserCustomFieldUpdateInputSLZ(serializers.Serializer):
    display_name = serializers.CharField(help_text="展示用名称", max_length=128)
    required = serializers.BooleanField(help_text="是否必填")
    default = serializers.JSONField(help_text="默认值", required=False)
    options = serializers.JSONField(help_text="选项", required=False, default=list)

    def validate_display_name(self, display_name):
        if (
            TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"], display_name=display_name)
            .exclude(id=self.context["current_custom_field_id"])
            .exists()
        ):
            raise serializers.ValidationError(_("展示用名称 {} 已存在").format(display_name))

        if UserBuiltinField.objects.filter(display_name=display_name).exists():
            raise serializers.ValidationError(_("展示用名称 {} 与内置字段冲突").format(display_name))

        return display_name

    def validate(self, attrs):
        current_custom_field = TenantUserCustomField.objects.get(id=self.context["current_custom_field_id"])
        data_type = current_custom_field.data_type
        options = attrs.get("options")
        default = attrs.get("default")

        opt_ids = [opt["id"] for opt in options]
        if data_type == UserFieldDataType.ENUM.value:
            _validate_options(options)
            _validate_enum_default(default, opt_ids)

        elif data_type == UserFieldDataType.MULTI_ENUM.value:
            _validate_options(options)
            _validate_multi_enum_default(default, opt_ids)

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

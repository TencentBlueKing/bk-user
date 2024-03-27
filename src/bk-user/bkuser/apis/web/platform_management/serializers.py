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
from typing import Any, Dict

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.notification.constants import NotificationMethod
from bkuser.apps.tenant.constants import TENANT_ID_REGEX, TenantStatus
from bkuser.apps.tenant.models import Tenant
from bkuser.biz.validators import validate_logo
from bkuser.common.passwd import PasswordValidator
from bkuser.common.validators import validate_phone_with_country_code
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig


class TenantListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名")
    status = serializers.CharField(help_text="租户状态")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")
    is_default = serializers.BooleanField(help_text="是否默认租户")
    created_at = serializers.CharField(help_text="创建时间", source="created_at_display")

    class Meta:
        ref_name = "platform_management.TenantListOutputSLZ"

    def get_logo(self, obj: Tenant) -> str:
        return obj.logo or settings.DEFAULT_TENANT_LOGO


def _validate_duplicate_tenant_name(name: str, tenant_id: str = "") -> str:
    """检查租户是否重名"""
    queryset = Tenant.objects.filter(name=name)
    # 过滤掉自身名称
    if tenant_id:
        queryset = queryset.exclude(id=tenant_id)

    if queryset.exists():
        raise ValidationError(_("租户名 {} 已存在").format(name))

    return name


def _validate_fixed_password(fixed_password: str) -> str:
    cfg: LocalDataSourcePluginConfig = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL)  # type: ignore
    ret = PasswordValidator(cfg.password_rule.to_rule()).validate(fixed_password)  # type: ignore
    if not ret.ok:
        raise ValidationError(_("密码不符合密码规则：{}").format(ret.exception_message))

    return fixed_password


def _validate_notification(notification_method: str, email: str, phone: str, phone_country_code: str):
    """通知参数校验"""
    # 根据选择的通知方式，校验通知账号信息
    if notification_method == NotificationMethod.EMAIL and not email:
        raise ValidationError(_("选择邮箱通知方式时，邮箱不能为空"))

    if notification_method == NotificationMethod.SMS:
        if not phone:
            raise ValidationError(_("选择短信通知方式时，手机号不能为空"))
        # 校验手机号是否合法
        try:
            validate_phone_with_country_code(phone=phone, country_code=phone_country_code)
        except ValueError as e:
            raise ValidationError(str(e))


class TenantCreateInputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.CharField(
        help_text="租户 Logo",
        required=False,
        allow_blank=True,
        default=settings.DEFAULT_TENANT_LOGO,
        validators=[validate_logo],
    )
    status = serializers.ChoiceField(help_text="租户状态", choices=TenantStatus.get_choices())
    # [内置管理]类型的本地数据源配置
    fixed_password = serializers.CharField(help_text="固定初始密码")
    notification_method = serializers.ChoiceField(help_text="通知方式", choices=NotificationMethod.get_choices())
    # 内置管理账号信息
    email = serializers.EmailField(help_text="管理员邮箱", required=False, default="", allow_blank=True)
    phone = serializers.CharField(help_text="管理员手机号", required=False, default="", allow_blank=True)
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE, allow_blank=True
    )

    def validate_id(self, id: str) -> str:
        if Tenant.objects.filter(id=id).exists():
            raise ValidationError(_("租户 ID {} 已被使用").format(id))

        if not re.fullmatch(TENANT_ID_REGEX, id):
            raise ValidationError(
                _(
                    "{} 不符合 租户 ID 的命名规范: 由3-32位字母、数字、连接符(-)字符组成，以字母开头，字母或数字结尾",
                ).format(id),
            )  # noqa: E501

        return id

    def validate_name(self, name: str) -> str:
        return _validate_duplicate_tenant_name(name)

    def validate_fixed_password(self, fixed_password: str) -> str:
        return _validate_fixed_password(fixed_password)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 校验通知信息是否正确
        _validate_notification(
            attrs["notification_method"], attrs["email"], attrs["phone"], attrs["phone_country_code"]
        )
        return attrs


class TenantCreateOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")


class TenantRetrieveBuiltinManagementUserOutputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名")


class TenantRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")

    def get_logo(self, obj: Tenant) -> str:
        return obj.logo or settings.DEFAULT_TENANT_LOGO


class TenantUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.CharField(
        help_text="租户 Logo",
        required=False,
        allow_blank=True,
        default=settings.DEFAULT_TENANT_LOGO,
        validators=[validate_logo],
    )

    def validate_name(self, name: str) -> str:
        return _validate_duplicate_tenant_name(name, self.context["tenant_id"])


class TenantStatusUpdateOutputSLZ(serializers.Serializer):
    status = serializers.CharField(help_text="租户状态")


class TenantBuiltinManagerRetrieveOutputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名")


class TenantRelatedResourceStatsOutputSLZ(serializers.Serializer):
    data_source_count = serializers.IntegerField(help_text="数据源数量")
    data_source_user_count = serializers.IntegerField(help_text="数据源用户数量")
    data_source_department_count = serializers.IntegerField(help_text="数据源部门数量")
    tenant_count = serializers.IntegerField(help_text="关联租户数量（含归属 / 协同）")
    tenant_user_count = serializers.IntegerField(help_text="租户用户数量")
    tenant_department_count = serializers.IntegerField(help_text="租户部门数量")


class TenantBuiltinManagerUpdateOutputSLZ(serializers.Serializer):
    # [内置管理]类型的本地数据源配置
    fixed_password = serializers.CharField(help_text="固定初始密码")
    notification_method = serializers.ChoiceField(help_text="通知方式", choices=NotificationMethod.get_choices())
    # 内置管理账号信息
    email = serializers.EmailField(help_text="管理员邮箱", required=False, default="", allow_blank=True)
    phone = serializers.CharField(help_text="管理员手机号", required=False, default="", allow_blank=True)
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE, allow_blank=True
    )

    def validate_fixed_password(self, fixed_password: str) -> str:
        return _validate_fixed_password(fixed_password)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 校验通知信息是否正确
        _validate_notification(
            attrs["notification_method"], attrs["email"], attrs["phone"], attrs["phone_country_code"]
        )
        return attrs

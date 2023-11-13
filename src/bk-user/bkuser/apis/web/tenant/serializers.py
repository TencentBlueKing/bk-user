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
from typing import Any, Dict, List

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from pydantic import ValidationError as PDValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.constants import TENANT_ID_REGEX
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.biz.data_source import DataSourceSimpleInfo
from bkuser.biz.data_source_plugin import DefaultPluginConfigProvider
from bkuser.biz.tenant import TenantUserWithInheritedInfo
from bkuser.biz.validators import validate_data_source_user_username
from bkuser.common.passwd import PasswordValidator
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.constants import PasswordGenerateMethod
from bkuser.plugins.local.models import LocalDataSourcePluginConfig, NotificationConfig
from bkuser.utils.pydantic import stringify_pydantic_error


class TenantManagerCreateInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="管理员用户名", validators=[validate_data_source_user_username])
    full_name = serializers.CharField(help_text="管理员姓名")
    email = serializers.EmailField(help_text="管理员邮箱")
    # TODO: 手机号&区号补充校验
    phone = serializers.CharField(help_text="管理员手机号")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )


class TenantFeatureFlagSLZ(serializers.Serializer):
    user_number_visible = serializers.BooleanField(help_text="人员数量是否可见", default=True)


class TenantManagerPasswordInitialConfigSLZ(serializers.Serializer):
    force_change_at_first_login = serializers.BooleanField(help_text="首次登录后强制修改密码", default=True)
    cannot_use_previous_password = serializers.BooleanField(help_text="修改密码时候不能使用之前的密码", default=True)
    reserved_previous_password_count = serializers.IntegerField(
        help_text="之前的 N 个密码不能被本次修改使用",
        default=3,
    )
    generate_method = serializers.ChoiceField(help_text="密码生成方式", choices=PasswordGenerateMethod.get_choices())
    fixed_password = serializers.CharField(
        help_text="固定初始密码", required=False, allow_null=True, allow_blank=True, default=None
    )
    notification = serializers.JSONField(help_text="通知相关配置")

    def validate_fixed_password(self, fixed_password: str) -> str:
        if not fixed_password:
            return fixed_password

        cfg: LocalDataSourcePluginConfig = DefaultPluginConfigProvider().get(  # type: ignore
            DataSourcePluginEnum.LOCAL,
        )
        ret = PasswordValidator(cfg.password_rule.to_rule()).validate(fixed_password)  # type: ignore
        if not ret.ok:
            raise ValidationError(_("固定密码的值不符合密码规则：{}").format(ret.exception_message))

        return fixed_password

    def validate_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        try:
            NotificationConfig(**notification)
        except PDValidationError as e:
            raise ValidationError(_("通知配置不合法：{}").format(stringify_pydantic_error(e)))

        return notification


class TenantCreateInputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.CharField(help_text="租户 Logo", required=False, allow_blank=True, default="")
    managers = serializers.ListField(help_text="管理人列表", child=TenantManagerCreateInputSLZ(), allow_empty=False)
    feature_flags = TenantFeatureFlagSLZ(help_text="租户特性集")
    password_initial_config = TenantManagerPasswordInitialConfigSLZ()

    def validate_id(self, id: str) -> str:
        if Tenant.objects.filter(id=id).exists():
            raise ValidationError(_("租户 ID {} 已被使用").format(id))

        if not re.fullmatch(TENANT_ID_REGEX, id):
            raise ValidationError(
                _("{} 不符合 租户ID 的命名规范: 由3-32位字母、数字、连接符(-)字符组成，以字母开头").format(id)
            )  # noqa: E501

        return id

    def validate_name(self, name: str) -> str:
        if Tenant.objects.filter(name=name).exists():
            raise ValidationError(_("租户名 {} 已存在").format(name))

        return name


class TenantCreateOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")


class TenantSearchInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="租户名", required=False, allow_blank=True)


class TenantSearchManagerOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="姓名")


class TenantSearchDataSourceOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="数据源 ID")
    name = serializers.CharField(help_text="数据源名称")


class TenantSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")
    created_at = serializers.SerializerMethodField(help_text="创建时间")
    managers = serializers.SerializerMethodField(help_text="租户管理员")
    data_sources = serializers.SerializerMethodField(help_text="租户数据源")

    def get_logo(self, obj: Tenant) -> str:
        return obj.logo or settings.DEFAULT_TENANT_LOGO

    def get_created_at(self, obj: Tenant) -> str:
        return obj.created_at_display

    @swagger_serializer_method(serializer_or_field=TenantSearchManagerOutputSLZ(many=True))
    def get_managers(self, obj: Tenant) -> List[Dict]:
        tenant_manager_map: Dict[str, List[TenantUserWithInheritedInfo]] = self.context["tenant_manager_map"]
        managers = tenant_manager_map.get(obj.id) or []
        return [
            {
                "id": i.id,
                **i.data_source_user.model_dump(include={"username", "full_name"}),
            }
            for i in managers
        ]

    @swagger_serializer_method(serializer_or_field=TenantSearchDataSourceOutputSLZ(many=True))
    def get_data_sources(self, obj: Tenant) -> List[Dict]:
        data_source_map: Dict[str, List[DataSourceSimpleInfo]] = self.context["data_source_map"]
        data_sources = data_source_map.get(obj.id) or []
        return [i.model_dump(include={"id", "name"}) for i in data_sources]


class TenantUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.CharField(
        help_text="租户 Logo", required=False, allow_blank=True, default=settings.DEFAULT_TENANT_LOGO
    )
    manager_ids = serializers.ListField(child=serializers.CharField(), help_text="租户用户 ID 列表", allow_empty=False)
    feature_flags = TenantFeatureFlagSLZ(help_text="租户特性集")


class TenantRetrieveManagerOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="租户用户名")
    full_name = serializers.CharField(help_text="用户姓名")
    email = serializers.EmailField(help_text="用户邮箱")
    phone = serializers.CharField(help_text="用户手机号")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )


class TenantRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名")
    updated_at = serializers.SerializerMethodField(help_text="更新时间")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")
    feature_flags = TenantFeatureFlagSLZ(help_text="租户特性集")
    managers = serializers.SerializerMethodField(help_text="租户管理员")

    @swagger_serializer_method(serializer_or_field=TenantRetrieveManagerOutputSLZ(many=True))
    def get_managers(self, obj: Tenant) -> List[Dict]:
        tenant_manager_map: Dict[str, List[TenantUserWithInheritedInfo]] = self.context["tenant_manager_map"]
        managers = tenant_manager_map.get(obj.id) or []
        return [
            {
                "id": i.id,
                **i.data_source_user.model_dump(
                    include={"username", "full_name", "email", "phone", "phone_country_code"}
                ),
            }
            for i in managers
        ]

    def get_logo(self, obj: Tenant) -> str:
        return obj.logo or settings.DEFAULT_TENANT_LOGO

    def get_updated_at(self, obj: Tenant) -> str:
        return obj.updated_at_display


class TenantUserSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False)


class TenantUserSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="租户用户名", required=False)
    full_name = serializers.CharField(help_text="用户姓名", required=False)
    email = serializers.EmailField(help_text="用户邮箱", required=False)
    phone = serializers.CharField(help_text="用户手机号", required=False)
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )

    def to_representation(self, instance: TenantUser) -> Dict:
        data = super().to_representation(instance)
        data_source_user = DataSourceUser.objects.filter(id=instance.data_source_user_id).first()
        if data_source_user is not None:
            data["username"] = data_source_user.username
            data["full_name"] = data_source_user.full_name
            data["email"] = data_source_user.email
            data["phone"] = data_source_user.phone
            data["phone_country_code"] = data_source_user.phone_country_code
            data["logo"] = data_source_user.logo or settings.DEFAULT_DATA_SOURCE_USER_LOGO

        return data

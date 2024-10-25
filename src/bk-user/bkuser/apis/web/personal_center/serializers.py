# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
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

from typing import Any, Dict, List

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apis.web.personal_center.constants import PhoneOrEmailUpdateRestrictionEnum
from bkuser.apis.web.tenant_setting.serializers import BuiltinFieldOutputSLZ
from bkuser.apps.data_source.models import (
    DataSourceDepartmentUserRelation,
    DataSourceUserLeaderRelation,
    LocalDataSourceIdentityInfo,
)
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantDepartment, TenantUser, TenantUserCustomField
from bkuser.biz.validators import validate_logo, validate_user_extras, validate_user_new_password
from bkuser.common.constants import TIME_ZONE_CHOICES, BkLanguageEnum
from bkuser.common.desensitize import desensitize_email, desensitize_phone
from bkuser.common.hashers import check_password
from bkuser.common.validators import validate_phone_with_country_code


class TenantInfoSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名称")


class TenantUserInfoSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户 ID")
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="姓名")
    logo = serializers.CharField(help_text="头像")
    tenant = TenantInfoSLZ(help_text="租户")

    class Meta:
        ref_name = "personal_center.TenantUserInfoSLZ"


class NaturalUserWithTenantUserListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="自然人ID")
    full_name = serializers.CharField(help_text="自然人姓名")
    tenant_users = serializers.ListField(help_text="自然人关联的租户账号列表", child=TenantUserInfoSLZ())


class TenantUserDepartmentSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户部门 ID")
    name = serializers.CharField(help_text="租户部门名称", source="data_source_department.name")

    class Meta:
        ref_name = "personal_center.TenantUserDepartmentSLZ"


class TenantUserLeaderSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户 ID")
    username = serializers.CharField(help_text="租户用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="租户用户名称", source="data_source_user.full_name")

    class Meta:
        ref_name = "personal_center.TenantUserLeaderSLZ"


class TenantUserRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户 ID")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    logo = serializers.CharField(help_text="头像", source="data_source_user.logo")

    # 邮箱信息
    is_inherited_email = serializers.BooleanField(help_text="是否继承数据源邮箱")
    email = serializers.SerializerMethodField(help_text="用户邮箱")
    custom_email = serializers.SerializerMethodField(help_text="自定义用户邮箱")

    # 手机号信息
    is_inherited_phone = serializers.BooleanField(help_text="是否继承数据源手机号")
    phone = serializers.SerializerMethodField(help_text="用户手机号")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号",
        source="data_source_user.phone_country_code",
        default=settings.DEFAULT_PHONE_COUNTRY_CODE,
    )
    custom_phone = serializers.SerializerMethodField(help_text="自定义用户手机号")
    custom_phone_country_code = serializers.CharField(help_text="自定义用户手机国际区号")

    account_expired_at = serializers.DateTimeField(help_text="账号过期时间")
    departments = serializers.SerializerMethodField(help_text="用户所属部门")
    leaders = serializers.SerializerMethodField(help_text="用户上级")
    extras = serializers.SerializerMethodField(help_text="自定义字段")

    # 语言与时区信息
    language = serializers.ChoiceField(help_text="语言", choices=BkLanguageEnum.get_choices())
    time_zone = serializers.ChoiceField(help_text="时区", choices=TIME_ZONE_CHOICES)

    class Meta:
        ref_name = "personal_center.TenantUserRetrieveOutputSLZ"

    @swagger_serializer_method(serializer_or_field=TenantUserDepartmentSLZ(many=True))
    def get_departments(self, obj: TenantUser) -> List[Dict]:
        relations = DataSourceDepartmentUserRelation.objects.filter(user_id=obj.data_source_user_id)
        if not relations.exists():
            return []

        depts = TenantDepartment.objects.filter(
            tenant_id=obj.tenant_id, data_source_department_id__in=[rel.department_id for rel in relations]
        ).select_related("data_source_department")

        return TenantUserDepartmentSLZ(depts, many=True).data

    @swagger_serializer_method(serializer_or_field=TenantUserLeaderSLZ(many=True))
    def get_leaders(self, obj: TenantUser) -> List[Dict]:
        relations = DataSourceUserLeaderRelation.objects.filter(user_id=obj.data_source_user_id)
        if not relations.exists():
            return []

        leaders = TenantUser.objects.filter(
            tenant_id=obj.tenant_id, data_source_user_id__in=[rel.leader_id for rel in relations]
        ).select_related("data_source_user")

        return TenantUserLeaderSLZ(leaders, many=True).data

    @swagger_serializer_method(serializer_or_field=serializers.JSONField)
    def get_extras(self, obj: TenantUser) -> Dict[str, Any]:
        # 过滤掉 extras 中用户在个人中心不可见的自定义字段
        return {
            k: v for k, v in obj.data_source_user.extras.items() if k in self.context["visible_custom_field_names"]
        }

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_email(self, obj: TenantUser) -> str:
        return desensitize_email(obj.data_source_user.email)

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_custom_email(self, obj: TenantUser) -> str:
        return desensitize_email(obj.custom_email)

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_phone(self, obj: TenantUser) -> str:
        return desensitize_phone(obj.data_source_user.phone)

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_custom_phone(self, obj: TenantUser) -> str:
        return desensitize_phone(obj.custom_phone)


class TenantUserPhoneUpdateInputSLZ(serializers.Serializer):
    is_inherited_phone = serializers.BooleanField(help_text="是否继承数据源手机号")
    custom_phone = serializers.CharField(help_text="用户自定义手机号", required=False, allow_blank=True)
    custom_phone_country_code = serializers.CharField(
        help_text="用户自定义手机国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )
    verification_code = serializers.CharField(
        help_text="手机号验证码", required=False, allow_blank=True, max_length=32
    )

    def validate(self, attrs):
        # custom_phone_country_code 具有默认值
        # 不通过继承，则需校验手机号，custom_phone 必须存在
        if not attrs["is_inherited_phone"]:
            if not attrs.get("custom_phone"):
                raise ValidationError(_("自定义手机号码为必填项"))
            try:
                validate_phone_with_country_code(attrs["custom_phone"], attrs["custom_phone_country_code"])
            except ValueError as e:
                raise ValidationError(str(e))

        return attrs


class TenantUserEmailUpdateInputSLZ(serializers.Serializer):
    is_inherited_email = serializers.BooleanField(help_text="是否继承数据源邮箱")
    custom_email = serializers.EmailField(help_text="用户自定义邮箱", required=False, allow_blank=True)
    verification_code = serializers.CharField(help_text="邮箱验证码", required=False, allow_blank=True, max_length=32)

    def validate(self, attrs):
        # 不通过继承，custom_email 必须存在
        if not attrs["is_inherited_email"] and not attrs.get("custom_email"):
            raise ValidationError(_("自定义邮箱为必填项"))

        return attrs


class TenantUserLanguageUpdateInputSLZ(serializers.Serializer):
    language = serializers.ChoiceField(help_text="语言", choices=BkLanguageEnum.get_choices())


class TenantUserTimeZoneUpdateInputSLZ(serializers.Serializer):
    time_zone = serializers.ChoiceField(help_text="时区", choices=TIME_ZONE_CHOICES)


class TenantUserLogoUpdateInputSLZ(serializers.Serializer):
    logo = serializers.CharField(help_text="用户 Logo", validators=[validate_logo])


class TenantUserExtrasUpdateInputSLZ(serializers.Serializer):
    extras = serializers.JSONField(help_text="自定义字段")

    def validate_extras(self, extras: Dict[str, Any]) -> Dict[str, Any]:
        custom_fields = TenantUserCustomField.objects.filter(
            tenant_id=self.context["tenant_id"],
            personal_center_editable=True,
            # 允许仅更新部分 Extras 字段
            name__in=extras.keys(),
        )
        return validate_user_extras(
            extras, custom_fields, self.context["data_source_id"], self.context["data_source_user_id"]
        )


class TenantUserCustomFieldOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="字段 ID")
    name = serializers.CharField(help_text="英文标识")
    display_name = serializers.CharField(help_text="展示用名称")
    data_type = serializers.ChoiceField(help_text="字段类型", choices=UserFieldDataType.get_choices())
    required = serializers.BooleanField(help_text="是否必填")
    editable = serializers.BooleanField(help_text="是否可编辑", source="personal_center_editable")
    options = serializers.JSONField(help_text="可选项")

    class Meta:
        ref_name = "personal_center.TenantUserCustomFieldOutputSLZ"


class TenantUserFieldOutputSLZ(serializers.Serializer):
    builtin_fields = serializers.ListField(help_text="内置字段", child=BuiltinFieldOutputSLZ())
    custom_fields = serializers.ListField(help_text="自定义字段", child=TenantUserCustomFieldOutputSLZ())

    class Meta:
        ref_name = "personal_center.TenantUserFieldOutputSLZ"


class TenantUserFeatureFlagOutputSLZ(serializers.Serializer):
    can_change_password = serializers.BooleanField(help_text="修改密码")
    phone_update_restriction = serializers.ChoiceField(
        help_text="修改手机号权限", choices=PhoneOrEmailUpdateRestrictionEnum.get_choices()
    )
    email_update_restriction = serializers.ChoiceField(
        help_text="修改邮箱权限", choices=PhoneOrEmailUpdateRestrictionEnum.get_choices()
    )


class TenantUserPasswordUpdateInputSLZ(serializers.Serializer):
    old_password = serializers.CharField(help_text="旧密码", max_length=128)
    new_password = serializers.CharField(help_text="新密码", max_length=128)

    def validate(self, attrs):
        data_source_user_id = self.context["data_source_user_id"]

        identify_info = LocalDataSourceIdentityInfo.objects.get(user_id=data_source_user_id)
        if not check_password(attrs["old_password"], identify_info.password):
            raise ValidationError(_("旧密码校验失败"))

        validate_user_new_password(
            password=attrs["new_password"],
            data_source_user_id=data_source_user_id,
            plugin_config=self.context["plugin_config"],
        )

        return attrs


class TenantUserPhoneVerificationCodeSendInputSLZ(serializers.Serializer):
    phone = serializers.CharField(help_text="用户手机号")
    phone_country_code = serializers.CharField(
        help_text="用户手机国际区号", default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )

    def validate(self, attrs):
        try:
            validate_phone_with_country_code(attrs["phone"], attrs["phone_country_code"])
        except ValueError as e:
            raise ValidationError(str(e))

        return attrs


class TenantUserEmailVerificationCodeSendInputSLZ(serializers.Serializer):
    email = serializers.EmailField(help_text="用户邮箱")

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
from typing import Any, Dict, List

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apis.web.data_source_organization.serializers import validate_user_extras
from bkuser.apis.web.organization.serializers import TenantUserDepartmentOutputSLZ, TenantUserLeaderOutputSLZ
from bkuser.apis.web.tenant_setting.serializers import BuiltinFieldOutputSLZ
from bkuser.apps.tenant.models import TenantUser, TenantUserCustomField
from bkuser.biz.tenant import TenantUserHandler
from bkuser.biz.validators import validate_logo, validate_password
from bkuser.common.validators import validate_phone_with_country_code


class TenantInfoOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名称")


class TenantUserInfoOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户 ID")
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="姓名")
    logo = serializers.CharField(help_text="头像")
    tenant = TenantInfoOutputSLZ(help_text="租户")


class NaturalUserWithTenantUserListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="自然人ID")
    full_name = serializers.CharField(help_text="自然人姓名")
    tenant_users = serializers.ListField(help_text="自然人关联的租户账号列表", child=TenantUserInfoOutputSLZ())


class TenantUserRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户 ID")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    logo = serializers.CharField(help_text="头像", source="data_source_user.logo")

    # 邮箱信息
    is_inherited_email = serializers.BooleanField(help_text="是否继承数据源邮箱")
    email = serializers.EmailField(help_text="用户邮箱", source="data_source_user.email")
    custom_email = serializers.EmailField(help_text="自定义用户邮箱")

    # 手机号信息
    is_inherited_phone = serializers.BooleanField(help_text="是否继承数据源手机号")
    phone = serializers.CharField(help_text="用户手机号", source="data_source_user.phone")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号",
        source="data_source_user.phone_country_code",
        default=settings.DEFAULT_PHONE_COUNTRY_CODE,
    )
    custom_phone = serializers.CharField(help_text="自定义用户手机号")
    custom_phone_country_code = serializers.CharField(help_text="自定义用户手机国际区号")

    account_expired_at = serializers.CharField(help_text="账号过期时间", source="account_expired_at_display")
    departments = serializers.SerializerMethodField(help_text="用户所属部门")
    leaders = serializers.SerializerMethodField(help_text="用户上级")
    extras = serializers.SerializerMethodField(help_text="自定义字段")

    class Meta:
        ref_name = "personal_center.TenantUserRetrieveOutputSLZ"

    @swagger_serializer_method(serializer_or_field=TenantUserDepartmentOutputSLZ(many=True))
    def get_departments(self, obj: TenantUser) -> List[Dict]:
        tenant_user_depts_map = TenantUserHandler.get_tenant_users_depts_map(obj.tenant_id, [obj])
        depts = tenant_user_depts_map.get(obj.id) or []
        return TenantUserDepartmentOutputSLZ(depts, many=True).data

    @swagger_serializer_method(serializer_or_field=TenantUserLeaderOutputSLZ(many=True))
    def get_leaders(self, obj: TenantUser) -> List[Dict]:
        tenant_users_leader_infos = TenantUserHandler.get_tenant_user_leader_infos(obj)
        return TenantUserLeaderOutputSLZ(tenant_users_leader_infos, many=True).data

    @swagger_serializer_method(serializer_or_field=serializers.JSONField)
    def get_extras(self, obj: TenantUser) -> Dict[str, Any]:
        # 过滤掉 extras 中用户在个人中心不可见的自定义字段
        return {
            k: v for k, v in obj.data_source_user.extras.items() if k in self.context["visible_custom_field_names"]
        }


class TenantUserPhoneUpdateInputSLZ(serializers.Serializer):
    is_inherited_phone = serializers.BooleanField(help_text="是否继承数据源手机号", required=True)
    custom_phone = serializers.CharField(help_text="自定义用户手机号", required=False, allow_blank=True)
    custom_phone_country_code = serializers.CharField(
        help_text="自定义用户手机国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )

    def validate(self, attrs):
        # custom_phone_country_code 具有默认值
        # 不通过继承，则需校验手机号，custom_phone 必须存在
        if not attrs["is_inherited_phone"]:
            if not attrs.get("custom_phone"):
                raise ValidationError(_("自定义手机号码为必填项"))

            if "+" in attrs["custom_phone_country_code"]:
                raise ValidationError(_("区号设置无需携带标识:'+'"))

            try:
                validate_phone_with_country_code(
                    phone=attrs["custom_phone"], country_code=attrs["custom_phone_country_code"]
                )
            except ValueError as e:
                raise ValidationError(str(e))

        return attrs


class TenantUserEmailUpdateInputSLZ(serializers.Serializer):
    is_inherited_email = serializers.BooleanField(help_text="是否继承数据源邮箱", required=True)
    custom_email = serializers.EmailField(help_text="自定义用户邮箱", required=False, allow_blank=True)

    def validate(self, attrs):
        # 不通过继承，custom_email 必须存在
        if not attrs["is_inherited_email"] and not attrs.get("custom_email"):
            raise ValidationError(_("自定义邮箱为必填项"))

        return attrs


class TenantUserLogoUpdateInputSLZ(serializers.Serializer):
    logo = serializers.CharField(help_text="用户 Logo", validators=[validate_logo])


class TenantUserExtrasUpdateInputSLZ(serializers.Serializer):
    extras = serializers.JSONField(help_text="自定义字段")

    def validate_extras(self, extras: Dict[str, Any]) -> Dict[str, Any]:
        custom_fields = TenantUserCustomField.objects.filter(
            tenant_id=self.context["tenant_id"],
            personal_center_editable=True,
        )
        return validate_user_extras(
            extras, custom_fields, self.context["data_source_id"], self.context["data_source_user_id"]
        )


class TenantUserCustomFieldOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="字段 ID")
    name = serializers.CharField(help_text="英文标识")
    display_name = serializers.CharField(help_text="展示用名称")
    data_type = serializers.CharField(help_text="字段类型")
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


class TenantUserPasswordResetInputSLZ(serializers.Serializer):
    old_password = serializers.CharField(required=True, max_length=254)
    new_password = serializers.CharField(required=True, max_length=254)

    def validate_new_password(self, new_password: str) -> str:
        validate_password(
            new_password,
            self.context["current_password"],
            self.context["data_source_user_id"],
            self.context["plugin_config"],
        )

        return new_password

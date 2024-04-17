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
from typing import Any, Dict, List

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.models import TenantUserCustomField
from bkuser.biz.validators import (
    validate_data_source_user_username,
    validate_logo,
    validate_user_extras,
    validate_user_new_password,
)
from bkuser.common.validators import validate_phone_with_country_code

logger = logging.getLogger(__name__)


class UserSearchInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名", required=False, allow_blank=True)


class DataSourceSearchDepartmentsOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="部门ID")
    name = serializers.CharField(help_text="部门名称")


class UserSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户ID")
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="姓名")
    phone = serializers.CharField(help_text="手机号")
    email = serializers.CharField(help_text="邮箱")
    departments = serializers.SerializerMethodField(help_text="用户部门")
    extras = serializers.JSONField(help_text="自定义字段")

    @swagger_serializer_method(serializer_or_field=DataSourceSearchDepartmentsOutputSLZ(many=True))
    def get_departments(self, obj: DataSourceUser):
        departments = self.context["user_dept_infos_map"].get(obj.id) or []
        return DataSourceSearchDepartmentsOutputSLZ(departments, many=True).data


class UserCreateInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名", validators=[validate_data_source_user_username])
    full_name = serializers.CharField(help_text="姓名")
    email = serializers.EmailField(help_text="邮箱")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )
    phone = serializers.CharField(help_text="手机号")
    logo = serializers.CharField(
        help_text="用户 Logo",
        required=False,
        default=settings.DEFAULT_DATA_SOURCE_USER_LOGO,
        validators=[validate_logo],
    )
    extras = serializers.JSONField(help_text="自定义字段", default=dict)

    department_ids = serializers.ListField(help_text="部门ID列表", child=serializers.IntegerField(), default=[])
    leader_ids = serializers.ListField(help_text="上级ID列表", child=serializers.IntegerField(), default=[])

    def validate(self, attrs):
        try:
            validate_phone_with_country_code(phone=attrs["phone"], country_code=attrs["phone_country_code"])
        except ValueError as e:
            raise ValidationError(str(e))

        return attrs

    def validate_department_ids(self, department_ids):
        diff_department_ids = set(department_ids) - set(
            DataSourceDepartment.objects.filter(
                id__in=department_ids, data_source_id=self.context["data_source_id"]
            ).values_list("id", flat=True)
        )
        if diff_department_ids:
            raise ValidationError(_("传递了错误的部门信息: {}").format(diff_department_ids))
        return department_ids

    def validate_leader_ids(self, leader_ids):
        diff_leader_ids = set(leader_ids) - set(
            DataSourceUser.objects.filter(
                id__in=leader_ids,
                data_source_id=self.context["data_source_id"],
            ).values_list("id", flat=True)
        )
        if diff_leader_ids:
            raise ValidationError(_("传递了错误的上级信息: {}").format(diff_leader_ids))
        return leader_ids

    def validate_extras(self, extras: Dict[str, Any]) -> Dict[str, Any]:
        custom_fields = TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"])
        return validate_user_extras(extras, custom_fields, self.context["data_source_id"])


class LeaderSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False)


class LeaderSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="上级ID")
    username = serializers.CharField(help_text="上级名称")


class DepartmentSearchInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="部门名称", required=False, allow_blank=True)


class DepartmentSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="部门ID")
    name = serializers.CharField(help_text="部门名称")


class UserDepartmentOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门ID")
    name = serializers.CharField(help_text="部门名称")


class UserLeaderOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="上级ID")
    username = serializers.CharField(help_text="上级用户名")


class UserRetrieveOutputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="姓名")
    email = serializers.CharField(help_text="邮箱")
    phone_country_code = serializers.CharField(help_text="手机区号")
    phone = serializers.CharField(help_text="手机号")
    logo = serializers.SerializerMethodField(help_text="用户Logo")
    extras = serializers.JSONField(help_text="自定义字段")

    departments = serializers.SerializerMethodField(help_text="部门信息")
    leaders = serializers.SerializerMethodField(help_text="上级信息")

    def get_logo(self, obj: DataSourceUser) -> str:
        return obj.logo or settings.DEFAULT_DATA_SOURCE_USER_LOGO

    @swagger_serializer_method(serializer_or_field=UserDepartmentOutputSLZ(many=True))
    def get_departments(self, obj: DataSourceUser) -> List[Dict]:
        relations = DataSourceDepartmentUserRelation.objects.filter(user_id=obj.id).select_related("department")
        departments = [{"id": rel.department_id, "name": rel.department.name} for rel in relations]
        return UserDepartmentOutputSLZ(departments, many=True).data

    @swagger_serializer_method(serializer_or_field=UserLeaderOutputSLZ(many=True))
    def get_leaders(self, obj: DataSourceUser) -> List[Dict]:
        relations = DataSourceUserLeaderRelation.objects.filter(user_id=obj.id).select_related("leader")
        leaders = [{"id": rel.leader_id, "username": rel.leader.username} for rel in relations]
        return UserLeaderOutputSLZ(leaders, many=True).data


class UserUpdateInputSLZ(serializers.Serializer):
    full_name = serializers.CharField(help_text="姓名")
    email = serializers.CharField(help_text="邮箱")
    phone_country_code = serializers.CharField(help_text="手机国际区号")
    phone = serializers.CharField(help_text="手机号")
    logo = serializers.CharField(
        help_text="用户 Logo",
        allow_blank=True,
        required=False,
        default=settings.DEFAULT_DATA_SOURCE_USER_LOGO,
        validators=[validate_logo],
    )
    extras = serializers.JSONField(help_text="自定义字段")

    department_ids = serializers.ListField(help_text="部门 ID 列表", child=serializers.IntegerField())
    leader_ids = serializers.ListField(help_text="上级 ID 列表", child=serializers.IntegerField())

    def validate(self, data):
        try:
            validate_phone_with_country_code(phone=data["phone"], country_code=data["phone_country_code"])
        except ValueError as e:
            raise ValidationError(str(e))

        return data

    def validate_department_ids(self, department_ids):
        diff_department_ids = set(department_ids) - set(
            DataSourceDepartment.objects.filter(
                id__in=department_ids, data_source_id=self.context["data_source_id"]
            ).values_list("id", flat=True)
        )
        if diff_department_ids:
            raise ValidationError(_("传递了错误的部门信息: {}").format(diff_department_ids))
        return department_ids

    def validate_leader_ids(self, leader_ids):
        diff_leader_ids = set(leader_ids) - set(
            DataSourceUser.objects.filter(
                id__in=leader_ids, data_source_id=self.context["data_source_id"]
            ).values_list("id", flat=True)
        )
        if diff_leader_ids:
            raise ValidationError(_("传递了错误的上级信息: {}").format(diff_leader_ids))

        if self.context["data_source_user_id"] in leader_ids:
            raise ValidationError(_("上级不可传递自身"))

        return leader_ids

    def validate_extras(self, extras: Dict[str, Any]) -> Dict[str, Any]:
        custom_fields = TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"])
        return validate_user_extras(
            extras, custom_fields, self.context["data_source_id"], self.context["data_source_user_id"]
        )


class DataSourceUserPasswordResetInputSLZ(serializers.Serializer):
    password = serializers.CharField(help_text="数据源用户重置的新密码")

    def validate_password(self, password: str) -> str:
        return validate_user_new_password(
            password=password,
            data_source_user_id=self.context["data_source_user_id"],
            plugin_config=self.context["plugin_config"],
        )


class DataSourceUserOrganizationPathOutputSLZ(serializers.Serializer):
    organization_paths = serializers.ListField(help_text="数据源用户所属部门路径列表", child=serializers.CharField())

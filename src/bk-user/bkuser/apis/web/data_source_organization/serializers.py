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
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserDeprecatedPasswordRecord,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantUserCustomField
from bkuser.biz.validators import validate_data_source_user_username, validate_logo
from bkuser.common.hashers import check_password
from bkuser.common.passwd import PasswordValidator
from bkuser.common.validators import validate_phone_with_country_code

logger = logging.getLogger(__name__)


def _validate_type_and_convert_field_data(field: TenantUserCustomField, value: Any) -> Any:  # noqa: C901
    """对自定义字段的值进行类型检查 & 做必要的类型转换"""
    if value is None:
        # 必填性在后续进行检查，这里直接跳过即可
        return value

    opt_ids = [opt["id"] for opt in field.options]

    # 数字类型，转换成整型不丢精度就转，不行就浮点数
    if field.data_type == UserFieldDataType.NUMBER:
        try:
            value = float(value)  # type: ignore
            value = int(value) if int(value) == value else value  # type: ignore
        except ValueError:
            raise ValidationError(_("字段 {} 的值 {} 不是合法数字").format(field.display_name, value))

        return value

    # 枚举类型，值（id）必须是字符串，且是可选项中的一个
    if field.data_type == UserFieldDataType.ENUM:
        if value not in opt_ids:
            raise ValidationError(_("字段 {} 的值 {} 不是可选项之一").format(field.display_name, value))

        return value

    # 多选枚举类型，值必须是字符串列表，且是可选项的子集
    if field.data_type == UserFieldDataType.MULTI_ENUM:
        if not (value and isinstance(value, list)):
            raise ValidationError(_("多选枚举类型自定义字段值必须是非空列表"))

        if set(value) - set(opt_ids):
            raise ValidationError(_("字段 {} 的值 {} 不是可选项的子集").format(field.display_name, value))

        if len(value) != len(set(value)):
            raise ValidationError(_("字段 {} 的值 {} 中存在重复值").format(field.display_name, value))

        return value

    # 字符串类型，不需要做转换
    if field.data_type == UserFieldDataType.STRING:
        if not isinstance(value, str):
            raise ValidationError(_("字段 {} 的值 {} 不是字符串类型").format(field.display_name, value))

        return value

    raise ValidationError(_("字段类型 {} 不被支持").format(field.data_type))


def _validate_unique_and_required(
    field: TenantUserCustomField, data_source_id: int, data_source_user_id: int | None, value: Any
) -> Any:
    """对自定义字段的值进行唯一性检查 & 必填性检查"""
    if field.required and value in ["", None]:
        raise ValidationError(_("字段 {} 必须填值").format(field.display_name))

    if field.unique:
        # 唯一性检查，由于添加 / 修改用户一般不会有并发操作，因此这里没有对并发的情况进行预防
        queryset = DataSourceUser.objects.filter(data_source_id=data_source_id, **{f"extras__{field.name}": value})
        if data_source_user_id:
            queryset = queryset.exclude(id=data_source_user_id)

        if queryset.exists():
            raise ValidationError(_("字段 {} 的值 {} 不满足唯一性要求").format(field.display_name, value))

    return value


def validate_user_extras(
    extras: Dict[str, Any],
    custom_fields: QuerySet[TenantUserCustomField],
    data_source_id: int,
    data_source_user_id: int | None = None,
) -> Dict[str, Any]:
    """校验 extras 中的键，值是否合法"""
    if not custom_fields.exists() and extras:
        raise ValidationError(_("当前租户未设置租户用户自定义字段"))

    if set(extras.keys()) != {field.name for field in custom_fields}:
        # Q：这里为什么不抛出具体的错误字段信息
        # A：这个校验是用于序列化器的，在前端逻辑正确的情况下，不会触发该异常，因此不暴露过多的错误信息
        raise ValidationError(_("提供的自定义字段数据与租户自定义字段不匹配"))

    for field in custom_fields:
        value = _validate_type_and_convert_field_data(field, extras[field.name])
        value = _validate_unique_and_required(field, data_source_id, data_source_user_id, value)
        extras[field.name] = value

    return extras


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
        # 新密码不可与当前正在使用的密码相同
        if check_password(password, self.context["current_password"]):
            raise ValidationError(_("新密码不可与当前密码相同"))

        # 密码规则校验
        plugin_config = self.context["plugin_config"]
        ret = PasswordValidator(plugin_config.password_rule.to_rule()).validate(password)
        if not ret.ok:
            raise ValidationError(_("密码不符合规则：{}").format(ret.exception_message))

        reseved_cnt = plugin_config.password_initial.reserved_previous_password_count
        # 当历史密码保留数量小于等于 1 时，只需要检查不与当前密码相同即可
        if reseved_cnt <= 1:
            return password

        used_passwords = (
            DataSourceUserDeprecatedPasswordRecord.objects.filter(
                user_id=self.context["data_source_user_id"],
            )
            .order_by("-created_at")[: reseved_cnt - 1]
            .values_list("password", flat=True)
        )

        for used_pwd in used_passwords:
            if check_password(password, used_pwd):
                raise ValidationError(_("新密码不能与近 {} 次使用的密码相同".format(reseved_cnt)))

        return password


class DataSourceUserOrganizationPathOutputSLZ(serializers.Serializer):
    organization_paths = serializers.ListField(help_text="数据源用户所属部门路径列表", child=serializers.CharField())

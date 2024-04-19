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

from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceUser
from bkuser.apps.tenant.constants import TenantUserStatus
from bkuser.apps.tenant.models import TenantDepartment, TenantUser, TenantUserCustomField
from bkuser.biz.validators import validate_data_source_user_username, validate_logo, validate_user_extras
from bkuser.common.validators import validate_phone_with_country_code


class DataSourceUserListInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", min_length=2, max_length=64, required=False)


class DataSourceUserListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="数据源用户 ID")
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="用户姓名")


class TenantUserSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", min_length=2, max_length=64)


class TenantUserSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    status = serializers.ChoiceField(help_text="用户状态", choices=TenantUserStatus.get_choices())
    tenant_id = serializers.CharField(help_text="用户来源租户 ID", source="data_source.owner_tenant_id")
    tenant_name = serializers.SerializerMethodField(help_text="用户来源租户名称")
    organization_paths = serializers.SerializerMethodField(help_text="组织路径")

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_tenant_name(self, obj: TenantUser) -> str:
        return self.context["tenant_name_map"][obj.data_source.owner_tenant_id]

    @swagger_serializer_method(serializer_or_field=serializers.ListSerializer(child=serializers.CharField()))
    def get_organization_paths(self, obj: TenantUser) -> List[str]:
        return self.context["org_path_map"].get(obj.id, [])


class TenantUserListInputSLZ(serializers.Serializer):
    recursive = serializers.BooleanField(help_text="包含子部门的人员", default=False)
    department_id = serializers.IntegerField(help_text="部门 ID（为 0 表示不指定部门）", default=0)
    keyword = serializers.CharField(help_text="搜索关键字", min_length=2, max_length=64, required=False)

    def validate_department_id(self, department_id: int) -> int:
        if (
            department_id
            and not TenantDepartment.objects.filter(tenant_id=self.context["tenant_id"], id=department_id).exists()
        ):
            raise ValidationError("部门不存在")

        return department_id


class TenantUserListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    status = serializers.ChoiceField(help_text="用户状态", choices=TenantUserStatus.get_choices())
    email = serializers.CharField(help_text="用户邮箱", source="data_source_user.email")
    phone = serializers.CharField(help_text="用户手机号", source="data_source_user.phone")
    departments = serializers.SerializerMethodField(help_text="用户所属部门")

    def get_departments(self, obj: TenantUser) -> List[str]:
        return self.context["tenant_user_depts_map"].get(obj.id, [])


def _validate_duplicate_data_source_username(
    data_source_id: str, username: str, data_source_user_id: int | None = None
) -> str:
    """校验数据源用户名是否重复"""
    queryset = DataSourceUser.objects.filter(data_source_id=data_source_id, username=username)
    # 过滤掉自身
    if data_source_user_id:
        queryset = queryset.exclude(id=data_source_user_id)

    if queryset.exists():
        raise ValidationError(_("用户名 {} 已存在").format(username))

    return username


class TenantUserCreateInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名", validators=[validate_data_source_user_username])
    full_name = serializers.CharField(help_text="姓名")
    email = serializers.EmailField(help_text="邮箱", required=False, default="", allow_blank=True)
    phone = serializers.CharField(help_text="手机号", required=False, default="", allow_blank=True)
    phone_country_code = serializers.CharField(
        help_text="手机国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE, allow_blank=True
    )
    logo = serializers.CharField(
        help_text="用户 Logo",
        required=False,
        default=settings.DEFAULT_DATA_SOURCE_USER_LOGO,
        validators=[validate_logo],
    )
    extras = serializers.JSONField(help_text="自定义字段", default=dict)

    # Q：这里为什么用的数据源部门/用户 ID 而不是租户部门/用户 ID
    # A：实际 DB 存储关联表是数据源部门/用户的 ID，如果 options api & 参数都是数据源部门/用户的 ID
    #   那么就不需要提供出去 & 接收参数后都要转换一遍（数据源 -> 租户 & 租户 -> 数据源）能省点事 :D
    department_ids = serializers.ListField(
        help_text="数据源部门 ID 列表", child=serializers.IntegerField(), default=list
    )
    leader_ids = serializers.ListField(help_text="数据源上级 ID 列表", child=serializers.IntegerField(), default=list)

    def validate_username(self, username: str) -> str:
        return _validate_duplicate_data_source_username(self.context["data_source_id"], username)

    def validate_department_ids(self, department_ids):
        invalid_department_ids = set(department_ids) - set(
            DataSourceDepartment.objects.filter(
                id__in=department_ids, data_source_id=self.context["data_source_id"]
            ).values_list("id", flat=True)
        )
        if invalid_department_ids:
            raise ValidationError(_("指定的部门 {} 不存在").format(invalid_department_ids))

        return department_ids

    def validate_leader_ids(self, leader_ids):
        invalid_leader_ids = set(leader_ids) - set(
            DataSourceUser.objects.filter(
                id__in=leader_ids, data_source_id=self.context["data_source_id"]
            ).values_list("id", flat=True)
        )
        if invalid_leader_ids:
            raise ValidationError(_("指定的直属上级 {} 不存在").format(invalid_leader_ids))

        return leader_ids

    def validate_extras(self, extras: Dict[str, Any]) -> Dict[str, Any]:
        custom_fields = TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"])
        return validate_user_extras(extras, custom_fields, self.context["data_source_id"])

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 如果提供了手机号，则校验手机号是否合法
        if attrs["phone"]:
            try:
                validate_phone_with_country_code(phone=attrs["phone"], country_code=attrs["phone_country_code"])
            except ValueError as e:
                raise ValidationError(str(e))

        return attrs


class TenantUserCreateOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")


class TenantUserOrganizationPathOutputSLZ(serializers.Serializer):
    organization_paths = serializers.ListField(help_text="数据源用户所属部门路径列表", child=serializers.CharField())

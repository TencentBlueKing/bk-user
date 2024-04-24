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
import collections
from typing import Any, Dict, List

import phonenumbers
from django.conf import settings
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantDepartment, TenantUser, TenantUserCustomField, UserBuiltinField
from bkuser.biz.validators import validate_data_source_user_username, validate_user_extras
from bkuser.common.serializers import StringArrayField
from bkuser.common.validators import validate_phone_with_country_code


class TenantUserInfoSLZ(serializers.Serializer):
    """批量创建时校验用户信息用，该模式邮箱，手机号等均为必填字段"""

    username = serializers.CharField(help_text="用户名", validators=[validate_data_source_user_username])
    full_name = serializers.CharField(help_text="姓名")
    email = serializers.EmailField(help_text="邮箱")
    phone = serializers.CharField(help_text="手机号")
    phone_country_code = serializers.CharField(help_text="手机国际区号")
    extras = serializers.JSONField(help_text="自定义字段")

    def validate_extras(self, extras: Dict[str, Any]) -> Dict[str, Any]:
        return validate_user_extras(extras, self.context["custom_fields"], self.context["data_source_id"])

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 校验手机号是否合法
        try:
            validate_phone_with_country_code(phone=attrs["phone"], country_code=attrs["phone_country_code"])
        except ValueError as e:
            raise ValidationError(str(e))

        return attrs


class TenantUserBatchCreateInputSLZ(serializers.Serializer):
    user_infos = serializers.ListField(
        help_text="用户信息列表",
        child=serializers.CharField(help_text="用户信息（纯字符串，以空格分隔）"),
        min_length=1,
        max_length=settings.ORGANIZATION_BATCH_OPERATION_API_LIMIT,
    )
    department_id = serializers.IntegerField(help_text="目标租户部门 ID")

    def validate_user_infos(self, raw_user_infos: List[str]) -> List[Dict[str, Any]]:
        builtin_fields = UserBuiltinField.objects.all()
        custom_fields = TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"])

        user_infos = self._parse_user_infos(raw_user_infos, builtin_fields, custom_fields)
        self._validate_user_infos(user_infos, custom_fields)
        return user_infos

    def _parse_user_infos(
        self,
        raw_user_infos: List[str],
        builtin_fields: QuerySet[UserBuiltinField],
        custom_fields: QuerySet[TenantUserCustomField],
    ) -> List[Dict[str, Any]]:
        # 默认的内置字段，虽然邮箱 & 手机在 DB 中不是必填，但是在快速录入场景中要求必填，
        # 手机国际区号与手机号合并，不需要单独提供，租户用户自定义字段则只需要选择必填的
        required_field_names = [f.name for f in builtin_fields if f.name != "phone_country_code"] + [
            f.name for f in custom_fields if f.required
        ]

        field_count = len(required_field_names)
        user_infos: List[Dict[str, Any]] = []
        for idx, raw_info in enumerate(raw_user_infos, start=1):
            # 注：raw_info 格式是以空格为分隔符的用户信息字符串
            # 形式如：tiga 迪迦 tiga@otm.com +8613612356789 male shenzhen running,swimming
            # 字段对应：username full_name email phone gender region sport_hobbies
            data: List[str] = [s for s in raw_info.split(" ") if s]
            if len(data) != field_count:
                raise ValidationError(
                    _(
                        "第 {} 行，用户信息格式不正确，预期 {} 个字段，实际 {} 个字段",
                    ).format(idx, field_count, len(data))
                )

            # 按字段顺序映射（业务逻辑会确保数据顺序一致）
            props = dict(zip(required_field_names, data, strict=True))
            # 手机号 + 国际区号单独解析
            phone_numbers = props["phone"]
            props["phone_country_code"] = settings.DEFAULT_PHONE_COUNTRY_CODE
            if phone_numbers.startswith("+"):
                ret = phonenumbers.parse(phone_numbers)
                props["phone"], props["phone_country_code"] = str(ret.national_number), str(ret.country_code)

            user_infos.append(
                {
                    "username": props["username"],
                    "full_name": props["full_name"],
                    "email": props["email"],
                    "phone": props["phone"],
                    "phone_country_code": props["phone_country_code"],
                    "extras": self._build_user_extras(props, custom_fields),
                }
            )

        return user_infos

    def _build_user_extras(
        self, props: Dict[str, str], custom_fields: QuerySet[TenantUserCustomField]
    ) -> Dict[str, Any]:
        """构建用户自定义字段"""
        username = props["username"]
        extras = {}
        for f in custom_fields:
            opt_ids = [opt["id"] for opt in f.options]
            value = props.get(f.name, f.default)

            # 数字类型，转换成整型不丢精度就转，不行就浮点数
            if f.data_type == UserFieldDataType.NUMBER:
                try:
                    value = float(value)  # type: ignore
                    value = int(value) if int(value) == value else value  # type: ignore
                except ValueError:
                    raise ValidationError(
                        _(
                            "用户名：{} 自定义字段 {} 值 {} 不能转换为数字",
                        ).format(username, f.name, value)
                    )

            # 枚举类型，值（id）必须是字符串，且是可选项中的一个
            elif f.data_type == UserFieldDataType.ENUM:
                if value not in opt_ids:
                    raise ValidationError(
                        _("用户名：{} 自定义字段 {} 值 {} 不在可选项 {} 中").format(username, f.name, value, opt_ids)
                    )
            # 多选枚举类型，值必须是字符串列表，且是可选项的子集
            elif f.data_type == UserFieldDataType.MULTI_ENUM:
                # 快速录入的数据中的的多选枚举，都是通过 "," 分隔的字符串表示列表
                # 但是，默认值 default 可能是 list 类型，因此这里还是需要做类型判断的
                if isinstance(value, str):
                    value = [v.strip() for v in value.split(",") if v.strip()]  # type: ignore

                if set(value) - set(opt_ids):
                    raise ValidationError(
                        _("用户名：{} 自定义字段 {} 值 {} 不在可选项 {} 中").format(username, f.name, value, opt_ids)
                    )
            # 必填字段检查仅适用于字符串类型字段，因为数字类型即使是 0 也不能判断是空，枚举类型都有值检查
            elif f.data_type == UserFieldDataType.STRING and f.required and not value:
                raise ValidationError(f"username: {username}, field {f.name} is required")

            extras[f.name] = value

        return extras

    def _validate_user_infos(
        self, user_infos: List[Dict[str, Any]], custom_fields: QuerySet[TenantUserCustomField]
    ) -> None:
        """校验用户信息列表中数据是否合法"""
        usernames = [u["username"] for u in user_infos]
        # 检查新增的数据是否有用户名重复的
        counter = collections.Counter(usernames)
        if duplicate_usernames := [u for u, cnt in counter.items() if cnt > 1]:
            raise ValidationError(_("用户名 {} 重复").format(", ".join(duplicate_usernames)))

        if exists_users := DataSourceUser.objects.filter(
            username__in=usernames, data_source_id=self.context["data_source_id"]
        ):
            raise ValidationError(_("用户名 {} 已存在").format(", ".join(u.username for u in exists_users)))

        # 单独字段校验走序列化器，无需获取 validated_data
        TenantUserInfoSLZ(
            data=user_infos,
            context={
                "tenant_id": self.context["tenant_id"],
                "data_source_id": self.context["data_source_id"],
                "custom_fields": custom_fields,
            },
            many=True,
        ).is_valid(raise_exception=True)


def _validate_tenant_user_ids(user_ids: List[str], tenant_id: str) -> None:
    """校验租户用户 ID 列表中数据是否合法"""
    exists_tenant_users = TenantUser.objects.filter(id__in=user_ids, tenant_id=tenant_id)
    if invalid_user_ids := set(user_ids) - set(exists_tenant_users.values_list("id", flat=True)):
        raise ValidationError(_("用户 ID {} 在当前租户中不存在").format(", ".join(invalid_user_ids)))

    if len({u.data_source_id for u in exists_tenant_users}) != 1:
        raise ValidationError(_("待批量操作的用户应属于同一数据源").format(", ".join(user_ids)))

    data_source = exists_tenant_users.first().data_source
    if not (data_source.is_local and data_source.is_real_type):
        raise ValidationError(_("仅能批量操作本地数据源用户"))


def _validate_tenant_department_ids(department_ids: List[int], tenant_id: str) -> None:
    """校验租户部门 ID 列表中数据是否合法"""
    exists_tenant_depts = TenantDepartment.objects.filter(id__in=department_ids, tenant_id=tenant_id)
    if invalid_dept_ids := set(department_ids) - set(exists_tenant_depts.values_list("id", flat=True)):
        raise ValidationError(_("部门 ID {} 在当前租户中不存在").format(invalid_dept_ids))

    if len({u.data_source_id for u in exists_tenant_depts}) != 1:
        raise ValidationError(_("选中的部门应属于同一数据源").format(department_ids))

    data_source = exists_tenant_depts.first().data_source
    if not (data_source.is_local and data_source.is_real_type):
        raise ValidationError(_("仅能选择本地数据源部门"))


class TenantUserBatchCopyInputSLZ(serializers.Serializer):
    user_ids = serializers.ListField(
        help_text="用户 ID 列表",
        child=serializers.CharField(help_text="租户用户 ID"),
        min_length=1,
        max_length=settings.ORGANIZATION_BATCH_OPERATION_API_LIMIT,
    )
    department_ids = serializers.ListField(
        help_text="目标部门 ID 列表",
        child=serializers.IntegerField(help_text="目标部门 ID"),
        min_length=1,
        max_length=10,
    )

    def validate_user_ids(self, user_ids: List[str]) -> List[str]:
        _validate_tenant_user_ids(user_ids, self.context["tenant_id"])
        return user_ids

    def validate_department_ids(self, department_ids: List[int]) -> List[int]:
        _validate_tenant_department_ids(department_ids, self.context["tenant_id"])
        return department_ids


class TenantUserBatchMoveInputSLZ(TenantUserBatchCopyInputSLZ):
    ...


class TenantUserBatchDeleteInputSLZ(serializers.Serializer):
    user_ids = StringArrayField(
        help_text="用户 ID 列表",
        min_items=1,
        max_items=settings.ORGANIZATION_BATCH_OPERATION_API_LIMIT,
    )

    def validate_user_ids(self, user_ids: List[str]) -> List[str]:
        _validate_tenant_user_ids(user_ids, self.context["tenant_id"])
        return user_ids

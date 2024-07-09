# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.models import (
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.constants import TIME_ZONE_CHOICES, TenantUserStatus, UserFieldDataType
from bkuser.apps.tenant.models import (
    CollaborationStrategy,
    TenantDepartment,
    TenantUser,
    TenantUserCustomField,
    UserBuiltinField,
)
from bkuser.biz.validators import (
    validate_data_source_user_username,
    validate_logo,
    validate_user_extras,
    validate_user_new_password,
)
from bkuser.common.constants import BkLanguageEnum
from bkuser.common.serializers import StringArrayField
from bkuser.common.validators import validate_phone_with_country_code


class OptionalTenantUserListInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", min_length=1, max_length=64, required=False)
    excluded_user_id = serializers.CharField(help_text="排除的租户用户 ID（Leader 不能是自己）", required=False)


class OptionalTenantUserListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户 ID")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")


class TenantUserSearchInputSLZ(serializers.Serializer):
    tenant_id = serializers.CharField(help_text="租户 ID", required=False)
    keyword = serializers.CharField(help_text="搜索关键字", min_length=1, max_length=64, required=False)


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
            raise ValidationError(_("部门不存在"))

        return department_id


class TenantUserListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    status = serializers.ChoiceField(help_text="用户状态", choices=TenantUserStatus.get_choices())
    email = serializers.CharField(help_text="用户邮箱", source="data_source_user.email")
    phone = serializers.CharField(help_text="用户手机号", source="data_source_user.phone")
    phone_country_code = serializers.CharField(help_text="手机国际区号", source="data_source_user.phone_country_code")
    departments = serializers.SerializerMethodField(help_text="用户所属部门")

    @swagger_serializer_method(serializer_or_field=serializers.ListSerializer(child=serializers.CharField()))
    def get_departments(self, obj: TenantUser) -> List[str]:
        return self.context["tenant_user_depts_map"].get(obj.id, [])


def _validate_duplicate_data_source_username(
    data_source_id: str, username: str, excluded_data_source_user_id: int | None = None
) -> str:
    """校验数据源用户名是否重复"""
    queryset = DataSourceUser.objects.filter(data_source_id=data_source_id, username=username)
    # 过滤掉自身
    if excluded_data_source_user_id:
        queryset = queryset.exclude(id=excluded_data_source_user_id)

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
        allow_blank=True,
        default=settings.DEFAULT_DATA_SOURCE_USER_LOGO,
        validators=[validate_logo],
    )
    extras = serializers.JSONField(help_text="自定义字段", default=dict)

    department_ids = serializers.ListField(
        help_text="租户部门 ID 列表",
        child=serializers.IntegerField(),
        default=list,
    )
    leader_ids = serializers.ListField(
        help_text="租户上级 ID 列表",
        child=serializers.CharField(),
        default=list,
    )

    def validate_username(self, username: str) -> str:
        return _validate_duplicate_data_source_username(self.context["data_source_id"], username)

    def validate_department_ids(self, department_ids: List[int]) -> List[int]:
        invalid_department_ids = set(department_ids) - set(
            TenantDepartment.objects.filter(
                id__in=department_ids, data_source_id=self.context["data_source_id"]
            ).values_list("id", flat=True)
        )
        if invalid_department_ids:
            raise ValidationError(_("指定的部门 {} 不存在").format(invalid_department_ids))

        return department_ids

    def validate_leader_ids(self, leader_ids: List[str]) -> List[str]:
        invalid_leader_ids = set(leader_ids) - set(
            TenantUser.objects.filter(
                id__in=leader_ids,
                data_source_id=self.context["data_source_id"],
            ).values_list("id", flat=True)
        )
        if invalid_leader_ids:
            raise ValidationError(_("指定的直属上级 {} 不存在").format(",".join(invalid_leader_ids)))

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


class TenantUserDepartmentSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户部门 ID")
    name = serializers.CharField(help_text="租户部门名称", source="data_source_department.name")

    class Meta:
        ref_name = "organization.TenantUserDepartmentSLZ"


class TenantUserLeaderSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户用户 ID")
    username = serializers.CharField(help_text="租户用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="租户用户名称", source="data_source_user.full_name")

    class Meta:
        ref_name = "organization.TenantUserLeaderSLZ"


class TenantUserRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    status = serializers.ChoiceField(help_text="用户状态", choices=TenantUserStatus.get_choices())
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="姓名", source="data_source_user.full_name")
    email = serializers.CharField(help_text="邮箱", source="data_source_user.email")
    phone = serializers.CharField(help_text="手机号", source="data_source_user.phone")
    phone_country_code = serializers.CharField(help_text="手机国际区号", source="data_source_user.phone_country_code")
    account_expired_at = serializers.DateTimeField(help_text="账号过期时间")
    extras = serializers.SerializerMethodField(help_text="自定义字段")
    logo = serializers.SerializerMethodField(help_text="用户 Logo")
    language = serializers.ChoiceField(help_text="语言", choices=BkLanguageEnum.get_choices())
    time_zone = serializers.ChoiceField(help_text="时区", choices=TIME_ZONE_CHOICES)

    departments = serializers.SerializerMethodField(help_text="租户部门 ID & 名称列表")
    leaders = serializers.SerializerMethodField(help_text="上级（租户用户）ID & 名称列表")

    class Meta:
        ref_name = "organization.TenantUserRetrieveOutputSLZ"

    @swagger_serializer_method(serializer_or_field=serializers.JSONField)
    def get_extras(self, obj: TenantUser) -> Dict[str, Any]:
        # 租户用户租户 与 数据源所属租户 一致，说明不是协同产生，直接给 extras 即可
        if obj.tenant_id == obj.data_source.owner_tenant_id:
            return obj.data_source_user.extras

        # 对于协同过来的用户，自定义字段需要做次映射
        strategy = CollaborationStrategy.objects.get(
            source_tenant_id=obj.data_source.owner_tenant_id, target_tenant_id=obj.tenant_id
        )
        # TODO (su) 如果后续支持表达式，则不能直接取 Dict 做映射
        field_mapping = {mp["source_field"]: mp["target_field"] for mp in strategy.target_config["field_mapping"]}
        # 协同的字段映射不是全量的，可能源租户提供 5 个自定义字段，目标租户只配了 3 个，需要过滤掉多余的
        return {field_mapping[k]: v for k, v in obj.data_source_user.extras.items() if k in field_mapping}

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_logo(self, obj: TenantUser) -> str:
        return obj.data_source_user.logo or settings.DEFAULT_DATA_SOURCE_USER_LOGO

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


class TenantUserUpdateInputSLZ(TenantUserCreateInputSLZ):
    def validate_username(self, username: str) -> str:
        return _validate_duplicate_data_source_username(
            self.context["data_source_id"], username, self.context["data_source_user_id"]
        )

    def validate_extras(self, extras: Dict[str, Any]) -> Dict[str, Any]:
        custom_fields = TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"])

        extras = validate_user_extras(
            extras, custom_fields, self.context["data_source_id"], self.context["data_source_user_id"]
        )
        # 更新模式下，一些自定义字段是不允许修改的（前端也需要禁用）
        # 这里的处理策略是：在通过校验之后，用 DB 中的数据进行替换
        exists_extras = DataSourceUser.objects.get(id=self.context["data_source_user_id"]).extras
        for f in custom_fields.filter(manager_editable=False):
            if f.name in exists_extras:
                extras[f.name] = exists_extras[f.name]

        return extras

    def validate_leader_ids(self, leader_ids: List[str]) -> List[str]:
        if self.context["tenant_user_id"] in leader_ids:
            raise ValidationError(_("不能设置自己为自己的直接上级"))

        return super().validate_leader_ids(leader_ids)


class TenantUserPasswordRuleRetrieveOutputSLZ(serializers.Serializer):
    # --- 长度限制类 ---
    min_length = serializers.IntegerField(help_text="密码最小长度")
    max_length = serializers.IntegerField(help_text="密码最大长度")
    # --- 字符限制类 ---
    contain_lowercase = serializers.BooleanField(help_text="必须包含小写字母")
    contain_uppercase = serializers.BooleanField(help_text="必须包含大写字母")
    contain_digit = serializers.BooleanField(help_text="必须包含数字")
    contain_punctuation = serializers.BooleanField(help_text="必须包含特殊字符（标点符号）")
    # --- 连续性限制类 ---
    not_continuous_count = serializers.IntegerField(help_text="密码不允许连续 N 位出现")
    not_keyboard_order = serializers.BooleanField(help_text="不允许键盘序")
    not_continuous_letter = serializers.BooleanField(help_text="不允许连续字母序")
    not_continuous_digit = serializers.BooleanField(help_text="不允许连续数字序")
    not_repeated_symbol = serializers.BooleanField(help_text="重复字母，数字，特殊字符")
    # --- 规则提示 ---
    rule_tips = serializers.ListField(help_text="用户密码规则提示", child=serializers.CharField(), source="tips")


class TenantUserPasswordResetInputSLZ(serializers.Serializer):
    password = serializers.CharField(help_text="用户重置的新密码")

    def validate_password(self, password: str) -> str:
        return validate_user_new_password(
            password=password,
            data_source_user_id=self.context["data_source_user_id"],
            plugin_config=self.context["plugin_config"],
        )


class TenantUserOrganizationPathOutputSLZ(serializers.Serializer):
    organization_paths = serializers.ListField(help_text="数据源用户所属部门路径列表", child=serializers.CharField())


class TenantUserStatusUpdateOutputSLZ(serializers.Serializer):
    status = serializers.ChoiceField(help_text="用户状态", choices=TenantUserStatus.get_choices())


class TenantUserInfoSLZ(serializers.Serializer):
    """批量创建时校验用户信息用，该模式邮箱，手机号等均为必填字段"""

    username = serializers.CharField(help_text="用户名", validators=[validate_data_source_user_username])
    full_name = serializers.CharField(help_text="姓名")
    email = serializers.EmailField(help_text="邮箱")
    phone = serializers.CharField(help_text="手机号")
    phone_country_code = serializers.CharField(help_text="手机国际区号")
    extras = serializers.JSONField(help_text="自定义字段")

    class Meta:
        ref_name = "organization.TenantUserInfoSLZ"

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
        child=serializers.CharField(help_text="用户信息（纯字符串，以空格分隔）", allow_blank=True),
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
            # 跳过空白行
            if not raw_info.strip():
                continue

            # 注：raw_info 格式是以英文逗号 (,) 为分隔符的用户信息字符串，多选枚举以 / 拼接
            # 字段：username full_name email phone gender region hobbies
            # 示例：kafka, 卡芙卡, kafka@starrail.com, +8613612345678, female, StarCoreHunter, hunting/burning
            data: List[str] = [s.strip() for s in raw_info.split(",") if s.strip()]
            if len(data) != field_count:
                raise ValidationError(
                    _(
                        "第 {} 行，用户信息格式不正确，预期 {} 个字段，实际 {} 个字段",
                    ).format(idx, field_count, len(data))
                )

            # 按字段顺序映射（业务逻辑会确保数据顺序一致）
            props = dict(zip(required_field_names, data))
            # 手机号 + 国际区号单独解析
            phone_numbers = props["phone"]
            props["phone_country_code"] = settings.DEFAULT_PHONE_COUNTRY_CODE
            if phone_numbers.startswith("+"):
                try:
                    ret = phonenumbers.parse(phone_numbers)
                except phonenumbers.NumberParseException:
                    raise ValidationError(_("第 {} 行，手机号 {} 格式不正确").format(idx, phone_numbers))

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
                # 快速录入的数据中的的多选枚举，都是通过 "/" 分隔的字符串表示列表
                # 但是默认值 default 可能是 list 类型，因此这里还是需要做类型判断的
                if isinstance(value, str):
                    value = [v.strip() for v in value.split("/") if v.strip()]  # type: ignore

                if set(value) - set(opt_ids):
                    raise ValidationError(
                        _("用户名：{} 自定义字段 {} 值 {} 不在可选项 {} 中").format(username, f.name, value, opt_ids)
                    )

            extras[f.name] = value

        return extras

    def _validate_user_infos(
        self, user_infos: List[Dict[str, Any]], custom_fields: QuerySet[TenantUserCustomField]
    ) -> None:
        """校验用户信息列表中数据是否合法"""
        usernames = [u["username"].lower() for u in user_infos]
        # 检查新增的数据是否有用户名重复的，需要忽略大小写，因为 DB 中是忽略的
        counter = collections.Counter(usernames)
        if duplicate_usernames := [u for u, cnt in counter.items() if cnt > 1]:
            raise ValidationError(_("用户名 {} 重复").format(", ".join(duplicate_usernames)))

        if exists_usernames := DataSourceUser.objects.filter(
            username__in=usernames, data_source_id=self.context["data_source_id"]
        ).values_list("username", flat=True):
            raise ValidationError(_("用户名 {} 已存在").format(", ".join(exists_usernames)))

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


class TenantUserBatchCreatePreviewInputSLZ(TenantUserBatchCreateInputSLZ):
    ...


class TenantUserBatchCreatePreviewOutputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="姓名")
    email = serializers.EmailField(help_text="邮箱")
    phone = serializers.CharField(help_text="手机号")
    phone_country_code = serializers.CharField(help_text="手机国际区号")
    extras = serializers.JSONField(help_text="自定义字段")


class TenantUserBatchDeleteInputSLZ(serializers.Serializer):
    user_ids = StringArrayField(
        help_text="用户 ID 列表", min_items=1, max_items=settings.ORGANIZATION_BATCH_OPERATION_API_LIMIT
    )

    def validate_user_ids(self, user_ids: List[str]) -> List[str]:
        exists_tenant_users = TenantUser.objects.filter(
            id__in=user_ids, tenant_id=self.context["tenant_id"], data_source_id=self.context["data_source_id"]
        )
        if invalid_user_ids := set(user_ids) - set(exists_tenant_users.values_list("id", flat=True)):
            raise ValidationError(_("用户 ID {} 在当前租户中不存在").format(", ".join(invalid_user_ids)))

        return user_ids

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

import logging
import operator
from collections import defaultdict
from functools import reduce
from typing import Dict, List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel
from rest_framework.exceptions import ValidationError

from bkuser.apps.tenant.constants import (
    DISPLAY_NAME_EXPRESSION_EXTRA_FIELD_CONFIGS,
    DISPLAY_NAME_EXPRESSION_FIELD_PATTERN,
    DisplayNameExpressionExtraFieldEnum,
)
from bkuser.apps.tenant.data_models import DisplayNameExpressionExtraField
from bkuser.apps.tenant.models import (
    CollaborationStrategy,
    TenantUser,
    TenantUserCustomField,
    TenantUserDisplayNameExpressionConfig,
    UserBuiltinField,
)

logger = logging.getLogger(__name__)


class TenantUserPhoneInfo(BaseModel):
    is_inherited_phone: bool
    custom_phone: Optional[str] = ""
    custom_phone_country_code: Optional[str] = settings.DEFAULT_PHONE_COUNTRY_CODE


class TenantUserEmailInfo(BaseModel):
    is_inherited_email: bool
    custom_email: Optional[str] = ""


class TenantUserHandler:
    @staticmethod
    def update_tenant_user_phone(tenant_user: TenantUser, phone_info: TenantUserPhoneInfo):
        tenant_user.is_inherited_phone = phone_info.is_inherited_phone
        if not phone_info.is_inherited_phone:
            tenant_user.custom_phone = phone_info.custom_phone
            tenant_user.custom_phone_country_code = phone_info.custom_phone_country_code
        tenant_user.save()

    @staticmethod
    def update_tenant_user_email(tenant_user: TenantUser, email_info: TenantUserEmailInfo):
        tenant_user.is_inherited_email = email_info.is_inherited_email
        if not email_info.is_inherited_email:
            tenant_user.custom_email = email_info.custom_email
        tenant_user.save()

    @staticmethod
    def generate_tenant_user_display_name(user: TenantUser) -> str:
        # 如果是协同租户用户，使用源租户的表达式配置
        tenant_id = (
            user.data_source.owner_tenant_id if user.data_source.owner_tenant_id != user.tenant_id else user.tenant_id
        )
        try:
            config = TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=tenant_id)
        except TenantUserDisplayNameExpressionConfig.DoesNotExist:
            logger.exception(
                "tenant [%s] display name expression config not found, please contact administrator",
                tenant_id,
            )
        return TenantUserDisplayNameExpressionConfigHandler.render_display_name(user, config)

    @staticmethod
    def batch_generate_tenant_user_display_name(users: List[TenantUser]) -> Dict[str, str]:
        if not users:
            return {}

        tenant_ids = [
            user.data_source.owner_tenant_id if user.data_source.owner_tenant_id != user.tenant_id else user.tenant_id
            for user in users
        ]
        configs = TenantUserDisplayNameExpressionConfig.objects.filter(tenant_id__in=tenant_ids)

        tenant_config_map = {config.tenant_id: config for config in configs}

        return TenantUserDisplayNameExpressionConfigHandler.batch_render_display_name(users, tenant_config_map)

    @staticmethod
    def get_tenant_user_display_name_map_by_ids(tenant_user_ids: List[str]) -> Dict[str, str]:
        """
        根据指定的租户用户 ID 列表，获取对应的展示用名称列表

        :return: {user_id: user_display_name}
        """
        # 1. 尝试从 TenantUser 表根据表达式渲染出展示用名称
        display_name_map = {
            user.id: TenantUserHandler.generate_tenant_user_display_name(user)
            for user in TenantUser.objects.select_related("data_source_user").filter(id__in=tenant_user_ids)
        }
        # 2. 针对可能出现的 TenantUser 中被删除的 user_id，尝试从 User 表获取展示用名称（登录过就有记录）
        if not_exists_user_ids := set(tenant_user_ids) - set(display_name_map.keys()):
            logger.warning(
                "tenant user ids: %s not exists in TenantUser model, try find display name in User Model",
                not_exists_user_ids,
            )
            UserModel = get_user_model()  # noqa: N806
            for user in UserModel.objects.filter(username__in=not_exists_user_ids):
                # FIXME (nan) get_property 有 N+1 的风险，需要处理
                display_name_map[user.username] = user.get_property("display_name") or user.username

        # 3. 前两种方式都失效，那就给啥 user_id 就返回啥，避免调用的地方还需要处理
        if not_exists_user_ids := set(tenant_user_ids) - set(display_name_map.keys()):
            display_name_map.update({user_id: user_id for user_id in not_exists_user_ids})

        return display_name_map


class TenantUserDisplayNameExpressionConfigHandler:
    @staticmethod
    def parse_display_name_expression(tenant_id: str, expression: str) -> dict[str, List[str]]:
        fields = DISPLAY_NAME_EXPRESSION_FIELD_PATTERN.findall(expression)

        # TODO: 后续需要过滤敏感字段，敏感字段不支持展示
        builtin_field_map = {field.name: field.unique for field in UserBuiltinField.objects.all()}
        builtin_field_names = set(builtin_field_map.keys())

        custom_field_map = {
            field.name: field.unique for field in TenantUserCustomField.objects.filter(tenant_id=tenant_id)
        }
        custom_field_names = set(custom_field_map.keys())

        extra_fields = [
            DisplayNameExpressionExtraField(**field)  # type: ignore
            for field in DISPLAY_NAME_EXPRESSION_EXTRA_FIELD_CONFIGS
        ]
        extra_field_map = {field.name: field.unique for field in extra_fields}
        extra_field_names = set(extra_field_map.keys())

        # 获取所有允许配置的字段
        all_fields = builtin_field_names | custom_field_names | extra_field_names

        invalid_fields = [f for f in fields if f not in all_fields]
        if invalid_fields:
            raise ValidationError(_("表达式中存在无效字段: {}").format(", ".join(invalid_fields)))

        # 表达式字段必须存在唯一字段
        has_unique_field = any(
            builtin_field_map.get(field, False)
            or custom_field_map.get(field, False)
            or extra_field_map.get(field, False)
            for field in fields
        )
        if not has_unique_field:
            raise ValidationError(_("表达式中必须存在唯一字段"))

        # 集合运算 & 求交集，比遍历判断更高效
        return {
            "builtin": list(set(fields) & builtin_field_names),
            "custom": list(set(fields) & custom_field_names),
            "extra": list(set(fields) & extra_field_names),
        }

    @staticmethod
    def render_display_name(user: TenantUser, config: TenantUserDisplayNameExpressionConfig) -> str:
        """渲染用户展示名"""
        fields = config.fields

        # 获取各类字段值
        builtin_values = TenantUserDisplayNameExpressionConfigHandler._get_builtin_field_values(
            user, fields["builtin"]
        )
        custom_values = TenantUserDisplayNameExpressionConfigHandler._get_custom_field_values(user, fields["custom"])
        extra_values = TenantUserDisplayNameExpressionConfigHandler._get_extra_field_values(
            [user], fields["extra"], owner_tenant_id=user.data_source.owner_tenant_id
        )

        field_value_map = {}
        field_value_map.update(builtin_values)
        field_value_map.update(custom_values)
        field_value_map.update(extra_values[user.id])

        # 使用正则表达式替换表达式中的字段为对应值
        # match 是正则表达式从表达式（expression）中匹配到的对象，group(1) 是匹配到的第一个分组，即字段名
        # 如果字段名在 field_value_map 中存在，则使用 field_value_map 中的值替换，否则使用 "-"
        return DISPLAY_NAME_EXPRESSION_FIELD_PATTERN.sub(
            lambda match: field_value_map.get(match.group(1), "-"), config.expression
        )

    @staticmethod
    def batch_render_display_name(
        users: List[TenantUser], config_map: Dict[str, TenantUserDisplayNameExpressionConfig]
    ) -> Dict[str, str]:
        """批量渲染用户展示用名称"""
        if not users:
            return {}

        user_display_name_map: Dict[str, str] = {}

        # 使用用户数据源的 owner_tenant_id 作为租户 ID 进行分组
        tenant_user_map: Dict[str, List[TenantUser]] = defaultdict(list)
        for user in users:
            tenant_user_map[user.data_source.owner_tenant_id].append(user)

        # 遍历所有组合
        for owner_tenant_id, tenant_users in tenant_user_map.items():
            config = config_map.get(owner_tenant_id)
            if not config:
                logger.error(
                    "tenant [%s] display name expression config not found, please contact administrator",
                    owner_tenant_id,
                )
                raise ValidationError(_("租户 {} 的展示名表达式配置不存在，请联系管理员").format(owner_tenant_id))

            fields = config.fields
            # 由于未来额外字段查询可能涉及到 N + 1 问题，所以需要单独处理
            extra_values = TenantUserDisplayNameExpressionConfigHandler._get_extra_field_values(
                tenant_users, fields["extra"], owner_tenant_id
            )

            for user in tenant_users:
                user_id = user.id
                field_value_map = {}

                builtin_values = TenantUserDisplayNameExpressionConfigHandler._get_builtin_field_values(
                    user, fields["builtin"]
                )
                custom_values = TenantUserDisplayNameExpressionConfigHandler._get_custom_field_values(
                    user, fields["custom"]
                )

                field_value_map.update(builtin_values)
                field_value_map.update(custom_values)
                field_value_map.update(extra_values[user_id])

                # 使用表达式模板渲染展示名
                user_display_name_map[user_id] = DISPLAY_NAME_EXPRESSION_FIELD_PATTERN.sub(
                    lambda match, field_value_map=field_value_map: field_value_map.get(match.group(1), "-"),  # type: ignore
                    config.expression,
                )

        return user_display_name_map

    @staticmethod
    def _get_builtin_field_values(user: TenantUser, builtin_fields: List[str]) -> Dict[str, str]:
        """处理内置字段"""
        # TODO: 内建字段后续可能也存在协同字段映射的情况，需要处理
        # 联系方式字段映射
        field_value_map = {}

        # 联系信息字段映射
        contact_info = {
            "email": user.email,
            "phone": user.phone_info[0],
            "phone_country_code": user.phone_info[1],
        }

        for field in builtin_fields:
            if field in contact_info:
                field_value_map[field] = contact_info[field]
            else:
                field_value_map[field] = getattr(user.data_source_user, field)
        return field_value_map

    @staticmethod
    def _get_custom_field_values(user: TenantUser, custom_fields: List[str]) -> Dict[str, str]:
        """处理自定义字段"""
        return {field: str(user.data_source_user.extras.get(field, "-")) for field in custom_fields}

    @staticmethod
    def _get_extra_field_values(
        users: List[TenantUser],
        extra_fields: List[str],
        owner_tenant_id: str,
    ) -> Dict[str, Dict[str, str]]:
        """处理额外字段，如果是协同租户用户，则从源租户的 TenantUser 表中获取对应的 ID"""
        user_field_value_map: Dict[str, Dict[str, str]] = {user.id: {} for user in users}
        for field in extra_fields:
            if field == DisplayNameExpressionExtraFieldEnum.TENANT_USER_ID:
                # 如果用户是当前租户用户，则直接使用当前租户用户 ID
                if owner_tenant_id == users[0].tenant_id:
                    for user in users:
                        user_field_value_map[user.id][field] = user.id
                else:
                    # 如果用户是协同租户用户，则从源租户的 TenantUser 中获取对应的 ID
                    # 构建数据源用户ID到当前用户ID的映射
                    data_source_user_map = {user.data_source_user_id: user.id for user in users}
                    data_source_user_ids = set(data_source_user_map.keys())

                    # 获取源租户中的用户
                    tenant_users = TenantUser.objects.filter(
                        tenant_id=owner_tenant_id, data_source_user_id__in=data_source_user_ids
                    )

                    for tenant_user in tenant_users:
                        user_id = data_source_user_map[tenant_user.data_source_user_id]
                        # {目标租户用户 ID: {额外字段名: 源租户用户 ID}}
                        user_field_value_map[user_id][field] = tenant_user.id
            else:
                # TODO: 后续加入组织字段
                continue

        return user_field_value_map

    @staticmethod
    def build_display_name_search_queries(tenant_id: str, keyword: str) -> Q:
        """根据不同字段类型构建展示名搜索查询条件"""
        config = TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=tenant_id)
        collab_configs = (
            TenantUserDisplayNameExpressionConfigHandler._get_collaboration_tenant_display_name_expression_config(
                tenant_id
            )
        )
        all_configs = [config] + list(collab_configs) if collab_configs else [config]

        queries = []
        for config in all_configs:
            fields = config.fields

            # 构建内置字段查询条件
            builtin_queries = TenantUserDisplayNameExpressionConfigHandler._build_builtin_field_queries(
                fields["builtin"], keyword
            )
            # 为什么不构建自定义字段查询条件？
            # 因为自定义字段存储在 extra 字段（JsonField）中，进行模糊搜索非常消耗资源，JSON 数据需要解析与字符串匹配

            # 构建额外字段查询条件
            extra_queries = TenantUserDisplayNameExpressionConfigHandler._build_extra_field_queries(
                fields["extra"], keyword
            )

            field_queries = reduce(operator.or_, builtin_queries + extra_queries)

            queries.append(field_queries & Q(data_source__owner_tenant_id=config.tenant_id))

        return reduce(operator.or_, queries)

    @staticmethod
    def _get_collaboration_tenant_display_name_expression_config(
        tenant_id: str,
    ) -> QuerySet[TenantUserDisplayNameExpressionConfig]:
        """获取协同租户的展示名表达式配置"""
        source_tenant_ids = CollaborationStrategy.objects.filter(target_tenant_id=tenant_id).values_list(
            "source_tenant_id", flat=True
        )
        return TenantUserDisplayNameExpressionConfig.objects.filter(tenant_id__in=source_tenant_ids)

    @staticmethod
    def _build_builtin_field_queries(builtin_fields: List[str], keyword: str) -> List[Q]:
        """构建内置字段查询条件"""
        inherit_flag_mapping = {"phone_country_code": "phone", "phone": "phone", "email": "email"}
        queries = []

        for field in builtin_fields:
            if field in inherit_flag_mapping:
                inherit_flag = f"is_inherited_{inherit_flag_mapping[field]}"
                queries.append(
                    Q(**{inherit_flag: False, f"custom_{field}__icontains": keyword})
                    | Q(**{inherit_flag: True, f"data_source_user__{field}__icontains": keyword})
                )
            else:
                queries.append(Q(**{f"data_source_user__{field}__icontains": keyword}))

        return queries

    @staticmethod
    def _build_extra_field_queries(extra_fields: List[str], keyword: str) -> List[Q]:
        """构建额外字段查询条件"""
        return [
            Q(id__icontains=keyword) if field == DisplayNameExpressionExtraFieldEnum.TENANT_USER_ID else Q()
            for field in extra_fields
        ]

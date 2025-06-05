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
from functools import reduce
from typing import Dict, List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from pydantic import BaseModel

from bkuser.apps.tenant.constants import (
    DISPLAY_NAME_EXPRESSION_FIELD_PATTERN,
)
from bkuser.apps.tenant.display_name_cache import (
    DisplayNameCacheHandler,
    DisplayNameCacheManager,
    get_display_name_config,
)
from bkuser.apps.tenant.models import (
    DataSource,
    DataSourceUser,
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


class TenantUserDisplayNameHandler:
    @staticmethod
    def generate_tenant_user_display_name(user: TenantUser) -> str:
        """生成租户用户展示名"""

        if user.data_source.owner_tenant_id == user.tenant_id:
            config = get_display_name_config(user.tenant_id)
        else:
            config = DisplayNameCacheHandler.build_default_display_name_config()

        # 首先从 Redis 缓存获取
        display_name = DisplayNameCacheManager.get_display_name(user.id, config.version)
        if not display_name:
            # 如果缓存中没有，则从数据库中获取
            display_name = TenantUserDisplayNameHandler.render_display_name(user, config)
            # 将获取到的展示名缓存到 Redis 中
            DisplayNameCacheManager.set_display_name(user.id, config.version, display_name)

        return display_name

    @staticmethod
    def batch_generate_tenant_user_display_name(users: List[TenantUser]) -> Dict[str, str]:
        """
        批量生成租户用户展示名

        注意：调用时需要提前连表查询 `data_source_user`，否则会导致 N+1 问题
        """
        if not users:
            return {}

        # 1. 从缓存中获取已有的 display_name 映射，以及需要渲染的用户列表
        display_name_map, users_need_render = DisplayNameCacheHandler.get_display_names_from_cache(users)

        # 2. 渲染没有缓存的用户的 display_name
        if users_need_render:
            rendered_display_names = TenantUserDisplayNameHandler.batch_render_display_name(users_need_render)
            display_name_map.update(rendered_display_names)

            # 3. 将新渲染的结果缓存至 Redis 中
            DisplayNameCacheHandler.set_rendered_display_names_cache(users_need_render, rendered_display_names)

        return display_name_map

    @staticmethod
    def get_tenant_user_display_name_map_by_ids(tenant_user_ids: List[str]) -> Dict[str, str]:
        """
        根据指定的租户用户 ID 列表，获取对应的展示用名称列表

        :return: {user_id: user_display_name}
        """
        # 1. 尝试从 TenantUser 表根据表达式渲染出展示用名称（使用批量处理）
        users = TenantUser.objects.select_related("data_source_user").filter(id__in=tenant_user_ids)
        display_name_map = TenantUserDisplayNameHandler.batch_generate_tenant_user_display_name(users)

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

    @staticmethod
    def parse_display_name_expression(tenant_id: str, expression: str) -> Dict[str, List[str]]:
        """解析展示名表达式，返回格式为 {builtin: [内置字段列表], custom: [自定义字段列表], extra: [额外字段列表]}"""
        fields = DISPLAY_NAME_EXPRESSION_FIELD_PATTERN.findall(expression)

        # TODO: 后续需要过滤敏感字段，敏感字段不支持展示
        builtin_field_names = {field.name for field in UserBuiltinField.objects.all()}

        custom_field_names = {field.name for field in TenantUserCustomField.objects.filter(tenant_id=tenant_id)}

        # TODO: 后续支持 extra 字段
        # 集合运算 & 求交集，比遍历判断更高效
        return {
            "builtin": list(set(fields) & builtin_field_names),
            "custom": list(set(fields) & custom_field_names),
            "extra": [],
        }

    @staticmethod
    def render_display_name(user: TenantUser, config: TenantUserDisplayNameExpressionConfig) -> str:
        """渲染用户展示名"""

        # 获取各类字段值
        builtin_values = TenantUserDisplayNameHandler._get_builtin_field_values(user, config.builtin_fields)
        custom_values = TenantUserDisplayNameHandler._get_custom_field_values(user, config.custom_fields)

        field_value_map = {}
        field_value_map.update(builtin_values)
        field_value_map.update(custom_values)

        # 使用正则表达式替换表达式中的字段为对应值
        # match 是正则表达式从表达式（expression）中匹配到的对象，group(1) 是匹配到的第一个分组，即字段名
        # 如果字段名在 field_value_map 中存在，则使用 field_value_map 中的值替换，否则使用 "-"
        return DISPLAY_NAME_EXPRESSION_FIELD_PATTERN.sub(
            lambda match: field_value_map.get(match.group(1), "-"), config.expression
        )

    @staticmethod
    def batch_render_display_name(
        users: List[TenantUser],
    ) -> Dict[str, str]:
        """批量渲染用户展示用名称"""
        if not users:
            return {}

        user_display_name_map: Dict[str, str] = {}

        # 为了避免 n + 1 问题，需要提前获取所有用户数据源所属租户的信息
        data_source_ids = {user.data_source_id for user in users}
        data_source_tenant_map = dict(
            DataSource.objects.filter(id__in=data_source_ids).values_list("id", "owner_tenant_id")
        )

        # 遍历所有用户
        for user in users:
            field_value_map = {}
            owner_tenant_id = data_source_tenant_map[user.data_source_id]
            # 如果为本租户，则使用本租户的 display_name 表达式配置
            if owner_tenant_id == user.tenant_id:
                config = get_display_name_config(user.tenant_id)
            # 如果为协同租户，则使用默认的 display_name 表达式配置
            else:
                config = DisplayNameCacheHandler.build_default_display_name_config()

            builtin_values = TenantUserDisplayNameHandler._get_builtin_field_values(user, config.builtin_fields)
            custom_values = TenantUserDisplayNameHandler._get_custom_field_values(user, config.custom_fields)

            field_value_map.update(builtin_values)
            field_value_map.update(custom_values)

            # 使用表达式模板渲染展示名
            user_display_name_map[user.id] = DISPLAY_NAME_EXPRESSION_FIELD_PATTERN.sub(
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
    def build_display_name_search_queries(tenant_id: str, keyword: str) -> Q:
        """根据不同字段类型构建展示名搜索查询条件"""
        config = get_display_name_config(tenant_id)

        # 构建内置字段查询条件
        builtin_queries = TenantUserDisplayNameHandler._build_builtin_field_queries(config.builtin_fields, keyword)
        # 为什么不构建自定义字段查询条件？
        # 因为自定义字段存储在 extra 字段（JsonField）中，进行模糊搜索非常消耗资源，JSON 数据需要解析与字符串匹配

        if not builtin_queries:
            return Q()

        field_queries = reduce(operator.or_, builtin_queries)
        return field_queries & Q(data_source__owner_tenant_id=tenant_id)

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
    def build_default_preview_tenant_user(tenant_id: str) -> TenantUser:
        return TenantUser(
            id="517hMkqnSBqF9Mv9",
            data_source=DataSource(owner_tenant_id=tenant_id),
            tenant_id=tenant_id,
            data_source_user=DataSourceUser(
                username="zhangsan",
                full_name="张三",
                phone="13512345671",
                phone_country_code="86",
                email="zhangsan@m.com",
            ),
        )

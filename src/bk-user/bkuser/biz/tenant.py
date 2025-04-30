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

from bkuser.apps.tenant.constants import DISPLAY_NAME_EXPRESSION_FIELD_PATTERN
from bkuser.apps.tenant.models import TenantUser, TenantUserDisplayNameExpressionConfig

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
        config = TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=user.tenant_id)
        return TenantUserHandler.render_display_name(user, config)

    @staticmethod
    def render_display_name(user: TenantUser, config: TenantUserDisplayNameExpressionConfig) -> str:
        """渲染用户展示名"""
        tenant_user_contact_info = {
            "email": user.email,
            "phone": user.phone_info[0],
            "phone_country_code": user.phone_info[1],
        }

        field_value_map = {}
        # 处理内置字段
        for field in config.builtin_fields:
            if field in tenant_user_contact_info:
                field_value_map[field] = tenant_user_contact_info[field]
            # TODO：后续加入对用户组织的支持
            else:
                field_value_map[field] = getattr(user.data_source_user, field)

        # 处理自定义字段，需要将值转换为字符串，否则无法执行正则表达式替换操作
        field_value_map.update(
            {field: str(user.data_source_user.extras.get(field, "-")) for field in config.custom_fields}
        )

        # 使用正则表达式 sub 替换方法，将表达式中的字段替换为 field_value_map 对应的值
        return DISPLAY_NAME_EXPRESSION_FIELD_PATTERN.sub(
            lambda match: field_value_map.get(match.group(1), "-"), config.expression
        )

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

    @staticmethod
    def build_search_query(tenant_id: str, keyword: str) -> Q:
        config = TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=tenant_id)

        inherit_flag_mapping = {"phone_country_code": "phone", "phone": "phone", "email": "email"}

        def _covert_contact_field_to_query(field: str) -> Q:
            # 由于租户用户的电子邮箱与手机号、手机国际区号分为用户自定义与继承自数据源两种情况，故需要分别考虑查询条件
            inherit_flag = f"is_inherited_{inherit_flag_mapping[field]}"
            return Q(
                Q(**{inherit_flag: False, f"custom_{field}__icontains": keyword})
                | Q(**{inherit_flag: True, f"data_source_user__{field}__icontains": keyword})
            )

        # 处理内置字段
        builtin_queries = [
            _covert_contact_field_to_query(field)
            if field in inherit_flag_mapping
            else Q(**{f"data_source_user__{field}__icontains": keyword})
            for field in config.builtin_fields
        ]

        # 处理自定义字段
        custom_queries = [
            Q(**{f"data_source_user__extras__{field}__icontains": keyword}) for field in config.custom_fields
        ]

        return reduce(operator.or_, builtin_queries + custom_queries)

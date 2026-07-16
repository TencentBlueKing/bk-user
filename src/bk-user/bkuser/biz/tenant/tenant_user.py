# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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

from typing import Dict, List, Optional

from django.conf import settings
from pydantic import BaseModel

from bkuser.apps.data_source.cache import DataSourceCache
from bkuser.apps.tenant.models import TenantUser
from bkuser.common.language import get_language_codes


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
    def get_login_name(tenant_user: TenantUser) -> str:
        """
        获取租户用户的登录名

        对于协同过来的用户（即数据源所属租户 != 当前租户），加上来源租户 ID 作为后缀
        """
        owner_tenant_id = DataSourceCache.get_owner_tenant_id(tenant_user.data_source_id)
        if tenant_user.tenant_id != owner_tenant_id:
            return f"{tenant_user.data_source_user.username}@{owner_tenant_id}"
        return tenant_user.data_source_user.username

    @staticmethod
    def batch_get_login_name(tenant_users: List[TenantUser]) -> Dict[str, str]:
        """
        批量获取租户用户的登录名

        对于协同过来的用户（即数据源所属租户 != 当前租户），加上来源租户 ID 作为后缀

        Note: 调用方需确保 tenant_users 已通过 select_related("data_source_user") 预加载关联对象，
        否则可能导致 N+1 查询问题
        """
        return {user.id: TenantUserHandler.get_login_name(user) for user in tenant_users}

    @staticmethod
    def update_tenant_user_language(tenant_user: TenantUser, language: str) -> None:
        if language not in get_language_codes():
            return
        tenant_user.language = language
        tenant_user.save(update_fields=["language", "updated_at"])

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
import secrets
import string
from hashlib import md5
from typing import Dict

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from bkuser import settings
from bkuser.apis.web.password.constants import TokenRelatedObjType
from bkuser.apps.tenant.models import TenantUser
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum
from bkuser.plugins.constants import DataSourcePluginEnum


class GenerateTokenTooFrequently(Exception):
    """生成令牌过于频繁"""


class UserResetPasswordTokenManager:
    """用户重置密码 Token 管理器"""

    lock_timeout = 60

    def __init__(self):
        self.cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.RESET_PASSWORD_TOKEN)

    def gen_token(self, tenant_user: TenantUser, related_obj_type: TokenRelatedObjType) -> str:
        """生成 token"""
        info = {"type": related_obj_type.value, "tenant_id": tenant_user.tenant_id}
        if related_obj_type == TokenRelatedObjType.TENANT_USER:
            info["tenant_user_id"] = tenant_user.id
        elif related_obj_type == TokenRelatedObjType.EMAIL:
            info["email"] = tenant_user.email
        elif related_obj_type == TokenRelatedObjType.PHONE:
            info["phone"], info["phone_country_code"] = tenant_user.phone_info

        # 生成 token 有频率限制，不能短时间内频繁生成
        lock_key = self._gen_lock_key_by_info(info)
        if self.cache.get(lock_key):
            raise GenerateTokenTooFrequently(_("生成令牌过于频繁"))

        self.cache.set(lock_key, True, timeout=self.lock_timeout)

        token = self._gen_token()
        self.cache.set(self._gen_cache_key_by_token(token), info, timeout=settings.RESET_PASSWORD_TOKEN_VALID_TIME)
        return token

    def disable_token(self, token: str) -> None:
        """禁用 token"""
        cache_key = self._gen_cache_key_by_token(token)
        self.cache.delete(cache_key)

    def list_users_by_token(self, token: str) -> QuerySet[TenantUser]:
        """根据 token 获取用户信息，返回可修改密码的用户列表"""
        cache_key = self._gen_cache_key_by_token(token)
        info = self.cache.get(cache_key, None)
        if not info:
            return TenantUser.objects.none()

        if info["type"] == TokenRelatedObjType.EMAIL:
            tenant_users = TenantUser.objects.filter_by_email(info["tenant_id"], info["email"])
        elif info["type"] == TokenRelatedObjType.PHONE:
            tenant_users = TenantUser.objects.filter_by_phone(
                info["tenant_id"], info["phone"], info["phone_country_code"]
            )
        elif info["type"] == TokenRelatedObjType.TENANT_USER:
            tenant_users = TenantUser.objects.filter(tenant_id=info["tenant_id"], id=info["tenant_user_id"])
        else:
            return TenantUser.objects.none()

        # FIXME (su) 补充 status 过滤
        # 只有本地数据源用户关联的租户用户才可以修改密码
        return tenant_users.filter(data_source_user__data_source__plugin_id=DataSourcePluginEnum.LOCAL)

    def _gen_token(self) -> str:
        """生成重置密码用 Token，字符集：数字，大小写字母"""
        charset = string.ascii_letters + string.digits
        return "".join(secrets.choice(charset) for _ in range(settings.RESET_PASSWORD_TOKEN_LENGTH))

    def _gen_cache_key_by_token(self, token: str) -> str:
        """
        压缩 token，避免 cache_key 过长

        md5 -> 32, sha1 -> 40, sha256 -> 64
        """
        return md5(token.encode("utf-8")).hexdigest()

    def _gen_lock_key_by_info(self, info: Dict[str, str]) -> str:
        """根据 token 对应信息提供锁，避免短时间重复分配 token"""
        return ":".join(str(val) for val in info.values())

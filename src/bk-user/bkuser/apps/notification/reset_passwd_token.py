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
import json
import secrets
import string
from datetime import timedelta
from hashlib import md5

from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bkuser.apps.notification.constants import TokenRelatedObjType
from bkuser.apps.notification.exceptions import ExceedSendResetPasswordTokenLimit
from bkuser.apps.notification.tasks import send_reset_passwd_url_to_user
from bkuser.apps.tenant.models import TenantUser
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum
from bkuser.plugins.constants import DataSourcePluginEnum


class UserResetPasswordTokenManager:
    """用户重置密码 Token 管理器"""

    def __init__(self):
        self.cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.RESET_PASSWORD_TOKEN)

    def gen_token(self, tenant_user: TenantUser, related_obj_type: TokenRelatedObjType):
        info = {"type": related_obj_type.value, "tenant_id": tenant_user.tenant_id}
        if related_obj_type == TokenRelatedObjType.TENANT_USER:
            info["tenant_user_id"] = tenant_user.id
        elif related_obj_type == TokenRelatedObjType.EMAIL:
            info["email"] = tenant_user.email
        elif related_obj_type == TokenRelatedObjType.PHONE:
            info["phone"], info["phone_country_code"] = tenant_user.phone_info

        token = self._gen_token()
        self.cache.set(
            self._gen_cache_key_by_token(token),
            json.dumps(info),
            timeout=settings.RESET_PASSWORD_TOKEN_VALID_TIME,
        )
        return token

    def list_user_by_token(self, token: str) -> QuerySet[TenantUser]:
        """根据 token 获取用户信息，返回可修改密码的用户列表"""
        cache_val = self.cache.get(self._gen_cache_key_by_token(token), None)
        if not cache_val:
            return TenantUser.objects.none()

        info = json.loads(cache_val)
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

    def send(self, tenant_user: TenantUser):
        """发送重置密码链接到用户邮箱"""
        if not self._can_send(tenant_user):
            raise ExceedSendResetPasswordTokenLimit(_("超过发送次数限制"))

        token = self.gen_token(tenant_user, TokenRelatedObjType.EMAIL)
        send_reset_passwd_url_to_user.delay(tenant_user.id, token)

    def _can_send(self, tenant_user: TenantUser) -> bool:
        """检查当前验证码发送次数"""
        send_cnt_cache_key = f"{tenant_user.email}:send_cnt"
        send_cnt = self.cache.get(send_cnt_cache_key, 0)
        if send_cnt >= settings.RESET_PASSWORD_TOKEN_MAX_SEND_PER_DAY:
            return False

        # 今天结束后过期
        midnight = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        expire_seconds = (midnight - timezone.now()).total_seconds()
        self.cache.set(send_cnt_cache_key, send_cnt + 1, timeout=expire_seconds)
        return True

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

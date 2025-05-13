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

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from bkuser.apps.notification.constants import NotificationMethod, NotificationScene
from bkuser.apps.notification.notifier import TenantUserNotifier
from bkuser.apps.tenant.models import TenantUser
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum
from bkuser.common.verification_code import VerificationCodeScene
from bkuser.utils.time import calc_remaining_seconds_today


class ExceedSendRateLimit(Exception):
    """超过发送次数限制"""


class PhoneVerificationCodeSender:
    """发送用户手机验证码（含次数检查）"""

    def __init__(self, scene: VerificationCodeScene):
        self.cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.VERIFICATION_CODE)
        self.scene = scene

    def send(self, tenant_user: TenantUser, code: str):
        """发送验证码到用户手机"""
        if not self._can_send(tenant_user):
            raise ExceedSendRateLimit(_("今日发送验证码次数超过上限"))

        # 若是更新手机号场景，则使用自定义手机号与国际区号
        # Q：为什么使用自定义手机号与国际区号？
        # A：因为用户更新手机号（国际区号）的场景需要向新手机号发送验证码
        # 而用户更改的新手机号（国际区号）此时存于用户对象的自定义手机号（国际区号）属性
        if self.scene == VerificationCodeScene.UPDATE_PHONE:
            phone = tenant_user.custom_phone
            phone_country_code = tenant_user.custom_phone_country_code
        else:
            phone, phone_country_code = tenant_user.phone_info

        contact_info = {
            "phone_info": {
                "phone": phone,
                "phone_country_code": phone_country_code,
            }
        }

        TenantUserNotifier(
            NotificationScene.SEND_VERIFICATION_CODE,
            method=NotificationMethod.SMS,
        ).send(tenant_user, contact_info, verification_code=code)  # type: ignore

    def _can_send(self, tenant_user: TenantUser) -> bool:
        phone, phone_country_code = tenant_user.phone_info
        send_cnt_cache_key = f"{self.scene.value}:{phone_country_code}:{phone}:send_cnt"

        send_cnt = self.cache.get(send_cnt_cache_key, 0)

        if send_cnt >= settings.VERIFICATION_CODE_MAX_SEND_PER_DAY:
            return False

        self.cache.set(send_cnt_cache_key, send_cnt + 1, timeout=calc_remaining_seconds_today())
        return True


class EmailVerificationCodeSender:
    """发送用户邮箱验证码（含次数检查）"""

    def __init__(self, scene: VerificationCodeScene):
        self.cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.VERIFICATION_CODE)
        self.scene = scene

    def send(self, tenant_user: TenantUser, code: str):
        """发送验证码到用户邮箱"""
        if not self._can_send(tenant_user):
            raise ExceedSendRateLimit(_("今日发送验证码次数超过上限"))

        # 若是更新邮箱场景，则使用自定义邮箱
        # Q：为什么使用自定义邮箱？
        # A：因为用户更新邮箱的场景需要向新邮箱号发送验证码
        # 而用户更改的新邮箱号此时存于用户对象的自定义邮箱属性
        email = tenant_user.custom_email if self.scene == VerificationCodeScene.UPDATE_EMAIL else tenant_user.email

        TenantUserNotifier(
            NotificationScene.SEND_VERIFICATION_CODE,
            method=NotificationMethod.EMAIL,
        ).send(tenant_user, contact_info={"email": email}, verification_code=code)

    def _can_send(self, tenant_user: TenantUser) -> bool:
        email = tenant_user.email
        send_cnt_cache_key = f"{self.scene.value}:{email}:send_cnt"

        send_cnt = self.cache.get(send_cnt_cache_key, 0)
        if send_cnt >= settings.VERIFICATION_CODE_MAX_SEND_PER_DAY:
            return False

        self.cache.set(send_cnt_cache_key, send_cnt + 1, timeout=calc_remaining_seconds_today())
        return True


class EmailResetPasswdTokenSender:
    """发送用户邮箱重置密码链接"""

    def __init__(self):
        self.cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.RESET_PASSWORD_TOKEN)

    def send(self, tenant_user: TenantUser, token: str):
        """发送重置密码链接到用户邮箱"""
        if not self._can_send(tenant_user):
            raise ExceedSendRateLimit(_("超过发送次数限制"))

        TenantUserNotifier(
            NotificationScene.RESET_PASSWORD,
            data_source_id=tenant_user.data_source_user.data_source_id,
        ).send(tenant_user, contact_info={"email": tenant_user.email}, token=token)

    def _can_send(self, tenant_user: TenantUser) -> bool:
        send_cnt_cache_key = f"{tenant_user.email}:send_cnt"

        send_cnt = self.cache.get(send_cnt_cache_key, 0)
        if send_cnt >= settings.RESET_PASSWORD_TOKEN_MAX_SEND_PER_DAY:
            return False

        self.cache.set(send_cnt_cache_key, send_cnt + 1, timeout=calc_remaining_seconds_today())
        return True

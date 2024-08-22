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

        TenantUserNotifier(
            NotificationScene.SEND_VERIFICATION_CODE,
            method=NotificationMethod.SMS,
        ).send(tenant_user, verification_code=code)

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

        TenantUserNotifier(
            NotificationScene.SEND_VERIFICATION_CODE,
            method=NotificationMethod.EMAIL,
        ).send(tenant_user, verification_code=code)

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
        ).send(tenant_user, token=token)

    def _can_send(self, tenant_user: TenantUser) -> bool:
        send_cnt_cache_key = f"{tenant_user.email}:send_cnt"

        send_cnt = self.cache.get(send_cnt_cache_key, 0)
        if send_cnt >= settings.RESET_PASSWORD_TOKEN_MAX_SEND_PER_DAY:
            return False

        self.cache.set(send_cnt_cache_key, send_cnt + 1, timeout=calc_remaining_seconds_today())
        return True

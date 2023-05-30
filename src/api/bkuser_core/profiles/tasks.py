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
import datetime
import logging
import time
import urllib.parse

from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from django.utils.timezone import now

from .constants import TypeOfExpiration
from .notifier import (
    ExpirationNotifier,
    get_config_from_all_local_categories,
    get_notice_config_for_expiration,
    get_profiles_for_account_expiration,
    get_profiles_for_password_expiration,
)
from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.celery import app
from bkuser_core.common.notifier import send_mail
from bkuser_core.profiles import exceptions
from bkuser_core.profiles.constants import PASSWD_RESET_VIA_SAAS_EMAIL_TMPL, ProfileStatus
from bkuser_core.profiles.models import ExpirationNoticeRecord, Profile
from bkuser_core.profiles.utils import make_passwd_reset_url_by_token
from bkuser_core.user_settings.exceptions import SettingHasBeenDisabledError
from bkuser_core.user_settings.loader import ConfigProvider

logger = logging.getLogger(__name__)


@app.task
def send_password_by_email(profile_id: int, raw_password: str = None, init: bool = True, token: str = None):
    """发送密码到邮箱，支持初始化 & 重置"""
    logger.info(
        "--------- going to send password of Profile(%s) via email ----------",
        profile_id,
    )
    try:
        profile = Profile.objects.get(id=profile_id)
    except Exception:
        logger.exception("get profile<id=%s> failed during send mail", profile_id)
        raise

    if not profile.email:
        logger.exception("profiles<username=%s> has no valid email", profile.username)
        raise exceptions.ProfileEmailEmpty

    config_loader = ConfigProvider(profile.category_id)

    if init:
        email_config = config_loader["init_mail_config"]
        url = settings.LOGIN_REDIRECT_TO
        message = email_config["content"].format(username=profile.username, password=raw_password, url=url)
    else:
        # 从平台重置密码
        if token:
            email_config = config_loader["reset_mail_config"]
            message = email_config["content"].format(
                url=make_passwd_reset_url_by_token(token),
                reset_url=urllib.parse.urljoin(settings.SAAS_URL, "reset_password"),
            )
        # 在用户管理里管理操作重置密码
        else:
            email_config = config_loader["reset_mail_config"]
            message = PASSWD_RESET_VIA_SAAS_EMAIL_TMPL.format(username=profile.username)

    send_mail(
        sender=email_config["sender"],
        receivers=[profile.email],
        message=message,
        title=email_config["title"],
    )


@periodic_task(run_every=crontab(minute="0", hour="2"))
def notice_for_account_expiration():
    """
    用户账号过期通知
    #TODO:存在大数量级用户的情况下，当天的任务可能无法当天执行完毕，新一天的任务又同步开启，这里考虑做优化
    """
    expiring_profile_list, expired_profile_list = get_profiles_for_account_expiration()
    category_config_map = get_config_from_all_local_categories()

    logger.info(
        "--------- going to notice expiring_profiles count:(%s) for account expiration ----------",
        len(expiring_profile_list),
    )
    for profile in expiring_profile_list:
        notice_config = get_notice_config_for_expiration(
            expiration_type=TypeOfExpiration.ACCOUNT_EXPIRATION.value,
            profile=profile,
            config_loader=category_config_map[profile["category_id"]],
        )
        if not notice_config:
            continue

        ExpirationNotifier().handler(notice_config)
        time.sleep(settings.NOTICE_INTERVAL_SECONDS)

    logger.info(
        "--------- going to notice expired_profiles count:(%s) for account expiration ----------",
        len(expired_profile_list),
    )
    for profile in expired_profile_list:
        notice_config = get_notice_config_for_expiration(
            expiration_type=TypeOfExpiration.ACCOUNT_EXPIRATION.value,
            profile=profile,
            config_loader=category_config_map[profile["category_id"]],
        )
        if not notice_config:
            continue

        notice_record = ExpirationNoticeRecord.objects.filter(
            type=TypeOfExpiration.ACCOUNT_EXPIRATION.value, profile_id=profile["id"]
        ).first()
        if not notice_record:
            ExpirationNotifier().handler(notice_config)
            ExpirationNoticeRecord.objects.create(
                type=TypeOfExpiration.ACCOUNT_EXPIRATION.value,
                notice_date=datetime.date.today(),
                profile_id=profile["id"],
            )
            time.sleep(settings.NOTICE_INTERVAL_SECONDS)
            continue

        # 上一次过期通知的时间距离现在超过一个月则进行通知
        if notice_record.notice_date < datetime.date.today() - datetime.timedelta(days=30):
            ExpirationNotifier().handler(notice_config)
            notice_record.notice_date = datetime.date.today()
            notice_record.save()
            time.sleep(settings.NOTICE_INTERVAL_SECONDS)


@periodic_task(run_every=crontab(minute="0", hour="3"))
def notice_for_password_expiration():
    """
    用户密码过期通知
    """
    expiring_profile_list, expired_profile_list = get_profiles_for_password_expiration()
    category_config_map = get_config_from_all_local_categories()

    logger.info(
        "--------- going to notice expiring_profiles count:(%s) for password expiration ----------",
        len(expiring_profile_list),
    )
    for profile in expiring_profile_list:
        notice_config = get_notice_config_for_expiration(
            expiration_type=TypeOfExpiration.PASSWORD_EXPIRATION.value,
            profile=profile,
            config_loader=category_config_map[profile["category_id"]],
        )
        if not notice_config:
            continue

        ExpirationNotifier().handler(notice_config)
        time.sleep(settings.NOTICE_INTERVAL_SECONDS)

    logger.info(
        "--------- going to notice expired_profiles count:(%s) for password expiration ----------",
        len(expired_profile_list),
    )
    for profile in expired_profile_list:
        notice_config = get_notice_config_for_expiration(
            expiration_type=TypeOfExpiration.PASSWORD_EXPIRATION.value,
            profile=profile,
            config_loader=category_config_map[profile["category_id"]],
        )
        if not notice_config:
            continue

        notice_record = ExpirationNoticeRecord.objects.filter(
            type=TypeOfExpiration.PASSWORD_EXPIRATION.value, profile_id=profile["id"]
        ).first()
        if not notice_record:
            ExpirationNotifier().handler(notice_config)
            ExpirationNoticeRecord.objects.create(
                type=TypeOfExpiration.PASSWORD_EXPIRATION.value,
                notice_date=datetime.date.today(),
                profile_id=profile["id"],
            )
            time.sleep(settings.NOTICE_INTERVAL_SECONDS)
            continue

        if notice_record.notice_date < datetime.date.today() - datetime.timedelta(days=30):
            ExpirationNotifier().handler(notice_config)
            notice_record.notice_date = datetime.date.today()
            notice_record.save()
            time.sleep(settings.NOTICE_INTERVAL_SECONDS)


@periodic_task(run_every=crontab(minute="0", hour="4"))  # pylint: disable=function-name-too-long
def change_profile_status_for_account_expiration():
    """
    对账号过期的用户进行状态变更
    """
    category_ids = ProfileCategory.objects.filter(type=CategoryType.LOCAL.value).values_list("id")
    expired_profiles = Profile.objects.filter(
        category_id__in=category_ids,
        account_expiration_date__lt=datetime.date.today(),
        # Note: "禁用"状态比"已过期"状态优先级高，所以这里只会处理正常状态的时候过期场景
        # TODO: DISABLED/DELETED/LOCKED 这些非正常状态，需要在转为正常状态的时先判断是否过期，如果过期则调整为已过期状态
        #  现阶段非正常态变更为正常态时，暂时不处理，只通过该周期任务延期一天处理（PS: 现在状态变更位置过于离散，待实现统一方法对状态变更后的计算下个状态后考虑）
        status__in=[ProfileStatus.NORMAL.value, ProfileStatus.DISABLED.value],
    )
    expired_profiles.update(status=ProfileStatus.EXPIRED.value)


@periodic_task(run_every=crontab(minute="0", hour="5"))  # pylint: disable=function-name-too-long
def change_profile_status_for_account_locking():
    """
    对长时间未登录的用户进行状态冻结
    """
    category_ids = ProfileCategory.objects.filter(type=CategoryType.LOCAL.value).values_list("id", flat=True)
    frozen_profile_ids = []
    # 获取用户目录设置
    for category_id in category_ids:
        config_loader = ConfigProvider(category_id=category_id)
        try:
            enable_auto_freeze = config_loader.get("enable_auto_freeze")
            logger.info("category<%s> enable_auto_freeze = %s", category_id, enable_auto_freeze)
            if not enable_auto_freeze:
                continue
        except SettingHasBeenDisabledError:
            logger.info("category<%s> has disabled enable_auto_freeze", category_id)
            continue

        try:
            freeze_after_days = config_loader.get("freeze_after_days")
            if int(freeze_after_days) <= 0:
                logger.error("account_expired_to_locked: freeze_after_days should be more than 0")
                continue
        except SettingHasBeenDisabledError:
            logger.info("category<%s> has disabled freeze_after_days", category_id)
            continue

        profiles = Profile.objects.filter(
            category_id=category_id,
            status=ProfileStatus.NORMAL.value,
        )

        for profile in profiles:
            # 最后登录时间
            # 当用户从未登录过
            if not profile.last_login_time:
                # 场景考虑：该用户被管理员关注
                profile_last_operate_time = profile.update_time
            else:
                # 登录过，长久未登录，但是被管理员关注
                profile_last_operate_time = max(profile.last_login_time, profile.update_time)
            # 被冻结用户集合添加
            if profile_last_operate_time + datetime.timedelta(days=int(freeze_after_days)) < now():
                frozen_profile_ids.append(profile.id)
    # 批量冻结
    if frozen_profile_ids:
        Profile.objects.filter(id__in=frozen_profile_ids).update(status=ProfileStatus.LOCKED.value)

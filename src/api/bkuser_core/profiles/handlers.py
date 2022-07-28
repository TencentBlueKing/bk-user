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
import logging
from typing import TYPE_CHECKING

from django.dispatch import receiver

from .exceptions import ProfileEmailEmpty
from .tasks import send_password_by_email
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.signals import post_profile_create, post_profile_update

if TYPE_CHECKING:
    from bkuser_core.profiles.models import Profile
logger = logging.getLogger(__name__)


@receiver(post_profile_update)
def notify_reset_email(sender, instance: "Profile", operator: str, extra_values: dict, **kwargs):
    """Notify the result of creating or updating password"""
    if not extra_values.get("should_notify"):
        return

    try:
        send_password_by_email.delay(instance.id, raw_password=extra_values["raw_password"], init=False)
    except ProfileEmailEmpty:
        raise error_codes.EMAIL_NOT_PROVIDED
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "failed to send reset password via email. [profile.id=%s, profile.username=%s]",
            instance.id,
            instance.username,
        )


@receiver(post_profile_create)
def notify_init_password(sender, instance: "Profile", operator: str, extra_values: dict, **kwargs):
    """Notify the result of creating profile"""
    if not extra_values.get("should_notify"):
        return

    try:
        send_password_by_email.delay(instance.id, raw_password=extra_values["raw_password"], init=True)
    except ProfileEmailEmpty:
        raise error_codes.EMAIL_NOT_PROVIDED
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "failed to send init password via email. [profile.id=%s, profile.username=%s",
            instance.id,
            instance.username,
        )

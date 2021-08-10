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

from bkuser_core.audit.constants import OperationEnum
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.signals import post_profile_create, post_profile_update
from django.dispatch import receiver

from .exceptions import ProfileEmailEmpty
from .tasks import send_password_by_email

logger = logging.getLogger(__name__)


@receiver(post_profile_create)
@receiver(post_profile_update)
def notify_by_email(sender, profile, operator, operation_type, extra_values, **kwargs):
    """Notify the result of creating profile"""
    if not extra_values.get("should_notify"):
        return

    init = operation_type == OperationEnum.CREATE.value
    try:
        logger.info("going to notify password via email")
        send_password_by_email.delay(profile.id, raw_password=extra_values["raw_password"], init=init)
    except ProfileEmailEmpty:
        raise error_codes.EMAIL_NOT_PROVIDED
    except Exception:  # pylint: disable=broad-except
        logger.exception("failed to send password via email")

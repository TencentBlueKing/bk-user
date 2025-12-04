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
import logging
import time
from datetime import timedelta

from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import Q
from django.utils import timezone

from bklogin.authentication.models import BkToken

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "清理无效的 bk_token 数据（已注销、绝对过期、无操作过期），保留一定时间供问题排查"

    def handle(self, *args, **options):
        now = int(time.time())
        now_datetime = timezone.now()

        invalid_token_filter = (
            # 已注销
            Q(is_logout=True, updated_at__lt=now_datetime - timedelta(seconds=settings.BK_TOKEN_CLEANUP_RETENTION_AGE))
            # 无操作过期: inactive_expires_at + inactive_age + retention_age < now
            | Q(inactive_expires_at__lt=now - settings.BK_TOKEN_INACTIVE_AGE - settings.BK_TOKEN_CLEANUP_RETENTION_AGE)
            # 绝对过期：created_at + cookie_age + offset_error_age + retention_age < now
            # Note: created_at 理论上大于 expired_at + cookie_age
            | Q(
                created_at__lt=now_datetime
                - timedelta(
                    seconds=settings.BK_TOKEN_COOKIE_AGE
                    + settings.BK_TOKEN_OFFSET_ERROR_AGE
                    + settings.BK_TOKEN_CLEANUP_RETENTION_AGE
                )
            )
        )

        # 获取一批待删除的 ID
        ids_to_delete = list(
            BkToken.objects.filter(invalid_token_filter).values_list("id", flat=True)[
                : settings.BK_TOKEN_CLEANUP_BATCH_SIZE
            ]
        )
        # 批量删除
        deleted_count, _ = BkToken.objects.filter(id__in=ids_to_delete).delete()

        logger.info("cleanup_invalid_tokens completed, deleted %d tokens", deleted_count)

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
from django.utils import timezone

from bklogin.authentication.models import BkToken

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """清理无效的 bk_token 数据

    该命令用于配合 K8S CronJob 定期执行，清理无效的登录票据

    清理逻辑：删除 created_at < now - (cookie * 2 + retention_age）的记录
    - cookie_age * 2: 兜底，确保 token 已绝对过期
    - retention_age: 额外保留时间，便于问题排查
    """

    help = "清理无效的 bk_token 数据，无效后保留一段时间再删除，避免影响短期内的问题排查"

    def handle(self, *args, **options):
        # 清理阈值：cookie_age * 2 （兜底） + retention_age (保留时间)
        threshold_seconds = settings.BK_TOKEN_COOKIE_AGE * 2 + settings.BK_TOKEN_CLEANUP_RETENTION_AGE
        threshold_time = timezone.now() - timedelta(seconds=threshold_seconds)

        # 分批删除所有无效的 bk_token
        total_deleted = 0
        while True:
            # 获取一批待删除的 ID
            ids_to_delete = list(
                BkToken.objects.filter(created_at__lt=threshold_time).values_list("id", flat=True)[
                    : settings.BK_TOKEN_CLEANUP_BATCH_SIZE
                ]
            )
            if not ids_to_delete:
                break

            # 批量删除
            deleted_count, _ = BkToken.objects.filter(id__in=ids_to_delete).delete()
            total_deleted += deleted_count

            # 每批删除后休眠 1s, 避免对数据库造成过大压力
            time.sleep(1)

        logger.info("cleanup_invalid_tokens completed, deleted %d tokens", total_deleted)

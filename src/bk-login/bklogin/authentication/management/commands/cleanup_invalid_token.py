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
import math
import time
from datetime import timedelta

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

from bklogin.authentication.models import BkToken

logger = logging.getLogger(__name__)

# 默认保留时长 7 天 (秒)
DEFAULT_RETENTION_AGE = 60 * 60 * 24 * 7
# 默认批量删除大小
DEFAULT_BATCH_SIZE = 200


class Command(BaseCommand):
    """清理无效的 bk_token 数据

    该命令用于配合 K8S CronJob 定期执行，清理无效的登录票据

    清理逻辑：删除 (cookie_age * 2 + retention_age) 之前的记录
    - cookie_age * 2: 兜底，确保 token 已绝对过期
    - retention_age: 额外保留时间，便于问题排查
    """

    help = "清理无效的 bk_token 数据"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="只统计待删除数量，不实际删除")
        parser.add_argument(
            "--retention-age",
            type=int,
            default=DEFAULT_RETENTION_AGE,
            help=f"额外保留时长（秒），默认：{DEFAULT_RETENTION_AGE} (7天)",
        )
        parser.add_argument(
            "--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help=f"每批删除大小，默认：{DEFAULT_BATCH_SIZE}"
        )

    def handle(self, *args, **options):
        # 清理阈值：cookie_age * 2 （兜底） + retention_age (保留时间)
        threshold_seconds = settings.BK_TOKEN_COOKIE_AGE * 2 + options["retention_age"]
        threshold_time = timezone.now() - timedelta(seconds=threshold_seconds)

        # 统计待删除的总数，计算批次
        total_count = BkToken.objects.filter(created_at__lt=threshold_time).count()
        if total_count == 0:
            logger.info("cleanup_invalid_token completed, no tokens to delete")
            return

        if options["dry_run"]:
            logger.info("cleanup_invalid_token dry run, %d tokens to delete", total_count)
            return

        batch_size = options["batch_size"]
        batch_count = math.ceil(total_count / batch_size)

        # 分批删除
        total_deleted = 0
        for batch_num in range(batch_count):
            ids_to_delete = list(
                BkToken.objects.filter(created_at__lt=threshold_time).values_list("id", flat=True)[:batch_size]
            )

            deleted_count, _ = BkToken.objects.filter(id__in=ids_to_delete).delete()
            total_deleted += deleted_count

            # 每批删除后休眠 1s,避免对数据库造成过大压力,最后一批跳过
            if batch_num < batch_count - 1:
                time.sleep(1)

        logger.info("cleanup_invalid_token completed, deleted %d tokens", total_deleted)

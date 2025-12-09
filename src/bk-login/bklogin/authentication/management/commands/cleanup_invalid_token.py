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


class Command(BaseCommand):
    """清理无效的 bk_token 数据

    该命令用于配合 K8S CronJob 定期执行，清理无效的登录票据

    清理逻辑：删除 (cookie_age * 2 + retention_days) 之前的记录
    - cookie_age * 2: 兜底，确保 token 已绝对过期
    - retention_days: 额外保留时间，便于问题排查
    """

    # 保留时长，默认 7 天
    RETENTION_DAYS = 7
    # 批量删除大小，默认 200
    BATCH_SIZE = 200

    help = "清理无效的 bk_token 数据"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="只统计待删除数量，不实际删除")
        parser.add_argument(
            "--retention-days",
            type=int,
            nargs="?",
            const=self.RETENTION_DAYS,
            default=self.RETENTION_DAYS,
            help=f"额外保留时长（天），默认：{self.RETENTION_DAYS}",
        )

    def handle(self, *args, **options):
        # 清理阈值：cookie_age * 2（兜底） + retention_days (保留时间)
        threshold_seconds = settings.BK_TOKEN_COOKIE_AGE * 2 + options["retention_days"] * 24 * 3600
        threshold_time = timezone.now() - timedelta(seconds=threshold_seconds)

        # 统计待删除的总数，计算批次
        total_count = BkToken.objects.filter(created_at__lt=threshold_time).count()

        if options["dry_run"]:
            self.stdout.write(f"cleanup_invalid_token dry run, {total_count} tokens to delete")
            return

        batch_count = math.ceil(total_count / self.BATCH_SIZE)

        # 分批删除
        for _ in range(batch_count):
            ids_to_delete = list(
                BkToken.objects.filter(created_at__lt=threshold_time).values_list("id", flat=True)[: self.BATCH_SIZE]
            )
            BkToken.objects.filter(id__in=ids_to_delete).delete()

            # 每批删除后休眠 1s，避免对数据库造成过大压力
            time.sleep(1)

        self.stdout.write(f"cleanup_invalid_token completed, deleted {total_count} tokens")

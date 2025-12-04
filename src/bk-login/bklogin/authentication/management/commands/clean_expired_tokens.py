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

from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import Q

from bklogin.authentication.models import BkToken

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "清理过期或无效的 bk_token 数据"

    def handle(self, *args, **options):
        now = int(time.time())

        # 删除过期/无效的 bk_token
        # Note: 这里不判断“绝对过期”（需要通过 parse token 获取 expired_at）原因如下：
        # 1. parse 每个 token 需要解密操作，性能开销大，并且无法利用数据库批量删除
        # 2. 绝对过期的 token 在 is_valid 校验失败后， inactive_expires_at 不再更新
        #    最终会因"无操作过期"被清理，只是延迟最多一个 inactive_age 周期
        deleted_count, _ = BkToken.objects.filter(
            # 已注销
            Q(is_logout=True)
            # 无操作过期: inactive_expires_at + inactive_age < now
            | Q(inactive_expires_at__lt=now - settings.BK_TOKEN_INACTIVE_AGE)
        ).delete()

        logger.info("cleanup_expired_tokens completed, deleted %d tokens", deleted_count)

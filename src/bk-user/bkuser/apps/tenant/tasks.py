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
import logging

from django.utils import timezone

from bkuser.apps.tenant.constants import TenantUserStatus
from bkuser.apps.tenant.models import CollaborationStrategy, TenantUser
from bkuser.celery import app
from bkuser.common.task import BaseTask

logger = logging.getLogger(__name__)


@app.task(base=BaseTask, ignore_result=True)
def remove_dropped_field_in_collaboration_strategy_field_mapping(tenant_id: str, field_name: str):
    """删除租户某个用户自定义字段后，需要将协同策略的 FieldMapping 中的该字段一并清除"""

    # 注：一个租户关联的协同策略不会很多，且在后台任务中，可以不用批量操作
    # 协同策略（分享方）处理源字段
    for strategy in CollaborationStrategy.objects.filter(source_tenant_id=tenant_id):
        strategy.target_config["field_mapping"] = [
            mp for mp in strategy.target_config["field_mapping"] if mp["source_field"] != field_name
        ]
        strategy.save(update_fields=["target_config", "updated_at"])

    # 协同策略（接受方）处理目标字段
    for strategy in CollaborationStrategy.objects.filter(target_tenant_id=tenant_id):
        strategy.target_config["field_mapping"] = [
            mp for mp in strategy.target_config["field_mapping"] if mp["target_field"] != field_name
        ]
        strategy.save(update_fields=["target_config", "updated_at"])


@app.task(base=BaseTask, ignore_result=True)
def update_expired_tenant_user_status():
    """定时任务：批量更新过期用户的状态"""
    logger.info("[celery] receive task: update_expired_tenant_user_status")

    now = timezone.now()

    expired_users = TenantUser.objects.filter(
        status=TenantUserStatus.ENABLED,
        account_expired_at__lte=now,
    )

    expired_count = expired_users.count()

    if expired_count == 0:
        logger.info("No expired users found.")
        return

    for user in expired_users:
        user.status = TenantUserStatus.EXPIRED
        user.updated_at = now

    TenantUser.objects.bulk_update(expired_users, ["status", "updated_at"], batch_size=100)
    logger.info("Updated %d expired users to EXPIRED status.", expired_count)

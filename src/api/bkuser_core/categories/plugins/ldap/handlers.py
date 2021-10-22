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

from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.loader import get_plugin_by_category
from bkuser_core.categories.plugins.utils import (
    delete_periodic_sync_task,
    make_periodic_sync_task,
    update_periodic_sync_task,
)
from bkuser_core.categories.signals import post_category_create, post_category_delete
from bkuser_core.user_settings.signals import post_setting_create_or_update
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_category_create)
def create_sync_tasks(sender, category, creator: str, **kwargs):
    if category.type not in [CategoryType.LDAP.value, CategoryType.MAD.value]:
        return

    logger.info("going to add periodic task for Category<%s>", category.id)
    make_periodic_sync_task(
        category_id=category.id,
        operator=creator,
        interval_seconds=get_plugin_by_category(category).extra_config["default_sync_period"],
    )


@receiver(post_category_delete)
def delete_sync_tasks(sender, category, **kwargs):
    if category.type not in [CategoryType.LDAP.value, CategoryType.MAD.value]:
        return

    logger.info("going to delete periodic task for Category<%s>", category.id)
    delete_periodic_sync_task(category.id)


@receiver(post_setting_create_or_update)
def update_sync_tasks(sender, setting, operator: str, **kwargs):
    if setting.category.type not in [CategoryType.LDAP.value, CategoryType.MAD.value]:
        return

    if not setting.meta.key == "pull_cycle":
        return

    cycle_value = int(setting.value)
    category_config = get_plugin_by_category(setting.category)
    if cycle_value <= 0:
        delete_periodic_sync_task(category_id=setting.category_id)
        return

    elif cycle_value < category_config.extra_config["min_sync_period"]:
        cycle_value = category_config.extra_config["min_sync_period"]

    # 尝试更新周期任务周期
    logger.info(
        "going to update category<%s> sync interval to %s",
        setting.category_id,
        cycle_value,
    )
    try:
        update_periodic_sync_task(category_id=setting.category_id, operator=operator, interval_seconds=cycle_value)
    except Exception:  # pylint: disable=broad-except
        logger.exception("failed to update periodic task schedule")

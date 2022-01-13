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

from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.loader import get_plugin_by_category
from bkuser_core.categories.plugins.utils import (
    delete_periodic_sync_task,
    make_periodic_sync_task,
    update_periodic_sync_task,
    delete_dynamic_filed,
)
from bkuser_core.categories.signals import post_category_create, post_category_delete, post_dynamic_field_delete
from bkuser_core.user_settings.signals import post_setting_create, post_setting_update
from django.dispatch import receiver

if TYPE_CHECKING:
    from bkuser_core.categories.models import ProfileCategory
    from bkuser_core.user_settings.models import Setting
    from bkuser_core.profiles.models import DynamicFieldInfo

logger = logging.getLogger(__name__)


@receiver(post_category_create)
def create_sync_tasks(sender, instance: "ProfileCategory", operator: str, **kwargs):
    if instance.type not in [CategoryType.LDAP.value, CategoryType.MAD.value]:
        return

    logger.info("going to add periodic task for Category<%s>", instance.id)
    make_periodic_sync_task(
        category_id=instance.id,
        operator=operator,
        interval_seconds=get_plugin_by_category(instance).extra_config["default_sync_period"],
    )


@receiver(post_category_delete)
def delete_sync_tasks(sender, instance: "ProfileCategory", **kwargs):
    if instance.type not in [CategoryType.LDAP.value, CategoryType.MAD.value]:
        return

    logger.info("going to delete periodic task for Category<%s>", instance.id)
    delete_periodic_sync_task(instance.id)


@receiver(post_setting_update)
@receiver(post_setting_create)
def update_sync_tasks(sender, instance: "Setting", operator: str, **kwargs):
    if instance.category.type not in [CategoryType.LDAP.value, CategoryType.MAD.value]:
        return

    if not instance.meta.key == "pull_cycle":
        return

    cycle_value = int(instance.value)
    category_config = get_plugin_by_category(instance.category)
    if cycle_value <= 0:
        delete_periodic_sync_task(category_id=instance.category_id)
        return

    elif cycle_value < category_config.extra_config["min_sync_period"]:
        cycle_value = category_config.extra_config["min_sync_period"]

    # 尝试更新周期任务周期
    logger.info(
        "going to update category<%s> sync interval to %s",
        instance.category_id,
        cycle_value,
    )
    try:
        update_periodic_sync_task(category_id=instance.category_id, operator=operator, interval_seconds=cycle_value)
    except Exception:  # pylint: disable=broad-except
        logger.exception("failed to update periodic task schedule")


@receiver(post_dynamic_field_delete)
def update_dynamic_field_mapping(sender, instance: "DynamicFieldInfo", **kwargs):
    delete_dynamic_filed(dynamic_field=instance.name)
    logger.info("going to delete <%s> from dynamic_field_mapping", instance.name)

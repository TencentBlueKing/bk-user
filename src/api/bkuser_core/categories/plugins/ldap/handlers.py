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

from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.plugins.utils import (
    delete_dynamic_filed,
    delete_periodic_sync_task,
    update_periodic_sync_task,
)
from bkuser_core.categories.signals import post_category_delete, post_dynamic_field_delete
from bkuser_core.user_settings.loader import ConfigProvider
from bkuser_core.user_settings.signals import post_setting_create, post_setting_update

if TYPE_CHECKING:
    from bkuser_core.categories.models import ProfileCategory
    from bkuser_core.profiles.models import DynamicFieldInfo
    from bkuser_core.user_settings.models import Setting

logger = logging.getLogger(__name__)


PULL_INTERVAL_SETTING_KEY = "pull_cycle"

DEFAULT_MIN_SYNC_PERIOD = 60


def update_or_create_sync_tasks(instance: "Setting", operator: str):
    """尝试创建或更新同步数据任务"""
    if not instance.meta.key == PULL_INTERVAL_SETTING_KEY:
        return

    cycle_value = int(instance.value)
    config_provider = ConfigProvider(instance.category_id)

    min_sync_period = config_provider.get("min_sync_period", DEFAULT_MIN_SYNC_PERIOD)
    if cycle_value <= 0:
        # 特殊约定，当设置 <= 0 时，删除周期任务
        delete_periodic_sync_task(category_id=instance.category_id)
        return
    # 保证不会用户配置不会低于插件的最低间隔限制
    elif cycle_value < min_sync_period:
        cycle_value = min_sync_period

    # 尝试更新周期任务周期
    logger.info(
        "going to update category<%s> sync interval to %s",
        instance.category_id,
        cycle_value,
    )
    try:
        update_periodic_sync_task(category_id=instance.category_id, operator=operator, interval_seconds=cycle_value)
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "failed to update periodic task schedule. [category_id=%s, operator=%s, interval_seconds=%s",
            instance.category_id,
            operator,
            cycle_value,
        )


@receiver(post_category_delete)
def delete_sync_tasks(sender, instance: "ProfileCategory", **kwargs):
    if instance.type not in [CategoryType.LDAP.value, CategoryType.MAD.value]:
        logger.warning(
            "category<%s> is %s, not a ldap or mad category, skip delete sync tasks", instance.id, instance.type
        )
        return

    logger.info("going to delete periodic task for Category<%s>, the category type is %s", instance.id, instance.type)
    delete_periodic_sync_task(instance.id)


@receiver(post_setting_update)
@receiver(post_setting_create)
def update_sync_tasks(sender, instance: "Setting", operator: str, **kwargs):
    if instance.category.type not in [CategoryType.LDAP.value, CategoryType.MAD.value]:
        logger.warning(
            "category<%s> is %s, not a ldap or mad category, skip update sync tasks",
            instance.category.id,
            instance.category.type,
        )
        return

    # 针对 pull_cycle 配置更新同步任务
    logger.info(
        "going to update periodic task for Category<%s>, the category type is %s",
        instance.category.id,
        instance.category.type,
    )
    update_or_create_sync_tasks(instance, operator)


@receiver(post_dynamic_field_delete)
def update_dynamic_field_mapping(sender, instance: "DynamicFieldInfo", **kwargs):
    """尝试刷新自定义字段映射配置"""
    logger.info("going to delete <%s> from dynamic_field_mapping", instance.name)
    delete_dynamic_filed(dynamic_field=instance.name)

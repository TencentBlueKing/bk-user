# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
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
from bkuser_core.categories.plugins.utils import delete_periodic_sync_task
from bkuser_core.categories.signals import post_category_delete
from bkuser_core.categories.utils import change_periodic_sync_task_status
from bkuser_core.recycle_bin.constants import RecycleBinObjectType
from bkuser_core.recycle_bin.models import RecycleBin
from bkuser_core.recycle_bin.signals import post_category_hard_delete, post_category_revert

if TYPE_CHECKING:
    from bkuser_core.categories.models import ProfileCategory

logger = logging.getLogger(__name__)


# pylint: disable=function-name-too-long
@receiver(post_category_delete)
def create_recycle_bin_category_relationship(sender, instance, operator: str, **kwargs):
    relationship_kv: dict = {
        "object_id": instance.id,
        "object_type": RecycleBinObjectType.CATEGORY.value,
        "operator": operator,
    }
    logger.info(
        "creating recycle bin relationship for Category<%s>, the category type is %s", instance.id, instance.type
    )
    return RecycleBin.objects.create(**relationship_kv)


@receiver(post_category_hard_delete)
def delete_category_sync_task(sender, instance: "ProfileCategory", **kwargs):
    # 目录硬删除，同步任务删除
    if instance.type == CategoryType.LOCAL.value:
        logger.warning(
            "category<%s> is %s category, skip delete sync tasks",
            instance.id,
            instance.type,
        )
        return
    logger.info("going to delete periodic task for Category<%s>, the category type is %s", instance.id, instance.type)
    delete_periodic_sync_task(instance.id, is_hard_delete=True)


@receiver(post_category_revert)
def revert_category_sync_task(sender, instance: "ProfileCategory", **kwargs):
    # 目录从软删除状态还原时候，恢复同步任务
    if instance.type == CategoryType.LOCAL.value:
        logger.warning(
            "category<%s> is %s category, skip revert sync tasks",
            instance.id,
            instance.type,
        )
        return

    logger.info("going to revert periodic task for Category<%s>, the category type is %s", instance.id, instance.type)
    change_periodic_sync_task_status(instance.id, True)

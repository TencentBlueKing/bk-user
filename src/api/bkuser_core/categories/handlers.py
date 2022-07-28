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

from django.conf import settings
from django.dispatch import receiver

from bkuser_core.bkiam.constants import IAMAction, ResourceType
from bkuser_core.bkiam.helper import IAMHelper
from bkuser_core.categories.signals import post_category_create

logger = logging.getLogger(__name__)


@receiver(post_category_create)
def create_creator_actions(sender, instance, **kwargs):
    """请求权限中心，创建新建关联权限记录"""
    if not settings.ENABLE_IAM:
        logger.info("skip creation of resource_creator_action (category related) due to ENABLE_IAM is false")
        return

    logger.info("going to create resource_creator_action for Category<%s>", instance.id)
    helper = IAMHelper()
    try:
        helper.create_creator_actions(kwargs["operator"], instance)
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "failed to create resource_creator_action (category related). [operator=%s, instance=%s]",
            kwargs["creator"],
            instance,
        )

    # 创建目录之后，默认拥有了目录 & 组织的管理能力
    try:
        helper.create_auth_by_ancestor(
            username=kwargs["operator"],
            ancestor=instance,
            target_type=ResourceType.DEPARTMENT.value,
            action_ids=[IAMAction.MANAGE_DEPARTMENT, IAMAction.VIEW_DEPARTMENT],
        )
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "failed to create resource_creator_action (department related). [operator=%s, instance=%s]",
            kwargs["operator"],
            instance,
        )

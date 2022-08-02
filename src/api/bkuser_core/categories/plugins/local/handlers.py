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
from bkuser_core.categories.signals import post_category_create

if TYPE_CHECKING:
    from bkuser_core.categories.models import ProfileCategory

logger = logging.getLogger(__name__)


@receiver(post_category_create)
def make_local_default_settings(sender, instance: "ProfileCategory", **kwargs):
    if instance.type not in [CategoryType.LOCAL.value]:
        logger.info("category<%s> is not local, skip make_local_default_settings", instance.id)
        return

    logger.info("going to make default settings for Category<%s>", instance.id)
    instance.make_default_settings()

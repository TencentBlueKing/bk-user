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
from django.db import models

logger = logging.getLogger(__name__)


class ProfileCategoryManager(models.Manager):
    def switch_default(self, name):
        """切换默认用户目录"""
        category = self.get(default=True)

        if category.name == name:
            return

        category.default = False
        category.save(update_fields=["default"])

        new_default_category = self.get(name=name)
        new_default_category.default = True
        new_default_category.save(update_fields=["default"])

    def get_default(self):
        return self.get(default=True)

    def check_writable(self, category_id) -> bool:
        try:
            return self.get(pk=category_id).type in settings.CAN_MANUAL_WRITE_LISTS
        except Exception:  # pylint: disable=broad-except
            logger.exception("cannot get category<%s>", category_id)
            return False

    def get_max_order(self) -> int:
        orders = self.all().values_list("order", flat=True)
        # 若没有子组织，则返回 1
        if not orders:
            orders = [
                1,
            ]

        return max(orders)

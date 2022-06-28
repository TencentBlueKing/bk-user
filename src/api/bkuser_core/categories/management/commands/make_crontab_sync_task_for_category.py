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
import traceback

from django.core.management.base import BaseCommand

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.plugins.utils import make_periodic_sync_task

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "make a sync task for a given category"

    def add_arguments(self, parser):
        parser.add_argument("--category_id", type=str, help="目录ID")
        parser.add_argument("--interval", type=int, help="同步周期(单位秒)")
        parser.add_argument("--operator", type=str, default="admin", help="操作者")

    def handle(self, *args, **options):
        category_id = options.get("category_id")
        interval = options.get("interval")
        operator = options.get("operator")

        self.stdout.write(f"Will add a sync task for category_id={category_id}, run every {interval} seconds")

        try:
            category = ProfileCategory.objects.get(id=category_id)
        except ProfileCategory.DoesNotExist:
            self.stdout.write(f"Category {category_id} does not exist, exit")
            return

        self.stdout.write(f"Category {category_id} exists, name={category.display_name} and type={category.type}")

        try:
            make_periodic_sync_task(int(category_id), operator, interval)
        except Exception:  # pylint: disable=broad-except
            self.stdout.write(traceback.format_exc())
            self.stdout.write(f"Failed to add sync task for category {category_id}")

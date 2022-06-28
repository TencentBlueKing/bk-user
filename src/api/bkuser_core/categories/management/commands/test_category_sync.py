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
import uuid

from django.core.management.base import BaseCommand

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.tasks import adapter_sync

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "test category sync"

    def add_arguments(self, parser):
        parser.add_argument("--category_type", type=str, help="目录类型")
        parser.add_argument("--dry_run", action="store_true")
        parser.add_argument("--verbose", action="store_true")
        parser.add_argument("--excel_file", type=str, help="本地 Excel")

    def handle(self, *args, **options):
        category_type = options["category_type"]
        excel_file = options["excel_file"]
        task_id = uuid.uuid4()
        self.stdout.write(f"Your Task ID: {str(task_id)}")

        if excel_file:
            try:
                adapter_sync(
                    ProfileCategory.objects.filter(type=category_type)[0].pk,
                    task_id=task_id,
                    raw_data_file=excel_file,
                )
            except Exception:  # pylint: disable=broad-except
                self.stdout.write(traceback.format_exc())
                logger.exception("can not find category by type<%s>", category_type)
            return

        try:
            adapter_sync(ProfileCategory.objects.filter(type=category_type)[0].pk, task_id=task_id)
        except Exception:  # pylint: disable=broad-except
            self.stdout.write(traceback.format_exc())
            logger.exception("can not find category by type<%s>", category_type)

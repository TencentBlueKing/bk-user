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

from django.core.management.base import BaseCommand

from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.plugins.constants import PLUGIN_NAME_SETTING_KEY
from bkuser_core.profiles.validators import validate_domain
from bkuser_core.user_settings.models import Setting, SettingMeta

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Add pluggable category"

    def add_arguments(self, parser):
        parser.add_argument("--domain", type=str, help="目录Domain")
        parser.add_argument("--name", type=str, help="目录展示名")
        parser.add_argument("--plugin", type=str, help="插件名")

    def handle(self, *args, **options):
        domain = options["domain"]
        name = options["name"]
        plugin = options["plugin"]

        if not domain:
            self.stdout.write("domain is required")
            return

        if domain.startswith("@"):
            self.stdout.write("domain should not start with '@'")
            return

        self.stdout.write("validating domain...")
        validate_domain(domain)

        logger.info("creating SettingMeta %s", PLUGIN_NAME_SETTING_KEY)
        meta, _ = SettingMeta.objects.get_or_create(
            key=PLUGIN_NAME_SETTING_KEY,
            required=True,
            category_type=CategoryType.PLUGGABLE.value,
        )

        logger.info("creating category Name<%s> Domain<%s>", name, domain)
        category, _ = ProfileCategory.objects.get_or_create(
            type=CategoryType.PLUGGABLE.value,
            domain=domain,
            defaults={"display_name": name},
        )

        logger.info("inserting plugin name<%s> into setting", plugin)
        Setting.objects.update_or_create(category_id=category.id, meta=meta, defaults={"value": plugin})

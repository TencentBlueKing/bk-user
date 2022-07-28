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

from bkuser_core.profiles.models import Profile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "refresh profiles extras format"

    def add_arguments(self, parser):
        parser.add_argument("--dry_run", action="store_true")
        parser.add_argument("--verbose", action="store_true")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        verbose = options["verbose"]

        updated = []
        failed = []
        skipped = []

        if dry_run:
            logger.info("============== DRY-RUN OUTPUT ==============")

        for a in Profile.objects.all():
            if isinstance(a.extras, dict):
                if verbose:
                    logger.info(f"{a.username}'s extras<{a.extras}> format already dict, skip")
                skipped.append(str(a.id))
                continue

            if not isinstance(a.extras, list):
                if verbose:
                    logger.info(f"Profile<{a.id}-{a.username}> has unknown format(not dict or list), skip")
                skipped.append(str(a.id))
                continue

            try:
                a.extras = {x["key"]: x["value"] for x in a.extras if x["value"]}
                if not dry_run:
                    a.save(update_fields=["extras"])

                logger.info(f"Profile<{a.id}-{a.username}>'s extras updating to new format {a.extras}")
                updated.append(str(a.id))
            except Exception:  # pylint: disable=broad-except
                logger.info(f"failed to update a<{a.username}>'s extras<{a.extras}>")
                failed.append(str(a.id))
                continue

        logger.info(f"skipped: {len(skipped)}, updated: {len(updated)}, failed: {len(failed)}")
        if verbose:
            logger.info("skipped ids: %s", ",".join(skipped))
            logger.info("updated ids: %s", ",".join(updated))
            logger.info("failed ids: %s", ",".join(failed))

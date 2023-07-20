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

from django.db import transaction

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.celery import app
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile
from bkuser_core.recycle_bin.constants import RecycleBinObjectType
from bkuser_core.recycle_bin.models import RecycleBin
from bkuser_core.user_settings.models import Setting

logger = logging.getLogger(__name__)


# pylint: disable=function-name-too-long
@app.task
def hard_delete_category_related_resource(category_id: int):
    with transaction.atomic():
        try:
            instance = ProfileCategory.objects.get(id=category_id)
            if instance.default:
                logger.warning("Category<%s-%s> is default, can not delete", instance.id, instance.display_name)
                return
            if not instance.is_deleted:
                logger.warning("Category<%s-%s> is not soft deleted", instance.id, instance.display_name)
                return
        except ProfileCategory.DoesNotExist:
            logger.exception("delete category<%s-%s> failed, category is not exist", instance.id, instance.type)
            return

        logger.info("going to delete settings for Category<%s-%s>", instance.id, instance.type)
        Setting.objects.filter(category_id=category_id).delete()

        profiles = Profile.objects.filter(category_id=category_id)
        departments = Department.objects.filter(category_id=category_id)
        # 清理资源: 人员，部门，目录设置
        logger.info(
            "Categories <%s>: going to delete profiles-<count: %s>, departments-<count: %s> and settings",
            category_id,
            profiles.count(),
            departments.count(),
        )
        departments.delete()
        profiles.delete()

        RecycleBin.objects.filter(object_type=RecycleBinObjectType.CATEGORY.value, object_id=category_id).delete()
        instance.hard_delete()

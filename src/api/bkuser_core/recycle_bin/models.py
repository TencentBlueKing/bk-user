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
import datetime

from django.db import models
from django.utils import timezone

from bkuser_core.api.web.utils import get_category, get_department, get_profile
from bkuser_core.common.models import TimestampedModel
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.profiles.models import Profile
from bkuser_core.recycle_bin.constants import RecycleBinObjectStatus, RecycleBinObjectType
from bkuser_core.user_settings.constants import GlobalSettingsEnableNamespaces
from bkuser_core.user_settings.loader import GlobalConfigProvider


class RecycleBin(TimestampedModel):
    object_type = models.CharField("对象类型", choices=RecycleBinObjectType.get_choices(), max_length=64, default="")
    object_id = models.IntegerField("对象id")
    operator = models.CharField("操作人", max_length=255, default="")
    status = models.CharField(
        "数据状态",
        choices=RecycleBinObjectStatus.get_choices(),
        max_length=64,
        default=RecycleBinObjectStatus.SOFT_DELETED.value,
    )

    @property
    def expires(self) -> int:
        """
        过期剩余天数
        """
        config_loader = GlobalConfigProvider(namespace=GlobalSettingsEnableNamespaces.RECYCLING_STRATEGY.value)
        retention_days = config_loader.get("retention_days")
        expire_at = self.create_time + datetime.timedelta(days=int(retention_days))
        _expires = expire_at - timezone.now()
        return _expires.days

    @property
    def profile_count(self):
        # 目录/部门下人数
        if self.object_type == RecycleBinObjectType.CATEGORY.value:
            return Profile.objects.filter(category_id=self.object_id).count()
        if self.object_type == RecycleBinObjectType.DEPARTMENT.value:
            return DepartmentThroughModel.objects.filter(department_id=self.object_id).count()

    @property
    def department_count(self):
        # 目录下部门数量
        if self.object_type in [RecycleBinObjectType.DEPARTMENT.value, RecycleBinObjectType.PROFILE.value]:
            return
        return Department.objects.filter(category_id=self.object_id).count()

    def get_map_object(self):
        # 根据映射关系获取对象
        object_map = {
            RecycleBinObjectType.CATEGORY.value: get_category,
            RecycleBinObjectType.DEPARTMENT.value: get_department,
            RecycleBinObjectType.PROFILE.value: get_profile,
        }
        return object_map[self.object_type](self.object_id)

    def __str__(self):
        return f"{self.object_type}-{self.object_id}-{self.status}"

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "回收站信息"
        verbose_name_plural = "回收站信息"
        index_together = ("object_type", "object_id")

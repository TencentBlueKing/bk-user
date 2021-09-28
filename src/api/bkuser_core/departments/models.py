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

from bkuser_core.audit.models import AuditObjMetaInfo
from bkuser_core.common.bulk_update.manager import BulkUpdateManager
from bkuser_core.departments.managers import DepartmentManager
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.models import Profile
from django.db import models
from django.db.models import Q
from jsonfield import JSONField
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey

logger = logging.getLogger(__name__)


class TimestampMPTTModel(MPTTModel):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Department(TimestampMPTTModel):
    """组织"""

    name = models.CharField("组织名称", max_length=255)
    # 部门标识，不同于自增 id，多数情况存储各个公司组织架构系统的id, 非必须
    code = models.CharField("组织标识", null=True, blank=True, unique=True, max_length=64)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    order = models.IntegerField("顺序", default=1)
    profiles = models.ManyToManyField(Profile, blank=True, related_name="departments", verbose_name="成员")
    enabled = models.BooleanField("是否启用", default=True)
    extras = JSONField("额外信息", default={})

    category_id = models.IntegerField("用户目录ID", null=True, blank=True)

    objects = DepartmentManager()
    tree_objects = TreeManager()
    update_objects = BulkUpdateManager()

    class Meta:
        ordering = ["id"]
        verbose_name = "组织表"
        verbose_name_plural = "组织表"

    def __str__(self):
        return f"{self.id}-{self.name}"

    def get_profiles(self, recursive: bool = False, wildcard_search: str = None) -> models.QuerySet:
        if not recursive:
            target = self.profiles.exclude(status=ProfileStatus.DELETED.value)
        else:
            # 使用 DB 做 distinct 非常慢，所以先用 id 去重 TODO: 为什么差别这么大，有时间慢慢研究
            department_ids = self.get_descendants(include_self=True).values_list("id", flat=True)
            ids = DepartmentThroughModel.objects.filter(department_id__in=department_ids).values_list(
                "profile_id", flat=True
            )

            # 当后端 DB 不支持 microseconds 时 create_time 会无法准确排序
            target = Profile.objects.filter(id__in=ids).exclude(enabled=False).order_by("-id")

        if wildcard_search:
            target = target.filter(Q(username__icontains=wildcard_search) | Q(display_name__icontains=wildcard_search))

        target = target.prefetch_related("departments", "leader")
        return target

    def to_audit_info(self):
        """提供审计元信息"""
        return AuditObjMetaInfo(key=self.pk, display_name=self.name, category_id=self.category_id)

    @property
    def full_name(self):
        """如：总公司/子公司/分公司"""
        # 根目录不再多查一次 DB
        if self.level == 0:
            return self.name

        return "/".join(self.get_ancestors(include_self=True).values_list("name", flat=True))

    def add_profile(self, profile_instance) -> bool:
        """为该部门增加人员
        :return added: bool
        """
        if profile_instance not in self.profiles.all():
            self.profiles.add(profile_instance)
            return True
        return False

    def enable(self):
        """软删除恢复"""
        self.enabled = True
        self.save(update_fields=["enabled", "update_time"])

    def delete(self, *args, **kwargs):
        """默认为软删除"""
        # TODO: 区分软删除，用 disable 方法代替
        self.enabled = False
        self.save(update_fields=["enabled", "update_time"])

        # 解除关系
        self.profiles.clear()
        return

    def hard_delete(self, *args, **kwargs):
        """提供真实删除"""
        return super().delete(*args, **kwargs)

    def get_max_order_in_children(self) -> int:
        # TODO: 使用 lft rght 判断，删除 order 字段
        orders = self.children.all().values_list("order", flat=True)
        # 若没有子组织，则返回 1
        if not orders:
            orders = [1]

        return max(orders)


DepartmentThroughModel = Department.profiles.through

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

from django.db import models
from django.db.models import Q
from jsonfield import JSONField
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey

from bkuser_core.audit.models import AuditObjMetaInfo
from bkuser_core.common.bulk_update.manager import BulkUpdateManager
from bkuser_core.departments.cache import (
    get_department_full_name_from_local_cache,
    get_department_has_children_from_local_cache,
    set_department_full_name_to_local_cache,
    set_department_has_children_to_local_cache,
)
from bkuser_core.departments.managers import DepartmentManager
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.models import Profile

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

        index_together = [
            ["tree_id", "lft", "rght"],
            ["parent_id", "tree_id", "lft"],
        ]

    def __str__(self):
        return f"{self.id}-{self.name}"

    def get_profile_count(self, recursive: bool = False) -> int:
        # TODO: add a cache if needed
        if not recursive:
            return self.profiles.exclude(status=ProfileStatus.DELETED.value).count()

        department_ids = self.get_descendants(include_self=True).values_list("id", flat=True)
        ids = DepartmentThroughModel.objects.filter(department_id__in=department_ids).values_list(
            "profile_id", flat=True
        )
        if len(ids) == 0:
            return 0
        return Profile.objects.filter(id__in=ids, enabled=True).count()

    # FIXME: should be moved into the manager.py? Departments.objects.get_profiles()
    def get_profiles(self, recursive: bool = False, wildcard_search: str = None) -> models.QuerySet:
        if not recursive:
            # FIXME: 为什么滤掉了 status.DELETE? 而不是通过 enabled=False过滤?
            target = self.profiles.exclude(status=ProfileStatus.DELETED.value)
        else:
            # 使用 DB 做 distinct 非常慢，所以先用 id 去重 TODO: 为什么差别这么大，有时间慢慢研究
            department_ids = self.get_descendants(include_self=True).values_list("id", flat=True)
            ids = DepartmentThroughModel.objects.filter(department_id__in=department_ids).values_list(
                "profile_id", flat=True
            )

            # 当后端 DB 不支持 microseconds 时 create_time 会无法准确排序
            # target = Profile.objects.filter(id__in=ids).exclude(enabled=False).order_by("-id")
            target = Profile.objects.filter(id__in=ids, enabled=True).order_by("-id")

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

        # NOTE: serializer中配置了full_name, 导致放大查询, 需要使用cache优化这里的逻辑
        # => 场景: 查用户列表分页, page_size=100时同一个部门的用户只会触发一次查询
        # 这里是用 local mem cache for 5s, 每个worker内存短时cache, 如果部门full_name有变更, 最多5s生效
        ok, full_name = get_department_full_name_from_local_cache(self.id)
        if ok:
            return full_name

        # SQL:
        # SELECT `name` FROM `departments_department`
        # WHERE (`lft` <= 2 AND `rght` >= 13 AND `tree_id` = 5) ORDER BY `lft` ASC;
        # 新版: 加了索引 tree_id + lft + rght
        full_name = "/".join(self.get_ancestors(include_self=True).values_list("name", flat=True))

        set_department_full_name_to_local_cache(self.id, full_name)

        return full_name

    @property
    def has_children(self):
        """仅返回启用的子部门"""
        # 原始方案
        # SQL:
        # SELECT (1) AS `a` FROM departments_department
        # WHERE (`lft` >= 2 AND `lft` <= 3 AND `tree_id` = 4 AND `enabled`) LIMIT 1;
        # 走tree_id索引, 然后 where lft/rght/enabled
        # return obj.get_descendants(include_self=False).filter(enabled=True).exists()

        # 折中方案: 1 先判断是否有子节点, 没有直接返回False, 有子节点再fallback到数据库查询(enabled=True)

        # 不会带来数据库查询, 但是过滤不了 enabled=True; 约省去50%的数据库查询
        if self.get_descendant_count() == 0:
            return False

        # 这里是用 local mem cache for 5s, 每个worker内存短时cache, 如果部门full_name有变更, 最多5s生效
        ok, has_children = get_department_has_children_from_local_cache(self.id)
        if ok:
            return has_children

        # SQL:
        # SELECT (1) AS `a` FROM `departments_department` WHERE (`parent_id` = 1 AND `enabled`) LIMIT 1;
        # 走 parent_id 索引, 然后enabled=1 limit 1
        has_children = self.children.filter(enabled=True).exists()

        set_department_has_children_to_local_cache(self.id, has_children)

        return has_children

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

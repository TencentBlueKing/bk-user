# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

from typing import Dict, List

from bkuser.apps.data_source.models import DataSourceDepartmentRelation
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum


class DepartmentAncestorCache:
    """部门祖先缓存"""

    def __init__(self):
        self.cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.DEPARTMENT_ANCESTOR)
        self.cache_timeout = 60 * 60 * 24 * 30

    def batch_get(self, dept_ids: List[int]) -> Dict[int, List[int]]:
        """批量获取部门的祖先 ID 列表"""
        # 1. 批量获取已缓存的部门祖先 ID 列表
        cache_data = self.cache.get_many(dept_ids)

        dept_ancestor_map = {}
        cache_miss_dept_ids = []

        for dept_id in dept_ids:
            if dept_id in cache_data:
                dept_ancestor_map[dept_id] = cache_data[dept_id]
            else:
                cache_miss_dept_ids.append(dept_id)

        # 2. 查询缓存未命中的部门祖先 ID 列表，并缓存
        if cache_miss_dept_ids:
            cache_miss_ancestor_map = self._fetch_dept_ancestors_map(cache_miss_dept_ids)
            self._batch_set(cache_miss_ancestor_map)
            dept_ancestor_map.update(cache_miss_ancestor_map)

        return dept_ancestor_map

    def _batch_set(self, dept_ancestor_map: Dict[int, List[int]]) -> None:
        """批量缓存部门的祖先 ID 列表"""
        self.cache.set_many(dept_ancestor_map, timeout=self.cache_timeout)

    def batch_delete(self, dept_ids: List[int]) -> None:
        """批量删除指定部门的祖先 ID 缓存"""
        self.cache.delete_many(dept_ids)

    def _fetch_dept_ancestors_map(self, dept_ids: List[int]) -> Dict[int, List[int]]:
        """批量查询部门与其祖先 ID 列表之间的映射"""
        dept_ancestor_map = {}

        relations = DataSourceDepartmentRelation.objects.filter(department_id__in=dept_ids)
        for rel in relations:
            dept_ancestor_map[rel.department_id] = list(rel.get_ancestors().values_list("department_id", flat=True))

        return dept_ancestor_map

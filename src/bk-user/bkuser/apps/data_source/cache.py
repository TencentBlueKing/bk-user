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

    def batch_get(self, department_ids: List[int]) -> Dict[int, List[int]]:
        """批量获取部门的祖先 ID 列表"""
        cache_keys = [str(dept_id) for dept_id in department_ids]
        cache_data = self.cache.get_many(cache_keys)

        department_ancestor_map = {}
        uncached_department_ids = []

        for dept_id in department_ids:
            if dept_id in cache_data:
                department_ancestor_map[dept_id] = cache_data[dept_id]
            else:
                uncached_department_ids.append(dept_id)

        # 缓存未命中的部门祖先 ID 列表
        if uncached_department_ids:
            uncached_department_ancestor_map = {}

            relations = DataSourceDepartmentRelation.objects.filter(department_id__in=uncached_department_ids)
            for rel in relations:
                uncached_department_ancestor_map[rel.department_id] = list(
                    rel.get_ancestors().values_list("department_id", flat=True)
                )

            # 批量缓存祖先 ID 列表
            self._batch_set(uncached_department_ancestor_map)

            department_ancestor_map.update(uncached_department_ancestor_map)

        return department_ancestor_map

    def _batch_set(self, department_ancestor_map: Dict[int, List[int]]) -> None:
        """批量缓存部门的祖先 ID 列表"""
        cache_data = {}
        for dept_id, ancestor_ids in department_ancestor_map.items():
            cache_data[str(dept_id)] = ancestor_ids

        self.cache.set_many(cache_data, timeout=self.cache_timeout)

    def batch_delete(self, department_ids: List[int]) -> None:
        """批量删除指定部门的祖先 ID 缓存"""
        cache_keys = [str(dept_id) for dept_id in department_ids]
        self.cache.delete_many(cache_keys)

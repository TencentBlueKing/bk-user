# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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

from typing import Dict, List, Set, Tuple

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceDepartmentRelation
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum, cached


class DataSourceCache:
    """数据源基础信息缓存（单一底层缓存 + 多快捷方法）"""

    @staticmethod
    @cached(timeout=60)
    def _get_infos() -> List[Tuple[int, str, str]]:
        """底层缓存：[(id, type, owner_tenant_id), ...]"""
        return list(DataSource.objects.values_list("id", "type", "owner_tenant_id"))

    # ---------- 映射 ----------

    @classmethod
    def get_type_map(cls) -> Dict[int, str]:
        """数据源 ID → 类型"""
        return {ds_id: ds_type for ds_id, ds_type, _ in cls._get_infos()}

    @classmethod
    def get_owner_tenant_id_map(cls) -> Dict[int, str]:
        """数据源 ID → 归属租户 ID"""
        return {ds_id: owner for ds_id, _, owner in cls._get_infos()}

    # ---------- 单条查询 ----------

    @classmethod
    def get_type(cls, data_source_id: int) -> str:
        return cls.get_type_map()[data_source_id]

    @classmethod
    def get_owner_tenant_id(cls, data_source_id: int) -> str:
        return cls.get_owner_tenant_id_map()[data_source_id]

    # ---------- ID 集合快捷方法 ----------

    @classmethod
    def ids_by_type(cls, ds_type_filter: str) -> Set[int]:
        """指定类型的所有数据源 ID"""
        return {ds_id for ds_id, ds_type, _ in cls._get_infos() if ds_type == ds_type_filter}

    @classmethod
    def real_ids(cls) -> Set[int]:
        """所有 REAL 类型数据源 ID"""
        return {ds_id for ds_id, ds_type, _ in cls._get_infos() if ds_type == DataSourceTypeEnum.REAL}

    @classmethod
    def non_builtin_management_ids(cls) -> Set[int]:
        """所有非内置管理类型数据源 ID（REAL + VIRTUAL）"""
        return {ds_id for ds_id, ds_type, _ in cls._get_infos() if ds_type != DataSourceTypeEnum.BUILTIN_MANAGEMENT}

    @classmethod
    def real_ids_by_owner(cls, owner_tenant_id: str) -> Set[int]:
        """指定归属租户的 REAL 类型数据源 ID"""
        return {
            ds_id
            for ds_id, ds_type, owner in cls._get_infos()
            if ds_type == DataSourceTypeEnum.REAL and owner == owner_tenant_id
        }

    @classmethod
    def ids_by_owner(cls, owner_tenant_id: str) -> Set[int]:
        """指定归属租户的所有数据源 ID（不限类型）"""
        return {ds_id for ds_id, _, owner in cls._get_infos() if owner == owner_tenant_id}

    @classmethod
    def virtual_id_by_owner(cls, owner_tenant_id: str) -> int:
        """指定归属租户的虚拟数据源 ID，不存在时返回 0"""
        for ds_id, ds_type, owner in cls._get_infos():
            if ds_type == DataSourceTypeEnum.VIRTUAL and owner == owner_tenant_id:
                return ds_id
        return 0


class DepartmentAncestorCache:
    """部门祖先缓存"""

    def __init__(self):
        self.cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.DEPARTMENT_ANCESTOR)
        self.cache_timeout = 60 * 60 * 24 * 30

    def batch_get(self, dept_ids: List[int]) -> Dict[int, List[int]]:
        """批量获取部门的祖先 ID 列表"""
        # 1. 批量获取已缓存的部门祖先 ID 列表
        hit_data = self.cache.get_many(dept_ids)

        # 2. 全部都命中缓存
        miss_dept_ids = list(set(dept_ids) - set(hit_data.keys()))
        if not miss_dept_ids:
            return hit_data

        # 3. 未命中缓存的部门 ID，需 DB 查询并添加到缓存里
        miss_data = self._fetch_dept_ancestors_map(miss_dept_ids)
        self._batch_set(miss_data)

        return hit_data | miss_data

    def _batch_set(self, dept_ancestor_map: Dict[int, List[int]]) -> None:
        """批量缓存部门的祖先 ID 列表"""
        self.cache.set_many(dept_ancestor_map, timeout=self.cache_timeout)

    def batch_delete(self, dept_ids: List[int]) -> None:
        """批量删除指定部门的祖先 ID 缓存"""
        self.cache.delete_many(dept_ids)

    def _fetch_dept_ancestors_map(self, dept_ids: List[int]) -> Dict[int, List[int]]:
        """批量查询部门与其祖先 ID 列表之间的映射"""
        rels = DataSourceDepartmentRelation.objects.filter(department_id__in=dept_ids)

        return {r.department_id: list(r.get_ancestors().values_list("department_id", flat=True)) for r in rels}

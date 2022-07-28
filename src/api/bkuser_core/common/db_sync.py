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
import math
from dataclasses import dataclass, field
from enum import auto
from threading import RLock
from typing import Any, ClassVar, List, Optional, Type

from django.db import connections, models

from bkuser_core.common.enum import AutoLowerEnum

logger = logging.getLogger(__name__)


class SyncOperation(AutoLowerEnum):
    ADD = auto()
    UPDATE = auto()


class SyncModelMeta:
    """
    主要是针对不同的后端同步系统的同步DB模型描述

    例如，
    excel 导入数据时，是用 username 而不是 code 作为唯一标识
    ldap or mad 是有 uuid 作为 code 的
    """

    target_model: ClassVar[Type[models.Model]]
    table_name: ClassVar[str]
    is_relation_table: bool = False
    pk_field: str = "id"
    update_exclude_fields: List = []
    use_bulk: bool = True
    # TODO: support unique_together
    unique_key_field: ClassVar[str] = ""
    sharding_size: int = 1000

    @classmethod
    def has_unique_key(cls) -> bool:
        return bool(cls.unique_key_field)


@dataclass
class SyncModelManager:
    """同步DB模型管理器

    聚焦于将内存对象同步到 DB, 支持插入 & 更新
    """

    meta: Type[SyncModelMeta]

    # too big sql may cause "mysql gone away"
    adding_items: list = field(default_factory=list)
    updating_items: list = field(default_factory=list)
    _action_map_cache: dict = field(default_factory=dict)

    _default_sync_operation = SyncOperation.ADD.value
    _lock = RLock()

    def get(self, unique_key: Any) -> Optional[Any]:
        if not self.meta.has_unique_key():
            raise ValueError(f"there is no 'unique_key_field' in model meta<{self.meta}>, cannot get certain item")

        return self._action_map_cache.get(unique_key)

    def exists(self, db_obj: models.Model) -> bool:
        """是否在行为缓存中已存在某个资源"""
        if not self.meta.has_unique_key():
            raise ValueError(f"there is no 'unique_key_field' in model meta<{self.meta}>, cannot get certain item")

        return getattr(db_obj, self.meta.unique_key_field) in self._action_map_cache

    def add(self, db_obj: models.Model, operation: SyncOperation = None) -> None:
        """增加一个行为(Action)缓存到队列

        一个 DB 对象，加一个操作，组成一个行为 Action
        """
        operation = operation or self._default_sync_operation

        if not isinstance(db_obj, self.meta.target_model):
            raise ValueError(f"db_obj<{db_obj}> is not a {self.meta.target_model}")

        _cache_key = None
        if self.meta.unique_key_field:
            unique_key = getattr(db_obj, self.meta.unique_key_field)
            if unique_key and unique_key in self._action_map_cache:
                logger.debug("action (%s-%s) already in item cache, skipping", operation, db_obj)
                return

            # 尚不存在，添加 unique_key cache
            _cache_key = unique_key

        self._append(db_obj, operation, _cache_key)

    def _append(self, item: models.Model, operation: SyncOperation = None, cache_key: str = None):
        operation = operation or self._default_sync_operation
        with self._lock:
            if operation == SyncOperation.ADD.value:
                self.adding_items.append(item)
            else:
                self.updating_items.append(item)

            if cache_key:
                self._action_map_cache[cache_key] = item

    ######################
    # 以下是涉及数据库的操作 #
    ######################

    def sync_to_db(self):
        """将内存对象同步到数据库"""
        if self.meta.use_bulk:
            self._sync_in_batches()
        else:
            self._sync_one_by_one()

    def get_latest_auto_id(self) -> int:
        """找到最大的自增 id"""
        with connections["default"].cursor() as cursor:
            cursor.execute(
                "SELECT `AUTO_INCREMENT` "
                "FROM  INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_NAME = '%s';" % self.meta.table_name
            )
            all_value = cursor.fetchall()
            all_value = [v[0] for v in all_value]
            return max(all_value)

    def make_slices(self, origin_list: List) -> List:
        """内存对象列表切片, 避免触发 sql 异常"""
        origin_len = len(origin_list)
        if origin_len < self.meta.sharding_size:
            return [
                origin_list,
            ]

        logger.info("======== Slicing =======")
        slices = []
        count = math.ceil(origin_len / self.meta.sharding_size)
        for i in range(count):
            slices.append(origin_list[self.meta.sharding_size * i : self.meta.sharding_size * (i + 1)])

        return slices

    def _sync_one_by_one(self):
        """将内存对象逐个写入到数据库"""
        logger.info(
            "======== Going to adding items<%s> (%s), instead of bulk ========",
            self.meta.target_model.__name__,
            len(self.adding_items),
        )
        for adding in self.adding_items:
            adding.save()

        # 关系表不需要更新
        if self.meta.is_relation_table:
            return

        logger.info(
            "======== Going to updating items<%s> (%s), instead of bulk ========",
            self.meta.target_model.__name__,
            len(self.updating_items),
        )
        for updating in self.updating_items:
            updating.save()

    def _sync_in_batches(self):
        """使用 bulk_create 和 bulk_update(只有非关系表需要执行更新操作) 将内存对象批量同步到数据库"""
        # 使用 bulk_create 将内存对象写入到数据库
        self._sync_adding()

        # 关系表不需要更新
        if self.meta.is_relation_table:
            return

        # 使用 bulk_update 将内存对象的变更批量写入到数据库
        if not self.meta.update_exclude_fields:
            raise ValueError("%s should specific field not updating" % self.meta.target_model)
        self._sync_updating()

    def _sync_adding(self):
        manager = "objects"
        method = "bulk_create"
        items = self.adding_items
        extra_params = {}
        self._sync(items, manager, method, extra_params)

    def _sync_updating(self):
        manager = "update_objects"
        method = "bulk_update"
        items = self.updating_items
        extra_params = {"exclude_fields": self.meta.update_exclude_fields, "pk_field": self.meta.pk_field}
        self._sync(items, manager, method, extra_params)

    def _sync(self, items: List, manager: str, method: str, extra_params: dict):
        target_model_name = self.meta.target_model.__name__
        if not items:
            logger.info("======== %s is empty to %s 📭 =========", target_model_name, method)
            return

        logger.info("======== Going to %s(count: %s) for %s =========", method, len(items), target_model_name)

        current_count = 0
        total_fail_count = 0
        total_fail_records = []
        slices = self.make_slices(items)
        for idx, part in enumerate(slices):
            logger.info(
                "======== Syncing part of %s(%s/%s) current: %d + %d =========",
                target_model_name,
                idx + 1,
                len(slices),
                current_count,
                len(part),
            )
            current_count = current_count + len(part)
            # NOTE: 批量插入失败, 会导致整体同步任务失败
            # - 优化: 批量插入失败, 切换成单条插入
            # - 优化: 单条插入失败, continue (会打详细日志)
            try:
                getattr(getattr(self.meta.target_model, manager), method)(part, **extra_params)
            except Exception:
                logger.warning(
                    "%s %s failed, count=%d, extra_params=%s, will try to sync one by one",
                    target_model_name,
                    method,
                    len(part),
                    extra_params,
                )
                for one in part:
                    try:
                        one.save()
                        continue
                    except Exception:
                        total_fail_count += 1
                        logger.exception(
                            "%s %s: save one by one fail, item=%s, will not be updated, detail=%s",
                            target_model_name,
                            method,
                            one,
                            vars(one),
                        )
                        total_fail_records.append(one)
                        continue
                # 原先的逻辑: raise
                # raise
        if total_fail_count > 0:
            logger.error(
                "%s %s failed, total_fail_count=%d, total_fail_records=%s",
                target_model_name,
                method,
                total_fail_count,
                total_fail_records,
            )
            logger.info("======== %s synced. and got %d fail ✅ ========", target_model_name, total_fail_count)
            # TODO: should do something to let the admin know some record fail!
        else:
            logger.info("======== %s synced. ✅ ========", target_model_name)

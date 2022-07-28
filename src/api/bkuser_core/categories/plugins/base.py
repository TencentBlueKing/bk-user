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
import logging
from abc import abstractmethod
from collections import UserDict, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, ClassVar, Dict, List, MutableMapping, Optional, Type, TypeVar

from django.db.models import Model
from typing_extensions import Protocol

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.plugins.constants import SYNC_LOG_TEMPLATE_MAP, SyncStep
from bkuser_core.categories.plugins.metas import DepartmentMeta, DepartmentProfileMeta, LeaderProfileMeta, ProfileMeta
from bkuser_core.common.db_sync import SyncModelManager, SyncModelMeta, SyncOperation
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.profiles.models import LeaderThroughModel, Profile
from bkuser_core.user_settings.loader import ConfigProvider

logger = logging.getLogger(__name__)


@dataclass
class _SyncRecord:
    detail: Dict[str, str]
    success: bool = True
    dt: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class _SyncReportItem:
    step: SyncStep
    successful: bool
    logs: List[str] = field(default_factory=list)
    successful_items: List[_SyncRecord] = field(default_factory=list)
    failed_items: List[_SyncRecord] = field(default_factory=list)


@dataclass
class SyncContext:
    records: Dict[SyncStep, List[_SyncRecord]] = field(default_factory=lambda: defaultdict(list))
    failed: Dict[SyncStep, bool] = field(default_factory=dict)

    @contextmanager
    def __call__(self, op_steps: List[SyncStep]):
        try:
            yield self
        except Exception:
            for step in op_steps:
                self.mark_failed(step)
            raise

    def add_record(self, step: SyncStep, success: bool, **detail):
        self.records[step].append(_SyncRecord(detail=detail, success=success))

    def mark_failed(self, step: SyncStep):
        self.failed[step] = True

    def report(self) -> List[_SyncReportItem]:
        result = []
        for step in [
            SyncStep.DEPARTMENTS,
            SyncStep.USERS,
            SyncStep.DEPT_USER_RELATIONSHIP,
            SyncStep.USERS_RELATIONSHIP,
        ]:
            report = _SyncReportItem(step=step, successful=not self.failed.get(step))
            for record in self.records[step]:
                if not record.success:
                    report.failed_items.append(record)
                else:
                    report.successful_items.append(record)
                report.logs.append(
                    "{dt}: {msg}".format(
                        dt=record.dt, msg=SYNC_LOG_TEMPLATE_MAP[step, record.success].format(**record.detail)
                    )
                )
            result.append(report)
        return result


class IDGenerator:
    # TODO: 使用 redis 实现这个自增主键, 以保证后台任务并发的安全性.
    def __init__(self, manager: SyncModelManager):
        self.manager = manager
        self.latest_auto_id = self.manager.get_latest_auto_id()
        self._lock = RLock()

    def __iter__(self):
        return self

    def __next__(self):
        with self._lock:
            self.latest_auto_id += 1
            return self.latest_auto_id


class DBSyncManager:
    """Data DB Sync Manager

    主要的目的是将批量的操作聚合，将 IO 操作集中

    几点好处：
    - 提速，bulk_update & bulk_create 速度更快
    - 事务亲和，IO 操作集中

    可能引入的风险：
    - 内存爆炸，TODO: 需要更新细致的内存使用测试
    """

    _default_meta_map: Dict[str, Type[SyncModelMeta]] = {
        "department": DepartmentMeta,
        "profile": ProfileMeta,
        "department_profile_relation": DepartmentProfileMeta,
        "profile_leader_relation": LeaderProfileMeta,
    }

    def __init__(self, meta_map: dict = None):
        self.update_model_meta(meta_map or {})

    def __getitem__(self, item):
        return self._sets[item]

    def register_id(self, type_: Type[SyncModelMeta]):
        """注册自增ID"""
        return next(self.id_generators[type_.target_model])

    def sync_type(self, target_type: Type[Model]):
        """针对某种类型同步"""
        self._sets[target_type].sync_to_db()

    def sync_all(self):
        # 这里使用列表遍历，保证顺序
        for x in self.meta_map.values():
            self._sets[x.target_model].sync_to_db()

    def detect_model_manager(self, model_type: Type[Model]) -> SyncModelManager:
        """根据传递的 Model 类型获取对应的 SyncModelManager"""
        for type_ in list(self.meta_map.values()):
            if issubclass(model_type, type_.target_model):
                return self._sets[model_type]
        supported_types = [type_.target_model for type_ in self.meta_map.values()]
        raise ValueError(f"Unsupported Type<{model_type}>, item should be within types: {supported_types}")

    def magic_add(self, item: Model, operation: SyncOperation = None):
        """动态探测增加的对象类型"""
        manager = self.detect_model_manager(type(item))
        logger.debug("adding item<%s> of type<%s>", item, type(item))
        manager.add(item, operation)

    def magic_exists(self, item: Model) -> bool:
        """动态探测是否存在"""
        manager = self.detect_model_manager(type(item))
        return manager.exists(item)

    def magic_get(self, unique_key: Any, target_meta: Type[SyncModelMeta]):
        """动态探测获取已经添加的元素"""
        manager = self.detect_model_manager(target_meta.target_model)
        return manager.get(unique_key)

    def update_model_meta(self, update_meta_info: Dict[str, Type[SyncModelMeta]]):
        for key in update_meta_info.keys():
            if key not in self._default_meta_map:
                raise ValueError(f"model set key unknown, available choices: [{self._default_meta_map.keys()}]")

        update_map = self._default_meta_map.copy()
        update_map.update(update_meta_info)
        self._update_cache(meta_map=update_map)

    def _update_cache(self, meta_map: dict = None):
        self.meta_map = meta_map or self._default_meta_map
        self._sets = {x.target_model: SyncModelManager(meta=x) for x in list(self.meta_map.values())}

        self.id_generators = {manager.meta.target_model: IDGenerator(manager) for manager in self._sets.values()}


@dataclass
class Fetcher:
    """从远端拉取数据"""

    # 目录 ID
    category_id: int
    # 目录配置
    config_loader: Optional[ConfigProvider] = None

    def fetch(self, *args, **kwargs):
        raise NotImplementedError


@dataclass
class Syncer:
    """将序列化数据同步到数据库"""

    # 目录信息
    category_id: int
    # 数据拉取管理器
    fetcher_cls: ClassVar[Type[Fetcher]]

    # 默认的同步周期
    default_sync_period: Optional[int] = None
    # 最小的同步周期
    min_sync_period: Optional[int] = None

    context: SyncContext = field(default_factory=SyncContext)

    # 决定是否初始化client, 默认为True, 即默认会初始化; 某些场景不需要初始化(例如test_connection), 需要设置为False
    with_initialize_client: bool = True

    def __post_init__(self):
        try:
            self.category = ProfileCategory.objects.get(pk=self.category_id)
        except Exception:
            raise ValueError("category<%s> does not exist" % self.category_id)

        self.db_sync_manager = DBSyncManager()
        self.config_loader = ConfigProvider(category_id=self.category_id)

    def sync(self, *args, **kwargs):
        """将数据同步到 DB 中"""
        raise NotImplementedError

    def get_fetcher(self):
        return self.fetcher_cls(self.category_id, self.config_loader, self.with_initialize_client)

    def disable_departments_before_sync(self, exempt_ids: list = None):
        """全同步前禁用该目录下的组织
        !!! 仅限事务中调用，不然会有数据中断风险 !!!
        """
        exempt_ids = exempt_ids or []
        logger.info(
            "Going to mark departments in category<%s> as deleted, skipping %s",
            self.category_id,
            self.config_loader.get("exempt_sync_department_ids"),
        )
        Department.objects.filter(category_id=self.category_id).exclude(id__in=exempt_ids).update(enabled=False)

    def disable_profiles_before_sync(self, exempt_ids: list = None):
        """
        全同步前禁用该目录下的人员 & 删除人员与组织的关系
        !!! 仅限事务中调用，不然会有数据中断风险 !!!
        """
        exempt_ids = exempt_ids or []
        # 反向找出需要禁用的人员
        disabling_profiles = list(
            Profile.objects.filter(category_id=self.category_id)
            .exclude(id__in=exempt_ids)
            .values_list("id", flat=True)
        )

        logger.info(
            "Going to mark profiles(and relations)(all: %s) in category<%s> as deleted, skipping %s profiles",
            len(disabling_profiles),
            self.category_id,
            len(exempt_ids),
        )
        # 清除与部门之间的关联关系
        DepartmentThroughModel.objects.filter(profile_id__in=disabling_profiles).delete()
        # 清除人员上级关系
        LeaderThroughModel.objects.filter(from_profile_id__in=disabling_profiles).delete()
        # 禁用人员
        Profile.objects.filter(id__in=disabling_profiles).update(enabled=False)

    def try_to_add_profile_department_relation(self, profile: Profile, department: Department):
        relation_params = {"profile": profile, "department": department}
        # 存在豁免目录中有用户自定义添加的既存关系，需要强制判断
        exempt_department_ids = self.config_loader.get("exempt_sync_department_ids")
        if (
            exempt_department_ids
            and DepartmentThroughModel.objects.filter(
                profile=profile, department_id__in=exempt_department_ids
            ).exists()
        ):
            logger.info(
                "profile<%s> is in the exempted department<%s>, skip",
                profile,
                department,
            )
            return

        if DepartmentThroughModel.objects.filter(**relation_params).exists():
            logger.debug("profile<%s> already in department<%s>, skip", profile, department)
            return

        logger.info("trying to add profile<%s> to department<%s>", profile, department)
        relation = DepartmentThroughModel(**relation_params)
        self.db_sync_manager.magic_add(relation)


class LoginHandler:
    """登录校验处理类"""

    @abstractmethod
    def check(self, *args, **kwargs):
        raise NotImplementedError


class TypeProtocol(Protocol):
    @property
    def key_field(self) -> str:
        """The Key Field to make obj unique."""

    @property
    def display_str(self) -> str:
        """The Display str for obj."""


M = TypeVar("M")


class TypeList(UserDict, MutableMapping[str, M]):
    @classmethod
    def from_list(cls, items: List[TypeProtocol]):
        items_map = {i.key_field: i for i in items}
        return cls(items_map)

    @classmethod
    def get_type(cls) -> Type[M]:
        # As of Python 3.6. there is a public __args__ and (__parameters__) field for Generic
        return cls.__args__[0]  # type: ignore


class DBSyncHelper(Protocol):
    """将 TypeList 塞入到 DBSyncManager 中的协议"""

    category: ProfileCategory
    db_sync_manager: DBSyncManager
    target_obj_list: TypeList
    context: SyncContext

    def load_to_memory(self):
        """将数据对象加载到内存"""
        raise NotImplementedError

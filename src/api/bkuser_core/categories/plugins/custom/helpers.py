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
import hashlib
import logging
from dataclasses import dataclass
from typing import Dict, Optional, Type, Union

from django.db.models import Model
from django.utils.encoding import force_bytes
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.plugins.base import DBSyncManager, SyncContext, SyncStep
from bkuser_core.categories.plugins.custom.exceptions import NoKeyItemAvailable
from bkuser_core.categories.plugins.custom.metas import CustomDepartmentMeta, CustomProfileMeta
from bkuser_core.categories.plugins.custom.models import CustomDepartment, CustomProfile, CustomTypeList
from bkuser_core.categories.plugins.custom.utils import handle_with_progress_info
from bkuser_core.common.db_sync import SyncOperation
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.models import LeaderThroughModel, Profile
from bkuser_core.profiles.validators import validate_username

logger = logging.getLogger(__name__)


@dataclass
class DBSyncHelper:
    """将 CustomType 塞入到 DBSyncManager 中"""

    category: ProfileCategory
    db_sync_manager: DBSyncManager
    target_obj_list: CustomTypeList
    context: SyncContext

    def load_to_memory(self):
        """将数据对象加载到内存"""
        raise NotImplementedError

    def _get_code(self, raw_key: Union[str, int]) -> str:
        # 添加 category_id ，code 可以在多目录中唯一
        code = f"{self.category.pk}-{str(raw_key)}"
        sha = hashlib.sha256(force_bytes(code)).hexdigest()
        logger.info("transform code to sha: %s -> %s", code, sha)
        return sha


class DepSyncHelper(DBSyncHelper):
    _MPTT_INIT_PARAMS = {
        "tree_id": 0,
        "lft": 0,
        "rght": 0,
        "level": 0,
    }

    @cached_property
    def db_departments(self) -> Dict[str, Department]:
        # 由于 bulk_update 需要从数据库查询完整的 Department 信息, 为提高查询效率, 统一执行查询操作, 减轻数据库负担
        return {dep.code: dep for dep in Department.objects.filter(category_id=self.category.pk)}

    def load_to_memory(self):
        for dept in handle_with_progress_info(self.target_obj_list, progress_title="handle department"):
            self._handle_department(dept.code)

    def _handle_department(self, dept_code) -> Optional[Department]:
        """将 CustomDepartment 转换成 Department, 并递归处理其父节点

        从内存对象(CustomDepartment)列表中, 根据父节点的 code 查找父节点, 如果对象不存在则返回 None
        如果父节点存在, 则递归处理父节点, 并绑定部门上下级关系, 再将部门对象(Department)插入缓存层
        如果父节点不存在, 则直接将部门对象(Department)插入缓存层

        :raise ValueError: 如果父节点不存在, 则抛出 ValueError, **事务回滚**
        """
        try:
            dept_info = self.target_obj_list.get(dept_code)
        except (ValueError, NoKeyItemAvailable):
            return None

        parent_id = None
        # 如果父节点本身有父节点, 那么先处理父节点
        if dept_info.parent:
            # 递归处理父节点
            parent_dept = self._handle_department(dept_info.parent)
            if parent_dept is None:
                self.context.add_record(
                    step=SyncStep.DEPARTMENTS,
                    success=False,
                    department=dept_info.name,
                    error=_("父组织【{department}】不存在").format(department=dept_info.parent),
                )
                raise ValueError(
                    f"the given parent<{dept_info.parent}> of department<{dept_code}:{dept_info.name}> not found"
                )
            parent_id = parent_dept.pk

        code = self._get_code(dept_code)
        dept = self.insert_dept(
            code=code,
            update_params={
                "category_id": self.category.pk,
                "code": code,
                "name": dept_info.name,
                "enabled": True,
                "extras": {"code": dept_code},
                "parent_id": parent_id,
                **self._MPTT_INIT_PARAMS,
            },
        )
        return dept

    def insert_dept(self, code: str, update_params: dict) -> Department:
        """插入部门到 DBSyncManager"""
        dept = self.db_sync_manager.magic_get(unique_key=code, target_meta=CustomDepartmentMeta)
        # 部门信息已经加载到内存中, 不再重新更新
        if dept:
            return dept

        if code in self.db_departments:
            dept = self.db_departments[code]
            for key, value in update_params.items():
                setattr(dept, key, value)
            self.db_sync_manager.magic_add(dept, SyncOperation.UPDATE.value)
        else:
            update_params["pk"] = self.db_sync_manager.register_id(CustomDepartmentMeta)
            dept = Department(**update_params)
            self.db_sync_manager.magic_add(dept, SyncOperation.ADD.value)

        self.context.add_record(step=SyncStep.DEPARTMENTS, success=True, department=dept.name)
        return dept


class ProSyncHelper(DBSyncHelper):
    @cached_property
    def db_profiles(self) -> Dict[str, Profile]:
        # 由于 bulk_update 需要从数据库查询完整的 Profile 信息, 为提高查询效率, 统一执行查询操作, 减轻数据库负担
        return {profile.username: profile for profile in Profile.objects.filter(category_id=self.category.pk)}

    @cached_property
    def db_departments(self) -> Dict[str, Department]:
        # 由于 bulk_update 需要从数据库查询完整的 Department 信息, 为提高查询效率, 统一执行查询操作, 减轻数据库负担
        return {dep.code: dep for dep in Department.objects.filter(category_id=self.category.pk, enabled=True)}

    def _load_base_info(self):
        for info in handle_with_progress_info(self.target_obj_list, progress_title="handle profile"):
            try:
                validate_username(value=info.username)
            except ValidationError as e:
                self.context.add_record(step=SyncStep.USERS, success=False, username=info.username, error=str(e))
                logger.warning("username<%s:%s> does not meet format, will skip", info.code, info.username)
                continue

            # 1. 先更新 profile 本身
            code = self._get_code(info.code)
            extras = {"code": info.code}
            if info.extras:
                # note: the priority of extras from origin api is higher than `code=info.code`
                extras.update(info.extras)

            profile_params = {
                "category_id": self.category.pk,
                "domain": self.category.domain,
                "enabled": True,
                "username": info.username,
                "display_name": info.display_name,
                "email": info.email,
                "code": code,
                "telephone": info.telephone,
                "position": info.position,
                "extras": extras,
                "status": ProfileStatus.NORMAL.value,
            }

            # 2. 更新或创建 Profile 对象
            if info.username in self.db_profiles:
                profile = self.db_profiles[info.username]
                for key, value in profile_params.items():
                    setattr(profile, key, value)
                self.db_sync_manager.magic_add(profile, SyncOperation.UPDATE.value)
            else:
                profile = Profile(**profile_params)
                if self.db_sync_manager.magic_exists(profile):
                    # 如果增加用户的行为已经添加过了, 则使用内存中的 Profile
                    logger.debug(
                        "profile<%s> already add into db sync manager, only get",
                        profile,
                    )
                    profile = self.db_sync_manager.magic_get(code, CustomProfileMeta)
                else:
                    profile.id = self.db_sync_manager.register_id(CustomProfileMeta)
                    self.db_sync_manager.magic_add(profile, SyncOperation.ADD.value)

            # 3. 维护关联关系
            for dep_id in info.departments:
                department = self.db_departments.get(self._get_code(dep_id), None)
                if not department:
                    self.context.add_record(
                        step=SyncStep.DEPT_USER_RELATIONSHIP,
                        success=False,
                        username=info.username,
                        department=dep_id,
                        error=_("部门不存在"),
                    )
                    logger.warning(
                        "the department<%s> of profile<%s:%s> is missing, will skip", dep_id, info.code, info.username
                    )
                    continue

                self.try_add_relation(
                    params={"profile_id": profile.pk, "department_id": department.pk},
                    target_model=DepartmentThroughModel,
                )
                self.context.add_record(
                    step=SyncStep.DEPT_USER_RELATIONSHIP,
                    success=True,
                    username=info.username,
                    department=department.name,
                )
            self.context.add_record(step=SyncStep.USERS, success=True, username=info.username)

    def _load_leader_info(self):
        for info in handle_with_progress_info(self.target_obj_list, progress_title="handle profile leaders"):
            profile = self.db_sync_manager.magic_get(self._get_code(info.code), CustomProfileMeta)
            if not profile:
                self.context.add_record(
                    step=SyncStep.USERS_RELATIONSHIP, success=False, username=info.username, error=_("用户信息不存在")
                )
                logger.warning(
                    "profile<%s:%s> not exists, the profile leaders will not be synced, will skip",
                    info.code,
                    info.username,
                )
                continue

            for leader_id in info.leaders:
                if leader_id == profile.code:
                    self.context.add_record(
                        step=SyncStep.USERS_RELATIONSHIP, success=False, username=info.username, error=_("无法设置自己为上级")
                    )
                    logger.warning("profile<%s:%s> can not regard self as leader, will skip", info.code, info.username)
                    continue

                leader = self.db_sync_manager.magic_get(self._get_code(leader_id), CustomProfileMeta)
                if not leader:
                    self.context.add_record(
                        step=SyncStep.USERS_RELATIONSHIP,
                        success=False,
                        username=info.username,
                        error=_("上级【{username}】不存在").format(username=leader_id),
                    )
                    logger.warning(
                        "the leader<%s> of profile<%s:%s> is missing, will skip", leader_id, info.code, info.username
                    )
                    continue

                self.try_add_relation(
                    params={"from_profile_id": profile.pk, "to_profile_id": leader.pk},
                    target_model=LeaderThroughModel,
                )
                self.context.add_record(
                    step=SyncStep.USERS_RELATIONSHIP, success=True, username=info.username, leader=leader.username
                )

    def load_to_memory(self):
        self._load_base_info()
        self._load_leader_info()

    def try_add_relation(self, params: dict, target_model: Type[Model]):
        """增加关联关系"""
        logger.debug("trying to add relation: %s", params)
        relation = target_model(**params)
        self.db_sync_manager.magic_add(relation)


def init_helper(
    items: CustomTypeList, category: ProfileCategory, db_sync_manager: DBSyncManager, context: SyncContext
) -> DBSyncHelper:
    """加载对应的 Helper"""
    _map = {CustomProfile: ProSyncHelper, CustomDepartment: DepSyncHelper}
    return _map[items.custom_type](
        category=category, db_sync_manager=db_sync_manager, target_obj_list=items, context=context
    )

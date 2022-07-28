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
from dataclasses import dataclass
from typing import Optional

from django.db import transaction

from bkuser_core.categories.plugins.base import Syncer, SyncStep
from bkuser_core.categories.plugins.custom.client import CustomDataClient, CustomTypeList
from bkuser_core.categories.plugins.custom.helpers import init_helper
from bkuser_core.categories.plugins.custom.metas import CustomDepartmentMeta, CustomProfileMeta
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.profiles.models import LeaderThroughModel, Profile

logger = logging.getLogger(__name__)


@dataclass
class CustomSyncer(Syncer):
    """定义了拉取协议，按照协议拉取人员"""

    client: Optional[CustomDataClient] = None

    def __post_init__(self):
        super().__post_init__()

        self.db_sync_manager.update_model_meta({"department": CustomDepartmentMeta, "profile": CustomProfileMeta})
        self.client = CustomDataClient(
            api_host=self.config_loader.get("api_host"),
            paths=self.config_loader.get("paths"),
            category_id=self.category_id,
        )

    def sync(self, *args, **kwargs):
        """获取远程数据并存储"""
        with transaction.atomic():
            self._sync_department()
            self._sync_profile()

    def _sync_department(self):
        # 先尝试去获取远端数据，所有的在内存中处理完毕后，再尝试往 DB 中写
        self._load2sync_manager(self.client.fetch_departments())
        with Department.tree_objects.disable_mptt_updates(), self.context([SyncStep.DEPARTMENTS]):
            # 禁用所有 Department, 在同步时会重新激活仍然有效的 Department
            self.disable_departments_before_sync()
            self.db_sync_manager.sync_type(target_type=Department)

            # 由于使用 bulk_update 无法第一时间更新树信息，所以在保存完之后强制确保树信息全部正确
            logger.info("make sure tree sane...")
            # 由于插入时并没有更新 tree_id，所以这里需要全量更新
            Department.tree_objects.rebuild()

    def _sync_profile(self):
        self._load2sync_manager(self.client.fetch_profiles())
        with self.context([SyncStep.USERS, SyncStep.DEPT_USER_RELATIONSHIP, SyncStep.USERS_RELATIONSHIP]):
            # 禁用所有 Profiles, 在同步时会重新激活仍然有效的 Profiles
            self.disable_profiles_before_sync()

            self.db_sync_manager.sync_type(target_type=Profile)
            self.db_sync_manager.sync_type(target_type=DepartmentThroughModel)
            self.db_sync_manager.sync_type(target_type=LeaderThroughModel)

    def _load2sync_manager(self, items: CustomTypeList):
        """将远程数组加载到操作集"""
        helper = init_helper(
            category=self.category, db_sync_manager=self.db_sync_manager, items=items, context=self.context
        )
        return helper.load_to_memory()

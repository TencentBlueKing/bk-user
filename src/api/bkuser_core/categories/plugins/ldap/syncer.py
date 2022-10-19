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
import re
from dataclasses import dataclass
from itertools import chain, product
from typing import List, Optional, Tuple

from django.db import transaction
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _

from bkuser_core.categories.exceptions import FetchDataFromRemoteFailed
from bkuser_core.categories.plugins.base import DBSyncManager, Fetcher, SyncContext, Syncer, SyncStep, TypeList
from bkuser_core.categories.plugins.ldap.adaptor import ProfileFieldMapper, department_adapter, user_adapter
from bkuser_core.categories.plugins.ldap.client import LDAPClient
from bkuser_core.categories.plugins.ldap.helper import DepartmentSyncHelper, ProfileSyncHelper
from bkuser_core.categories.plugins.ldap.metas import LdapDepartmentMeta, LdapProfileMeta
from bkuser_core.categories.plugins.ldap.models import LdapDepartment, LdapUserProfile
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.profiles.models import LeaderThroughModel, Profile

logger = logging.getLogger(__name__)


@dataclass
class LDAPFetcher(Fetcher):
    """从 LDAP 拉取所需数据"""

    DN_REGEX = re.compile("(?P<key>[ \\w-]+)=(?P<value>[ \\w-]+)")

    # 决定是否初始化client, 默认为True, 即默认会初始化; 某些场景不需要初始化(例如test_connection), 需要设置为False
    with_initialize_client: bool = True

    def __post_init__(self):
        self.client = LDAPClient(self.config_loader, self.with_initialize_client)
        self.field_mapper = ProfileFieldMapper(config_loader=self.config_loader)
        self._data: Tuple[List, List, List] = None

    def fetch(self):
        """fetch data from remote ldap server"""
        return self._fetch_data(
            basic_pull_node=self.config_loader["basic_pull_node"],
            user_filter=self.config_loader["user_filter"],
            organization_class=self.config_loader["organization_class"],
            user_group_filter=self.config_loader.get("user_group_filter"),
            attributes=self.field_mapper.get_user_attributes(),
        )

    def test_fetch_data(self, configs: dict):
        """测试获取数据"""
        return self._fetch_data(
            basic_pull_node=configs["basic_pull_node"],
            user_filter=configs["user_filter"],
            organization_class=configs["organization_class"],
            user_group_filter=configs.get("user_group_filter"),
        )

    def _fetch_data(
        self,
        basic_pull_node,
        user_filter,
        organization_class,
        user_group_filter,
        attributes: Optional[List] = None,
    ) -> tuple:
        try:
            if user_group_filter:
                groups = self.client.search(start_root=basic_pull_node, force_filter_str=user_group_filter)
            else:
                groups = []
        except Exception as e:
            logger.exception(
                "failed to get groups from remote server. basic_pull_node: %s, user_group_filter: %s",
                basic_pull_node,
                user_group_filter,
            )
            error_detail = f" ({type(e).__module__}.{type(e).__name__}: {str(e)})"
            raise FetchDataFromRemoteFailed(_("无法获取用户组，请检查配置") + error_detail)

        try:
            departments = self.client.search(start_root=basic_pull_node, object_class=organization_class)
        except Exception as e:
            logger.exception(
                "failed to get departments from remote server. basic_pull_node: %s, organization_class: %s",
                basic_pull_node,
                organization_class,
            )
            error_detail = f" ({type(e).__module__}.{type(e).__name__}: {str(e)})"
            raise FetchDataFromRemoteFailed(_("无法获取组织部门，请检查配置") + error_detail)

        try:
            users = self.client.search(
                start_root=basic_pull_node,
                force_filter_str=user_filter,
                attributes=attributes or [],
            )
        except Exception as e:
            logger.exception(
                "failed to get users from remote server. basic_pull_node: %s, user_filter: %s, attributes: %s",
                basic_pull_node,
                user_filter,
                attributes,
            )
            error_detail = f" ({type(e).__module__}.{type(e).__name__}: {str(e)})"
            raise FetchDataFromRemoteFailed(_("无法获取用户数据, 请检查配置") + error_detail)

        return groups, departments, users

    def _get_code(self, raw_obj: dict) -> str:
        """通过对象 dn 生成 唯一code"""
        dn = f"{self.category_id}-{raw_obj.get('dn')}"
        sha = hashlib.sha256(force_bytes(dn)).hexdigest()
        logger.info("use dn to be code: %s -> %s", dn, sha)
        return sha

    def _load(self):
        # TODO: 将 Fetcher 拆成两个对象, 或者不再遵循原来的 Fetcher 协议
        if self._data is None:
            self._data = self.fetch()
        return self._data

    def fetch_profiles(self, restrict_types: List[str]):
        """获取 profile 对象列表"""
        _, _, users = self._load()
        profiles = []
        for user in users:
            if not user.get("dn"):
                logger.warning("no dn field, skipping for profile: %s", user)
                continue

            profiles.append(
                user_adapter(
                    code=self._get_code(user),
                    user_meta=user,
                    field_mapper=self.field_mapper,
                    restrict_types=restrict_types,
                )
            )
        return profiles

    def fetch_departments(self, restrict_types: List[str]):
        """获取 department 对象列表"""
        groups, departments, _ = self._load()
        results = []
        for is_group, dept_meta in chain.from_iterable(iter([product([False], departments), product([True], groups)])):
            if not dept_meta.get("dn"):
                logger.warning("no dn field, skipping for %s:%s", ("group" if is_group else "department"), dept_meta)
                continue
            results.append(
                department_adapter(
                    code=self._get_code(dept_meta),
                    dept_meta=dept_meta,
                    is_group=is_group,
                    restrict_types=restrict_types,
                )
            )
        return results


@dataclass
class LDAPSyncer(Syncer):
    OU_KEY = "ou"
    CN_KEY = "cn"

    fetcher_cls = LDAPFetcher

    def __post_init__(self):
        super().__post_init__()

        self.fetcher: LDAPFetcher = self.get_fetcher()
        self._field_mapper = self.fetcher.field_mapper
        self.db_sync_manager = DBSyncManager({"department": LdapDepartmentMeta, "profile": LdapProfileMeta})
        self.context = SyncContext()

    def sync(self):
        with transaction.atomic():
            self._sync_department()

        # FIX BUG: you can`t execute queries until the end of the 'atomic' block
        # move rebuild to single atomic
        with transaction.atomic():
            # 由于使用 bulk_update 无法第一时间更新树信息，所以在保存完之后强制确保树信息全部正确
            logger.info("make sure tree sane...")
            # 由于插入时并没有更新 tree_id，所以这里需要全量更新
            Department.tree_objects.rebuild()

        with transaction.atomic():
            self._sync_profile()

    def _sync_department(self):
        DepartmentSyncHelper(
            category=self.category,
            db_sync_manager=self.db_sync_manager,
            target_obj_list=(TypeList[LdapDepartment]).from_list(
                self.fetcher.fetch_departments([self.OU_KEY, self.CN_KEY])
            ),
            context=self.context,
            config_loader=self.config_loader,
        ).load_to_memory()

        with Department.tree_objects.disable_mptt_updates(), self.context([SyncStep.DEPARTMENTS]):
            # 禁用所有 Department, 在同步时会重新激活仍然有效的 Department
            self.disable_departments_before_sync()
            self.db_sync_manager.sync_type(target_type=Department)

    def _sync_profile(self):
        ProfileSyncHelper(
            category=self.category,
            db_sync_manager=self.db_sync_manager,
            target_obj_list=(TypeList[LdapUserProfile]).from_list(
                self.fetcher.fetch_profiles([self.OU_KEY, self.CN_KEY])
            ),
            context=self.context,
        ).load_to_memory()

        with self.context([SyncStep.USERS, SyncStep.DEPT_USER_RELATIONSHIP, SyncStep.USERS_RELATIONSHIP]):
            # 禁用所有 Profiles, 在同步时会重新激活仍然有效的 Profiles
            self.disable_profiles_before_sync()

            self.db_sync_manager.sync_type(target_type=Profile)
            self.db_sync_manager.sync_type(target_type=DepartmentThroughModel)
            self.db_sync_manager.sync_type(target_type=LeaderThroughModel)

            logger.info("all profiles & relations synced.")

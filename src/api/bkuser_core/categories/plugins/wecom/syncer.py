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
from bkuser_core.categories.exceptions import FetchDataFromRemoteFailed
from bkuser_core.categories.plugins.base import Fetcher, ProfileMeta, Syncer
from bkuser_core.categories.plugins.wecom.client import WeComClient
from bkuser_core.categories.plugins.wecom.constants import WeComStatus, WeComEnabled
from bkuser_core.common.db_sync import SyncOperation
from bkuser_core.common.progress import progress
from bkuser_core.departments.models import Department, Profile
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.validators import validate_username
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)



@dataclass
class WeComFetcher(Fetcher):
    """从 WeCom 拉取数据"""

    def __post_init__(self):
        self.client = WeComClient(self.config_loader)

    def fetch(self):
        """fetch data from remote WeCom API"""
        return self._fetch_data()

    def test_fetch_data(self, configs: dict):
        """测试获取数据"""
        self._fetch_data()
        return

    def _fetch_data(self) -> tuple:
        try:
            departments = self.client.get_departments()
        except Exception:
            logger.exception("failed to get get_departments from WeCom API")
            raise FetchDataFromRemoteFailed("无法获取用户组，请检查配置")
        try:
            users = self.client.get_user_info(departments=departments)
        except Exception:
            logger.exception("failed to get users from WeCom API")
            raise FetchDataFromRemoteFailed("无法获取用户数据, 请检查配置")

        return departments, users


@dataclass
class WeComSyncer(Syncer):
    fetcher_cls = WeComFetcher

    def __post_init__(self):
        super().__post_init__()

        self.fetcher: WeComFetcher = self.get_fetcher()
        self.department_localid = {}

    def sync(self):
        departments, users = self.fetcher.fetch()
        with transaction.atomic():
            self.disable_departments_before_sync()
            self._sync_departments(departments)
            logger.info("all departments synced.")

        with transaction.atomic():
            self.disable_profiles_before_sync()
            self._sync_users(users, departments)
            self.db_sync_manager.sync_all()
            logger.info("all profiles & relations synced.")

    def _sync_departments(self, raw_departments: list):
        """同步部门信息"""
        logger.debug("going to sync raw departments: %s", raw_departments)
        # 父节点的parentid为0，根据parentid创建即可
        sorted(raw_departments, key=lambda k: k['parentid'])
        _total = len(raw_departments)
        parent_department = None
        wecom_parent_id = 0
        deparment_local_id = {}
        for index, raw_department in enumerate(raw_departments):
            try:
                if wecom_parent_id != raw_department['parentid']:
                    parent_department = deparment_local_id.get(raw_department['parentid'])
                    wecom_parent_id = raw_department['parentid']

                (new_parent_department, created) = Department.objects.update_or_create(
                    name=raw_department['name'],
                    parent=parent_department,
                    category_id=self.category_id,
                    defaults={"enabled": True}
                )
                if created:
                    logger.info("created department {}".format(raw_department['name']))
                deparment_local_id.update({raw_department['id']: new_parent_department})

            except Exception as e:
                logger.error("create department error={}".format(e))
                pass
            progress(
                index,
                _total,
                f"adding department {raw_department['name']} ({index}/{_total})"
            )
        self.department_localid = deparment_local_id

    def _sync_users(self, raw_users, raw_departments):
        _total = len(raw_users)

        def get_target_departments(category_id: int, department_ids: int, row_departments: list) -> Department:
            departments = [x for x in row_departments if x['id'] in department_ids]
            target_departments = set()
            for department in departments:
                try:
                    if department['parentid'] == 0:
                        target_department = Department.objects.filter(category_id=category_id).get(
                            name=department['name'])
                    else:
                        target_department = Department.objects.filter(category_id=category_id).get(
                            name=department['name'], parent_id=self.department_localid.get(department['parentid'])
                        )
                    target_departments.add(target_department)
                except ObjectDoesNotExist:
                    logger.warning(
                        "cannot find target department<%s>, parent dep<%s>",
                        department['name'],
                        target_departments,
                    )
                except Exception:
                    logger.warning(
                        "cannot find target department<%s>, parent dep<%s>, break, please check",
                        department['name'],
                        target_department,
                    )

            return target_departments

        for index, user in enumerate(raw_users):
            username = user.get("userid")
            # 这里只同步已激活的用户
            # status 激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。
            if user.get("status", 0) != WeComStatus.ACTIVE and user.get("enable", 0) != WeComEnabled.ENABLE:
                continue
            try:
                validate_username(value=username)
            except ValidationError:
                logger.warning("username<%s> does not meet format", username)
                continue
            progress(
                index,
                _total,
                f"adding profile<{username}> ({index}/{_total})",
            )
            # todo 上下级关系还没有处理
            # 1. 先更新 profile 本身
            profile_params = {
                "username": username,
                "code": username,
                "display_name": user.get('name'),
                "email": user.get('email'),
                "telephone": user.get('mobile'),
                "enabled": True,
                "category_id": self.category_id,
                "domain": self.category.domain,
                "status": ProfileStatus.NORMAL.value,
                "logo": user.get("thumb_avatar"),
                "wx_userid": username
            }

            try:
                profile = Profile.objects.get(category_id=self.category_id, username=username)
                for key, value in profile_params.items():
                    setattr(profile, key, value)
                self.db_sync_manager.magic_add(profile, SyncOperation.UPDATE.value)
            except ObjectDoesNotExist:
                profile = Profile(**profile_params)
                profile.id = self.db_sync_manager.register_id(ProfileMeta)
                self.db_sync_manager.magic_add(profile)

            # 2. 更新 department 关系
            target_departments = get_target_departments(self.category_id, user.get('department'), raw_departments)

            for d in target_departments:
                self.try_to_add_profile_department_relation(profile=profile, department=d)

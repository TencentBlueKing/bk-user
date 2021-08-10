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
from typing import Callable, List, Optional

from bkuser_core.categories.exceptions import FetchDataFromRemoteFailed
from bkuser_core.categories.plugins.base import Fetcher, ProfileMeta, Syncer
from bkuser_core.categories.plugins.ldap.client import LDAPClient
from bkuser_core.common.db_sync import SyncOperation
from bkuser_core.common.progress import progress
from bkuser_core.departments.models import Department, Profile
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.validators import validate_username
from bkuser_core.user_settings.loader import ConfigProvider
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import transaction
from django.utils.encoding import force_bytes, force_str
from ldap3.utils import dn as dn_utils
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

SETTING_FIELD_MAP = {
    "username": "username",
    "display_name": "display_name",
    "email": "email",
    "telephone": "telephone",
    "user_member_of": "user_member_of",
}


@dataclass
class LDAPFetcher(Fetcher):
    """从 LDAP 拉取所需数据"""

    DN_REGEX = re.compile("(?P<key>[ \\w-]+)=(?P<value>[ \\w-]+)")

    def __post_init__(self):
        self.client = LDAPClient(self.config_loader)
        self.field_mapper = ProfileFieldMapper(config_loader=self.config_loader, setting_field_map=SETTING_FIELD_MAP)

    def fetch(self):
        """fetch data from remote ldap server"""
        return self._fetch_data(
            basic_pull_node=self.config_loader["basic_pull_node"],
            user_filter=self.config_loader["user_filter"],
            organization_class=self.config_loader["organization_class"],
            user_group_filter=self.config_loader["user_group_filter"],
            attributes=self.field_mapper.get_user_attributes(),
        )

    def test_fetch_data(self, configs: dict):
        """测试获取数据"""
        self._fetch_data(
            basic_pull_node=configs["basic_pull_node"],
            user_filter=configs["user_filter"],
            organization_class=configs["organization_class"],
            user_group_filter=configs["user_group_filter"],
        )
        return

    def _fetch_data(
        self,
        basic_pull_node,
        user_filter,
        organization_class,
        user_group_filter,
        attributes: Optional[List] = None,
    ) -> tuple:
        try:
            groups = self.client.search(start_root=basic_pull_node, force_filter_str=user_group_filter)
        except Exception:
            logger.exception("failed to get groups from remote server")
            raise FetchDataFromRemoteFailed("无法获取用户组，请检查配置")

        try:
            departments = self.client.search(start_root=basic_pull_node, object_class=organization_class)
        except Exception:
            logger.exception("failed to get departments from remote server")
            raise FetchDataFromRemoteFailed("无法获取组织部门，请检查配置")

        try:
            users = self.client.search(
                start_root=basic_pull_node,
                force_filter_str=user_filter,
                attributes=attributes or [],
            )
        except Exception:
            logger.exception("failed to get users from remote server")
            raise FetchDataFromRemoteFailed("无法获取用户数据, 请检查配置")

        return groups, departments, users


@dataclass
class LDAPSyncer(Syncer):
    OU_KEY = "ou"
    CN_KEY = "cn"

    fetcher_cls = LDAPFetcher

    def __post_init__(self):
        super().__post_init__()

        self.fetcher: LDAPFetcher = self.get_fetcher()
        self._field_mapper = self.fetcher.field_mapper

    def sync(self):
        groups, departments, users = self.fetcher.fetch()
        with transaction.atomic():
            self.disable_departments_before_sync()
            self._sync_departments(departments)
            self._sync_departments(groups, True)
            logger.info("all departments synced.")

        with transaction.atomic():
            self.disable_profiles_before_sync()
            self._sync_users(users)
            self.db_sync_manager.sync_all()
            logger.info("all profiles & relations synced.")

    def _sync_departments(self, raw_departments: list, is_user_group=False):
        """序列化部门"""
        logger.debug("going to sync raw departments: %s", raw_departments)

        _total = len(raw_departments)
        for index, raw_department in enumerate(raw_departments):
            if not raw_department.get("dn"):
                # 没有 dn 字段忽略
                logger.info("no dn field, skipping for %s", raw_department)
                continue

            dn = raw_department["dn"]
            tree = self._parse_tree(dn, [self.OU_KEY, self.CN_KEY])
            # 通过 dn 拿到目标组织和组织整条链路
            leaf, route = tree[0], tree[1:]

            leaf_name = list(leaf.values())[0]
            parent_department = None
            if route:
                logger.debug("%s has parents %s", leaf, route)
                # 从根开始逐级增加组织
                route.reverse()
                for dep in route:
                    # 暂时不需要区分 ou 或者 cn, parse tree 时已经限定了
                    dep_name = list(dep.values())[0]

                    # TODO: 使用 sync manager 批量同步?
                    try:
                        parent_department, _ = Department.objects.update_or_create(
                            name=dep_name,
                            parent=parent_department,
                            category_id=self.category_id,
                            defaults={"extras": self._make_department_extras(is_user_group), "enabled": True},
                        )
                    except MultipleObjectsReturned:
                        # 删除后创建的同名组织
                        departments = Department.objects.filter(name=dep_name, parent=parent_department).order_by(
                            "-create_time"
                        )
                        for department in departments[1:]:
                            department.hard_delete()

                        parent_department = departments[0]

            # 上级建立完毕之后，建立自己
            _, _ = Department.objects.update_or_create(
                name=leaf_name,
                code=self._get_code(raw_department),
                category_id=self.category_id,
                defaults={
                    "parent": parent_department,
                    "extras": self._make_department_extras(is_user_group),
                    "enabled": True,
                },
            )
            progress(
                index,
                _total,
                f"adding {'department' if not is_user_group else 'group'}"
                f"<{leaf_name}>, dn<{dn}> ({index}/{_total})",
            )

    def _sync_users(self, raw_users):
        _total = len(raw_users)
        for index, user in enumerate(raw_users):
            if not user.get("dn"):
                logger.info("no dn field, skipping for %s", user)
                continue

            # TODO: 使用 dataclass 优化 user 数据结构
            username = self._field_mapper.get_field(user_meta=user["raw_attributes"], field_name="username")
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

            # 1. 先更新 profile 本身
            profile_params = {
                "username": username,
                "code": self._get_code(user),
                "display_name": self._field_mapper.get_field(
                    user_meta=user["raw_attributes"], field_name="display_name"
                ),
                "email": self._field_mapper.get_field(user_meta=user["raw_attributes"], field_name="email"),
                "telephone": self._field_mapper.get_field(user_meta=user["raw_attributes"], field_name="telephone"),
                "enabled": True,
                "category_id": self.category_id,
                "domain": self.category.domain,
                "status": ProfileStatus.NORMAL.value,
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
            # 这里我们默认用户只能挂载在 用户组(cn) 和 组织(ou) 下
            def get_full_route(parse_method: Callable, parse_params: dict, raw_route: str) -> list:
                return parse_method(raw_route, **parse_params)

            def get_target_department(category_id: int, dep_route: list) -> Department:
                departments = [x for x in dep_route if list(x.keys())[0] in [self.OU_KEY, self.CN_KEY]]
                # 由于所有路径都是到根的，所以从根开始找寻
                departments.reverse()
                target_department = None
                for dep in departments:
                    dep_name = list(dep.values())[0]
                    try:
                        target_department = Department.objects.filter(category_id=category_id).get(
                            name=dep_name, parent_id=target_department
                        )
                    except ObjectDoesNotExist:
                        logger.warning(
                            "cannot find target department<%s>, parent dep<%s>",
                            dep_name,
                            target_department,
                        )
                    except Exception:  # pylint: disable=broad-except
                        logger.warning(
                            "cannot find target department<%s>, parent dep<%s>, break, please check",
                            dep_name,
                            target_department,
                        )

                return target_department

            # 同一个人员只能属于一个单位组织，但是可以属于多个用户组
            # 通常我们从 dn 里解析的，有两种可能：
            # 对于用户a: cn=a,ou=b,ou=c 或  cn=a,cn=b,cn=c, 前者表明了组织单位链路，后者说明用户只存在于某个用户组
            # 所以第一 cn=a 需要从整个链路中剔除
            full_ou = get_full_route(
                self._parse_tree,
                {"restrict_types": [self.OU_KEY, self.CN_KEY]},
                user["dn"],
            )[1:]
            full_groups = [
                get_full_route(self._parse_tree, {"restrict_types": [self.OU_KEY, self.CN_KEY]}, x)
                for x in user["attributes"][self.config_loader["user_member_of"]]
            ]

            binding_departments = set()
            target_ou = get_target_department(self.category_id, full_ou)
            if target_ou is not None:
                binding_departments.add(target_ou)

            # 原数据可能有多个用户组绑定关系
            for full_group in full_groups:
                d = get_target_department(self.category_id, full_group)
                if d is None:
                    logger.warning("can not find %s(group) from saved departments", full_group)
                    continue

                binding_departments.add(d)

            for d in binding_departments:
                self.try_to_add_profile_department_relation(profile=profile, department=d)

    @staticmethod
    def _parse_tree(dn, restrict_types: List[str] = None) -> List:
        """解析树路径"""
        restrict_types = restrict_types or []
        items = dn_utils.parse_dn(dn, escape=True)

        if restrict_types:
            parts = [{i[0]: i[1]} for i in items if i[0] in restrict_types]
        else:
            parts = [{i[0]: i[1]} for i in items]

        return parts

    def _make_department_extras(self, is_user_group):
        if is_user_group:
            return {"type": self.config_loader["user_group_class"]}
        else:
            return {"type": self.config_loader["organization_class"]}

    def _get_code(self, raw_obj: dict) -> str:
        """如果不存在 uuid 则用 dn(sha) 作为唯一标示"""
        entry_uuid = raw_obj.get("raw_attributes", {}).get("entryUUID", [])
        if isinstance(entry_uuid, list) and entry_uuid:
            logger.debug("uuid in raw_attributes: return %s", entry_uuid[0])
            return entry_uuid[0]
        else:
            # 由于其他目录也可能会出现这样的 code，所以添加 category_id 进行转换
            dn = f"{self.category_id}-{raw_obj.get('dn')}"

            sha = hashlib.sha256(force_bytes(dn)).hexdigest()
            logger.debug("no uuid in raw_attributes, use dn instead: %s -> %s", dn, sha)
            return sha


@dataclass
class ProfileFieldMapper:
    """从 ldap 对象属性中获取用户字段"""

    config_loader: ConfigProvider
    setting_field_map: dict

    def get_field(self, user_meta, field_name, raise_exception=False) -> str:
        """通过字段名从 ldap 配置中获取内容"""
        try:
            setting_name = self.setting_field_map[field_name]
        except KeyError:
            if raise_exception:
                raise ValueError("该用户字段没有在配置中有对应项，无法同步")
            return ""

        try:
            ldap_field_name = self.config_loader[setting_name]
        except KeyError:
            if raise_exception:
                raise ValueError(f"用户目录配置中缺失字段 {setting_name}")
            return ""

        try:
            if user_meta[ldap_field_name]:
                return force_str(user_meta[ldap_field_name][0])

            return ""
        except KeyError:
            if raise_exception:
                raise ValueError(f"搜索数据中没有对应的字段 {ldap_field_name}")
            return ""

    def get_user_attributes(self) -> list:
        """获取远端属性名列表"""
        return [self.config_loader[x] for x in self.setting_field_map.values() if self.config_loader[x]]

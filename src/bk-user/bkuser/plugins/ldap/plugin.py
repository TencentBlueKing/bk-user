# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

# ignore custom logger must use %s string format in this file
# ruff: noqa: G004
import logging
from collections import defaultdict
from typing import DefaultDict, Dict, List

from django.utils.translation import gettext_lazy as _

from bkuser.plugins.base import BaseDataSourcePlugin, PluginLogger
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.ldap import utils
from bkuser.plugins.ldap.client import LDAPClient
from bkuser.plugins.ldap.exceptions import DataNotFoundError
from bkuser.plugins.ldap.models import LDAPDataSourcePluginConfig, LDAPObject
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser, TestConnectionResult

logger = logging.getLogger(__name__)


class LDAPDataSourcePlugin(BaseDataSourcePlugin):
    """LDAP 数据源插件"""

    id = DataSourcePluginEnum.LDAP
    config_class = LDAPDataSourcePluginConfig

    def __init__(self, plugin_config: LDAPDataSourcePluginConfig, logger: PluginLogger):
        self.plugin_config = plugin_config
        self.logger = logger
        # 缓存部门相关信息，解析用户时候需要使用，可避免重复拉取 & 计算
        self.dept_dn_code_map: Dict[str, str] = {}
        self.user_group_dns_map: DefaultDict[str, List[str]] = defaultdict(list)

    def fetch_departments(self) -> List[RawDataSourceDepartment]:
        """获取部门信息"""
        cfg = self.plugin_config.data_config
        with LDAPClient(self.plugin_config.server_config) as ldap_client:
            depts = ldap_client.fetch_all_objects(cfg.dept_search_filter, cfg.dept_object_class)
            self.logger.info(f"fetch {len(depts)} departments from ldap server")

        raw_depts = [self._gen_raw_dept(d) for d in depts]

        # 启用用户组的情况
        if self.plugin_config.user_group_config.enabled:
            self.logger.info("user group enabled...")

            with LDAPClient(self.plugin_config.server_config) as ldap_client:
                groups = ldap_client.fetch_all_objects(
                    self.plugin_config.user_group_config.search_filter,
                    self.plugin_config.user_group_config.object_class,  # type: ignore
                )
                self.logger.info(f"fetch {len(groups)} groups from ldap server")

            # 提前存用户 - 用户组映射表，而不是后续依赖用户的 memberOf 属性
            # memberOf 属性需要特殊配置，ldap server 不一定会提供
            self.user_group_dns_map = self._gen_user_group_dns_map(
                groups, self.plugin_config.user_group_config.group_member_field
            )
            self.logger.info(f"found {len(self.user_group_dns_map)} user in group")

            # 用户组算是特殊的部门
            raw_depts.extend([self._gen_raw_dept(g) for g in groups])

        # dn -> code (entryUUID) 映射表
        self.dept_dn_code_map = {d.extras["dn"]: d.code for d in raw_depts}

        # 将 parent dn 转换成 parent code，如果找不到对应的 Code，则设置为 None
        for d in raw_depts:
            if not d.parent:
                continue

            if parent_code := self.dept_dn_code_map.get(d.parent):
                d.extras["parent_dn"] = d.parent
                d.parent = parent_code
            else:
                self.logger.warning(f"parent code not found for dn `{d.parent}`, set parent to None")
                d.parent = None

        return raw_depts

    def fetch_users(self) -> List[RawDataSourceUser]:
        """获取用户信息"""
        if not self.dept_dn_code_map:
            self.logger.warning("dept cache not found, this will cause user not dept infos")

        cfg = self.plugin_config.data_config
        with LDAPClient(self.plugin_config.server_config) as ldap_client:
            users = ldap_client.fetch_all_objects(cfg.user_search_filter, cfg.user_object_class)
            self.logger.info(f"fetch {len(users)} users from ldap server")

        # 生成的原始用户数据，不含部门，leader 信息
        raw_users = [self._gen_raw_user(u) for u in users]

        # 给用户填充上部门信息（code）
        self._set_raw_users_departments(raw_users)

        # 给用户填充上 leader 信息（code）
        self._set_raw_users_leaders(raw_users)

        return raw_users

    def test_connection(self) -> TestConnectionResult:
        """连通性测试"""
        cfg = self.plugin_config.data_config
        err_msg, user, dept = "", None, None
        user_data, dept_data = None, None
        try:
            with LDAPClient(self.plugin_config.server_config) as ldap_client:
                dept_data = ldap_client.fetch_first_object(cfg.dept_search_filter, cfg.dept_object_class)
                user_data = ldap_client.fetch_first_object(cfg.user_search_filter, cfg.user_object_class)
        except DataNotFoundError as e:
            err_msg = str(e)
        except Exception as e:
            logger.exception("ldap data source plugin test connection error")
            err_msg = _("连接测试失败: 无法建立连接或请求超时，请检查配置。异常信息：{}").format(str(e))

        # 请求 API 有异常，直接返回
        if err_msg:
            return TestConnectionResult(error_message=err_msg)

        # 检查获取到的数据情况，若都没有数据，也是异常
        if not (user_data and dept_data):
            err_msg = _("获取到的用户/部门数据为空，请检查数据源服务")
        else:
            try:
                dept = self._gen_raw_dept(dept_data)
                user = self._gen_raw_user(user_data)
            except Exception:
                err_msg = _("解析用户/部门数据失败，请检查返回的数据格式")

        return TestConnectionResult(
            error_message=str(err_msg),
            user=user,
            department=dept,
            extras={"user_data": user_data, "department_data": dept_data},
        )

    def _set_raw_users_departments(self, raw_users: List[RawDataSourceUser]):
        """为用户设置部门信息"""
        for u in raw_users:
            user_dn = u.properties["dn"]

            # 用户 DN 解析出的部门
            dept_dn = self._parse_dept_dn_from_user_dn(user_dn)
            if dept_code := self.dept_dn_code_map.get(dept_dn):
                u.departments.append(dept_code)
            else:
                self.logger.warning(f"user `{user_dn}` dept dn: `{dept_dn}` code not found, skip...")

            # 用户组关联所得的部门
            if group_dns := self.user_group_dns_map.get(user_dn):
                for group_dn in group_dns:
                    if group_code := self.dept_dn_code_map.get(group_dn):
                        u.departments.append(group_code)
                    else:
                        self.logger.warning(f"user `{user_dn}` group dn `{group_dn}` code not found, skip...")

    def _set_raw_users_leaders(self, raw_users: List[RawDataSourceUser]):
        """为用户设置 leader 信息"""
        if not self.plugin_config.leader_config.enabled:
            self.logger.info("user leader not enabled, skip...")
            return

        leader_field = self.plugin_config.leader_config.leader_field
        self.logger.info(f"user leader enabled, use field `{leader_field}` as leader")

        # 用户 DN -> Code 映射表
        user_dn_code_map = {u.properties["dn"]: u.code for u in raw_users}

        for u in raw_users:
            user_dn = u.properties["dn"]
            for leader_dn in u.properties.get(leader_field, "").split(" "):
                if leader_code := user_dn_code_map.get(leader_dn):
                    u.leaders.append(leader_code)
                else:
                    self.logger.warning(f"user `{user_dn}` leader dn `{leader_dn}` code not found, skip...")

    @staticmethod
    def _gen_raw_dept(obj: LDAPObject) -> RawDataSourceDepartment:
        """生成部门信息"""

        # dn 格式如：ou=dept_a,ou=company,dc=bk,dc=example,dc=com
        # -> rdns: [ou=dept_a, ou=company, dc=bk, dc=example, dc=com]
        rdns = utils.parse_dn(obj.dn)
        # 当前对象
        cur, parent = rdns[0], rdns[1:]
        # 这里直接填充父 DN，只有 dc 也没关系，后续转换成 Code 会去掉的
        parent_dn = utils.gen_dn(parent) if parent else None

        return RawDataSourceDepartment(
            code=obj.attrs["entryUUID"],
            name=cur.attr_value,
            # 其实这里的 dn 还不是最终需要的值，需要下一步转换成 entryUUID
            parent=parent_dn,
            extras={"attr_type": cur.attr_type, "dn": obj.dn},
        )

    @staticmethod
    def _gen_raw_user(obj: LDAPObject) -> RawDataSourceUser:
        properties: Dict[str, str] = {"dn": obj.dn}

        for k, v in obj.attrs.items():
            if k in ["entryUUID", "objectClass"]:
                continue

            if isinstance(v, list):
                properties[k] = " ".join(str(ele) for ele in v)
            else:
                properties[k] = str(v)

        # 由于 LDAP 用户数据结果比较特殊，因此生成的时候，不带 leaders，departments 字段，由后续处理
        return RawDataSourceUser(code=obj.attrs["entryUUID"], properties=properties, leaders=[], departments=[])

    @staticmethod
    def _gen_user_group_dns_map(groups: List[LDAPObject], group_member_field: str) -> DefaultDict[str, List[str]]:
        """根据用户组信息，生成用户 - 用户组映射关系"""
        user_group_dns_map: DefaultDict[str, List[str]] = defaultdict(list)
        for g in groups:
            for member in g.attrs.get(group_member_field, []):
                user_group_dns_map[member].append(g.dn)

        return user_group_dns_map

    @staticmethod
    def _parse_dept_dn_from_user_dn(dn: str) -> str:
        """从用户 DN 中获取部门信息（去除第一个层级的就是部门）"""
        return utils.gen_dn(utils.parse_dn(dn)[1:])

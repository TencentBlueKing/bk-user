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
import re
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Generator, List

import phonenumbers
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import ugettext_lazy as _

from .exceptions import ParseFailedException
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.utils import align_country_iso_code
from bkuser_core.profiles.validators import validate_username

logger = logging.getLogger(__name__)


@dataclass
class CellParser:
    name: ClassVar[str]
    category_id: int
    required: ClassVar[bool] = True

    def parse(self, raw_content: str) -> Dict:
        """解析单元格内容，转换为可插入参数模式，并兼顾对于格式的异常处理"""
        raise NotImplementedError

    def parse_to_db_obj(self, raw_content) -> Any:
        """解析单元格内容，转换为该字段普通形式"""
        raise NotImplementedError


@dataclass
class ColumnParser:
    name: ClassVar[str]
    category_id: int

    def parse(self, raw_column_values: list) -> Any:
        """解析某一列数据"""
        raise NotImplementedError


@dataclass
class DepartmentCellParser(CellParser):
    """
    对于部门字段而言，Excel 单个单元格可能存在多个部门链路

    总公司/部门A/部门B \n
    总公司/部门C/部门D

    需要解析成 [["总公司", "部门A", "部门B"], ["总公司", "部门C", "部门D"]]
    """

    name = "department_name"

    def parse(self, raw_content: str) -> dict:
        raw_departments = self._parse_raw_department_values(raw_content)
        department_groups = []
        for _raw in raw_departments:
            group = self._parse_single_department_value(_raw)
            if group not in department_groups:
                department_groups.append(group)

        return {self.name: department_groups}

    def parse_to_db_obj(self, raw_content) -> Generator[Department, None, None]:
        groups = self.parse(raw_content)[self.name]
        for group in groups:
            # 从叶子节点开始查找
            group.reverse()
            yield self._get_department_by_parent(group, 0)

    def _get_department_by_parent(self, group: list, self_index: int):
        try:
            name = group[self_index]
        except IndexError:
            return None

        try:
            return Department.objects.get(name=name, category_id=self.category_id)
        except MultipleObjectsReturned:
            parent = self._get_department_by_parent(group, self_index + 1)
            return Department.objects.get(name=name, parent_id=parent, category_id=self.category_id)

    def _parse_raw_department_values(self, raw_value: str):
        """解析单个单元格的多个部门信息

        xx/xxx/xxxx\naa/aaa/aaaa
        拆分为
        ['xx/xxx/xxxx', 'aa/aaa/aaaa']
        """
        if not raw_value:
            return []
        # 多个部门形如(以 '\n' or ';' or ',' 分割)： xx/xx/xxx\naaa/aa/aaa
        try:
            return re.split(r"[;\n,]", raw_value)
        except Exception:
            raise ParseFailedException(field_name=self.name, reason=_("无法分割"))

    @staticmethod
    def _parse_single_department_value(raw_value):
        """解析 'xx/xxx/xxxx' 为 ['xx', 'xxx', 'xxxx']"""
        departments = [item.strip() for item in raw_value.split("/")]
        return list(filter(lambda x: x != "", departments))


@dataclass
class DepartmentColumnParser(ColumnParser):
    name = "department_name"

    def __post_init__(self):
        self.cell_parser = DepartmentCellParser(self.category_id)

    def parse(self, raw_column_values: list) -> Any:
        departments = []
        for raw_department_groups in raw_column_values:
            department_groups = self.cell_parser.parse(raw_department_groups)[self.name]
            for group in department_groups:
                if group not in departments:
                    departments.append(group)

        return departments


@dataclass
class LeadersCellParser(CellParser):
    """
    对于上级字段而言，Excel 单个单元格可能存在多个上级的 username

    usernamea,usernameb

    需要解析成 Profile<xxxx-usernamea> Profile<xxxx-usernameb>
    """

    name = "leader"

    def parse(self, raw_content: str) -> dict:
        return {self.name: self._parse_raw_leader_username_list(raw_content)}

    def parse_to_db_obj(self, raw_content) -> List[Profile]:
        if not raw_content:
            return []

        username_list = self.parse(raw_content)[self.name]
        return Profile.objects.filter(username__in=username_list, category_id=self.category_id)

    @staticmethod
    def _parse_raw_leader_username_list(raw_value: str):
        """解析单个单元格多个username

        usernameA,usernameB
        拆分为
        ['usernameA', 'usernameB']
        """
        if not raw_value:
            return []
        return [x.strip() for x in re.split(r"[;\n,]", raw_value) if x]


@dataclass
class UsernameCellParser(CellParser):
    """用户名解析"""

    name = "username"

    def parse(self, raw_content: str) -> dict:
        # Excel 解析如果用户名全数字, 会被读取成数字, 导致这里报错, 暂时在这里强转; 先解决问题
        # FIXME: 统一重构excel导入, 每列确定的类型, 在上游读取就屏蔽确认
        # https://github.com/TencentBlueKing/bk-user/issues/673
        if not raw_content:
            raise ParseFailedException(field_name=self.name, reason=_("{} 是必须的").format(self.name))
        raw_content = str(raw_content)

        try:
            validate_username(value=raw_content)
        except Exception:
            logger.error("username<%s> has wrong format", raw_content)
            raise ParseFailedException(field_name=self.name, reason=_("{} 不符合格式要求").format(raw_content))

        return {self.name: raw_content}


@dataclass
class PhoneNumberParser(CellParser):
    """
    对于号码字段而言，需要解析出 Country Code
    """

    name = "telephone"

    def parse(self, raw_content: str) -> dict:
        try:
            pn = phonenumbers.parse(raw_content)

        except phonenumbers.NumberParseException:
            # 无地区码手机号的解析可能异常，尝试使用默认的中国地区码进行解析
            logger.debug("failed to parse phone number: %s", raw_content)
            try:
                logger.debug("use country_code:CN to parse")
                pn = phonenumbers.parse(raw_content, "CN")
                # phonenumbers库在验证号码的时：过短会解析为有效号码，超过250的字节才算超长=》所以这里需要显式做中国号码的长度校验
                if len(str(pn.national_number)) != 11:
                    raise ParseFailedException(field_name=self.name, reason=_("{} 不符合长度要求").format(raw_content))

            except Exception as e:
                raise ParseFailedException(field_name=self.name, reason=_("{}".format(e)))

        except Exception as e:  # pylint: disable=broad-except
            logger.debug("failed to parse phone number: %s", raw_content)
            raise ParseFailedException(field_name=self.name, reason=_("{}".format(e)))

        # 这里历史代码在except捕获异常后还是进行返回 =》导致实际是跳过了校验，暂时注释以便后续追溯
        # except Exception:  # pylint: disable=broad-except
        #     logger.debug("failed to parse phone number: %s", raw_content)
        #     # 当无法分割国际号码段时，直接存储
        #     if not raw_content:
        #         raise ParseFailedException(field_name=self.name, reason=_("{} 是必须的").format(self.name))
        #     return {self.name: raw_content}

        country_code, iso_code = align_country_iso_code(str(pn.country_code), "")
        return {
            "country_code": country_code,
            "telephone": str(pn.national_number),
            "iso_code": iso_code,
        }


@dataclass
class EmailCellParser(CellParser):
    """
    邮箱解析
    """

    name = "email"

    def parse(self, raw_content: str) -> dict:
        email_validator = EmailValidator()
        try:
            email_validator(raw_content)
        except ValidationError as e:
            logger.debug("failed to parse email: {}".format(e))
            raise ParseFailedException(field_name=self.name, reason=_("{} 不符合格式要求").format(raw_content))
        return {self.name: raw_content}

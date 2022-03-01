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
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Type
from unicodedata import category

from bkuser_core.categories.plugins.base import Fetcher, ProfileMeta, Syncer
from bkuser_core.common.db_sync import SyncOperation
from bkuser_core.common.progress import progress
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.profiles.constants import DynamicFieldTypeEnum, ProfileStatus, StaffStatus
from bkuser_core.profiles.models import DynamicFieldInfo, LeaderThroughModel, Profile
from bkuser_core.profiles.utils import make_password_by_config
from bkuser_core.user_settings.loader import ConfigProvider
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from .client import ExcelHelper
from .exceptions import ColumnNotFound, DataFormatError, ParseFailedException
from .parsers import (
    CellParser,
    ColumnParser,
    DepartmentCellParser,
    DepartmentColumnParser,
    LeadersCellParser,
    PhoneNumberParser,
    UsernameCellParser,
)

logger = logging.getLogger(__name__)


@dataclass
class ExcelFetcher(Fetcher):
    title_keys: Optional[list] = None
    title_fields: Optional[list] = None

    def __post_init__(self):
        self.excel_helper = ExcelHelper()

    def fetch(self, raw_data_file):
        self.excel_helper.set_sheet_values(excel_file=raw_data_file)
        self.parser_set = ParserSet.from_classes(category_id=self.category_id, titles=self.excel_helper.get_titles())

        # 获取数据表的表头字段
        self.title_keys = self._get_title_fields(raw_name=True)
        self.title_fields = self._get_title_fields(raw_name=False)

        departments = DepartmentColumnParser(self.category_id).parse(
            self.excel_helper.get_column_values(self.get_column_index("department_name"))
        )
        user_rows = self.excel_helper.get_values()

        return user_rows, departments

    def _get_title_fields(self, raw_name=True) -> List:
        """通过用户提供的中文表头，获取对应的字段 key"""
        fields = DynamicFieldInfo.objects.filter(enabled=True)
        fields_display_name_map = {x.display_name: x for x in fields}

        try:
            fields = [fields_display_name_map[t] for t in self.excel_helper.get_titles() if t]
            if raw_name:
                return [x.name for x in fields]
            return fields

        except KeyError as e:
            raise DataFormatError(f"表头 {e} 找不到对应字段，请检查用户字段设置")

    def get_column_index(self, column_key: str) -> int:
        """获取某个字段的列序号"""
        if self.title_keys is None:
            raise ValueError("需要预先 fetch 数据")

        try:
            return self.title_keys.index(column_key)
        except ValueError:
            raise ColumnNotFound(f"查找的列 {column_key} 不存在")


@dataclass
class ExcelSyncer(Syncer):
    """Excel 数据同步类"""

    fetcher_cls: Type[ExcelFetcher] = ExcelFetcher

    def __post_init__(self):
        super().__post_init__()
        self._post_sync = False
        self._default_password_valid_days = int(ConfigProvider(self.category_id).get("password_valid_days"))
        self.fetcher: ExcelFetcher = self.get_fetcher()

    def sync(self, raw_data_file):
        user_rows, departments = self.fetcher.fetch(raw_data_file)
        with transaction.atomic():
            self._sync_departments(departments)

        with transaction.atomic():
            self._sync_users(self.fetcher.parser_set, user_rows)
            self._sync_leaders(self.fetcher.parser_set, user_rows)

    def _sync_departments(self, raw_department_groups):
        """由于部门之间存在比较多的父子关系，不适合使用批量插入，目前使用按照逻辑顺序插入"""

        # TODO: 插入时应该不需要关心 order
        def _get_order(parent_department: Department) -> int:
            return parent_department.get_max_order_in_children() + 1

        for department_names in raw_department_groups:
            logger.info("=========== trying to add departments: %s ===========" % department_names)

            # 以根组织开头
            root_depart, created = Department.objects.get_or_create(
                name=department_names[0], parent=None, category_id=self.category_id
            )
            if created:
                logger.info("created root department %s", department_names[0])

            # 逐级创建组织
            current_parent = root_depart
            for department_name in department_names[1:]:
                new_department, created = Department.objects.get_or_create(
                    name=department_name,
                    parent=current_parent,
                    category_id=self.category_id,
                    defaults={"order": _get_order(current_parent)},
                )
                if created:
                    logger.info("created department %s", department_name)

                current_parent = new_department

        logger.info("=========== departments synced ===========")
        return

    @staticmethod
    def _judge_data_all_none(raw_data: list) -> bool:
        """某些状况下会读取 Excel 整个空行"""
        return all(x is None for x in raw_data)

    def _sync_users(self, parser_set: "ParserSet", users: list):
        """在内存中操作&判断数据，bulk 插入"""
        logger.info("=========== trying to load profiles into memory ===========")

        total = len(users)
        for index, user_raw_info in enumerate(users):
            if self._judge_data_all_none(user_raw_info):
                logger.debug("empty line, skipping")
                continue

            # 拼接 profile 参数，生成 Profile 对象
            try:
                profile_params = parser_set.parse_row(user_raw_info, skip_keys=["department_name", "leader"])
                logger.debug("profile_params: %s", profile_params)
            except ParseFailedException as e:
                logger.exception(f"同步用户解析字段 <{e.field_name}> 失败: {e.reason}. [user_raw_info={user_raw_info}]")
                continue
            except Exception:  # pylint: disable=broad-except
                # TODO
                logger.exception("同步用户解析字段异常. [user_raw_info=%s]", user_raw_info)
                continue

            username = profile_params["username"]
            # 如果已经是删除状态，暂不处理
            if Profile.all_objects.filter(
                category_id=self.category_id,
                username=username,
                status=ProfileStatus.DELETED.name,
            ).exists():
                logger.debug("username<%s> already deleted, skip", username)
                continue

            logger.debug("parsed: %s", profile_params)
            # 展示进度
            progress(index, total, f"loading {username}")
            try:
                updating_profile = Profile.objects.get(username=username, category_id=self.category_id)

                # 如果已经存在，则更新该 profile
                for name, value in profile_params.items():
                    if name == "extras":
                        extras = updating_profile.extras or {}
                        #  存在旧格式数据,兼容处理
                        if isinstance(extras, list):
                            extras = {x["key"]: x["value"] for x in extras}

                        extras.update(value)
                        setattr(updating_profile, name, extras)
                        continue

                    setattr(updating_profile, name, value)
                profile_id = updating_profile.id
                self.db_sync_manager.magic_add(updating_profile, SyncOperation.UPDATE.value)
                logger.debug("(%s/%s) username<%s> already exist, trying to update it", username, index + 1, total)

            except ObjectDoesNotExist:
                profile_id = self.db_sync_manager.register_id(ProfileMeta)
                password, _ = make_password_by_config(self.category_id)
                initial_params = {
                    "id": profile_id,
                    "status": ProfileStatus.NORMAL.name,
                    "staff_status": StaffStatus.IN.name,
                    "extras": {},
                    "enabled": True,
                    "category_id": self.category_id,
                    "domain": self.category.domain,
                    "password_valid_days": self._default_password_valid_days,
                    "password": password,
                }
                initial_params.update(profile_params)

                adding_profile = Profile(**initial_params)
                self.db_sync_manager.magic_add(adding_profile)
                logger.debug("(%s/%s): adding profile %s", index, total, username)

            # 2 获取关联的部门DB实例，创建关联对象
            progress(index, total, "adding profile & department relation")
            department_groups = parser_set.get_cell_data("department_name", user_raw_info)

            cell_parser = DepartmentCellParser(self.category_id)
            for department in cell_parser.parse_to_db_obj(department_groups):
                relation_params = {"department_id": department.pk, "profile_id": profile_id}
                try:
                    DepartmentThroughModel.objects.get(**relation_params)
                except DepartmentThroughModel.DoesNotExist:
                    department_attachment = DepartmentThroughModel(**relation_params)
                    self.db_sync_manager.magic_add(department_attachment)

        # 需要在处理 leader 之前全部插入 DB
        self.db_sync_manager[Profile].sync_to_db()
        self.db_sync_manager[DepartmentThroughModel].sync_to_db()

    def _sync_leaders(self, parser_set: "ParserSet", users: list):
        # 由于 leader 需要等待 profiles 全部插入后才能引用
        for user_raw_info in users:
            if self._judge_data_all_none(user_raw_info):
                logger.debug("empty line, skipping")
                continue

            try:
                username = parser_set.parse_key("username", user_raw_info)["username"]
                leaders = LeadersCellParser(self.category_id).parse_to_db_obj(
                    parser_set.get_cell_data("leader", user_raw_info)
                )
            except ParseFailedException as e:
                logger.exception(f"同步上级解析字段 <{e.field_name}> 失败: {e.reason}. [user_raw_info={user_raw_info}]")
                continue
            except Exception:  # pylint: disable=broad-except
                logger.exception("同步上级解析字段异常. [user_raw_info=%s]", user_raw_info)
                continue

            try:
                from_profile = Profile.objects.get(category_id=self.category_id, username=username)
            except ObjectDoesNotExist:
                logger.error("profile %s does not exist. [category_id=%s]", username, self.category_id)
                continue

            for leader in leaders:
                params = {"from_profile_id": from_profile.id, "to_profile_id": leader.pk}
                try:
                    LeaderThroughModel.objects.get(**params)
                except LeaderThroughModel.DoesNotExist:
                    adding_leader_profile = LeaderThroughModel(**params)
                    self.db_sync_manager.magic_add(adding_leader_profile)

        # 单独批量插入 leaders
        self.db_sync_manager[LeaderThroughModel].sync_to_db()


@dataclass
class ParserSet:
    # 用户提供的中文表头信息
    titles: List[str]
    cell_parsers: Dict[str, "CellParser"]
    column_parsers: Dict[str, "ColumnParser"]

    def __post_init__(self):
        fields = DynamicFieldInfo.objects.filter(enabled=True, display_name__in=self.titles)

        missing_names = set(self.titles) - {x.display_name for x in fields}
        if missing_names:
            raise ValueError(_("找不到 {} 对应的字段信息, 请检查用户字段设置").format(",".join(list(missing_names))))

        self.fields = OrderedDict({fields.get(display_name=x).name: fields.get(display_name=x) for x in self.titles})

    @classmethod
    def from_classes(
        cls,
        category_id: int,
        titles: List[str],
        cell_classes: Optional[Sequence[Type]] = None,
        column_classes: Optional[Sequence[Type]] = None,
    ) -> "ParserSet":

        l_parsers = {}
        for cell_cls in cell_classes or [
            UsernameCellParser,
            DepartmentCellParser,
            LeadersCellParser,
            PhoneNumberParser,
        ]:
            l_parsers[cell_cls.name] = cell_cls.__call__(category_id)

        n_parsers = {}
        for col_cls in column_classes or [DepartmentColumnParser]:
            n_parsers[col_cls.name] = col_cls.__call__(category_id)

        return cls(cell_parsers=l_parsers, column_parsers=n_parsers, titles=titles)

    def parse_row(self, row_data_list: list, skip_keys: List[str]):
        """尝试解析整行内容"""
        params = {}
        extras = {}
        for f_name, f in self.fields.items():
            if f_name in skip_keys:
                continue

            if f.builtin:
                params.update(self.parse_key(f_name, row_data_list))
            else:
                extras.update(GeneralParser(f).parse(self.get_cell_data(f_name, row_data_list)))

        params["extras"] = extras
        return params

    def parse_key(self, column_key: str, row_data_list: list) -> dict:
        """解析行数据"""
        cell_data = self.get_cell_data(column_key, row_data_list)
        try:
            _pa = self.cell_parsers[column_key]
            return _pa.parse(cell_data)
        except KeyError:
            # 未注册的字段解析，统一处理
            return GeneralParser(self.fields[column_key]).parse(cell_data)

    def get_cell_data(self, column_key: str, row_data_list: list) -> str:
        """获取某一个单元格数据"""
        index = list(self.fields.keys()).index(column_key)
        return row_data_list[index]


@dataclass
class GeneralParser:
    """通用解析器"""

    field: DynamicFieldInfo

    @staticmethod
    def _judge_value_is_empty(value: str) -> bool:
        # position 相关字段存在 int(0) 的可能
        if value == 0:
            return False

        return not bool(value)

    def parse(self, raw_content: str) -> dict:

        value: Any = raw_content
        if self._judge_value_is_empty(value):
            if not self._judge_value_is_empty(self.field.default):
                return {self.field.name: self.field.default}

            if self.field.require:
                # 即使必填字段存在默认值，这里也直接报错
                raise ParseFailedException(
                    field_name=self.field.name,
                    reason=_("{} 字段是必填内容").format(self.field.display_name),
                )
            else:
                # 对于非必填的空值，直接跳过处理
                return {}

        if self.field.options:
            if self.field.type == DynamicFieldTypeEnum.MULTI_ENUM.value:
                raw_content_list = str(raw_content).split(",")
                value = [
                    self.field.get_option_key_by_value(r)  # type: ignore
                    for r in raw_content_list
                    if self.field.get_option_key_by_value(r) is not None
                ]
                if not value:
                    value = None
            else:
                value = self.field.get_option_key_by_value(str(raw_content))

            if not self._judge_value_is_empty(value):
                return {self.field.name: value}

            if self._judge_value_is_empty(self.field.default):
                raise ParseFailedException(
                    field_name=self.field.name,
                    reason=_("当前值 {} 找不到预设选项").format(raw_content),
                )

            value = self.field.default

        return {self.field.name: value}

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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Type

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from .client import ExcelHelper
from .exceptions import ColumnNotFound, DataFormatError, ParseFailedException
from .parsers import (
    CellParser,
    ColumnParser,
    DepartmentCellParser,
    DepartmentColumnParser,
    EmailCellParser,
    LeadersCellParser,
    PhoneNumberParser,
    UsernameCellParser,
)
from bkuser_core.categories.plugins.base import Fetcher, ProfileMeta, Syncer
from bkuser_core.common.db_sync import SyncOperation
from bkuser_core.common.progress import progress
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.profiles.constants import DynamicFieldTypeEnum, ProfileStatus, StaffStatus
from bkuser_core.profiles.models import DynamicFieldInfo, LeaderThroughModel, Profile
from bkuser_core.profiles.tasks import send_password_by_email
from bkuser_core.profiles.utils import make_password_by_config
from bkuser_core.user_settings.loader import ConfigProvider

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

        line_start = 2
        user_rows = self.excel_helper.get_values(line_start=line_start)

        department_rows = self.excel_helper.get_column_values(self.get_column_index("department_name"))
        departments = DepartmentColumnParser(self.category_id).parse(department_rows)

        # 组织必填怎么判断?
        # validate the department should not be empty
        real_user_rows = [u for u in user_rows if not ExcelSyncer._judge_data_all_none(u)]
        real_user_count = len(real_user_rows)
        real_department_rows = department_rows[:real_user_count]
        for index, department in enumerate(real_department_rows):
            if department is None:
                raise DataFormatError(f"第 {index + line_start} 行组织不能为空")

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


def _failed_records_error_message(failed_records: List[Dict]) -> str:
    """生成错误信息"""
    return "; ".join(
        [
            _("第{index}行，字段{field}，原因：{reason}，数据：{data}").format(
                index=record["index"] + 1, field=record["field"], reason=record["reason"], data=record["data"]
            )
            for record in failed_records
        ]
    )


@dataclass
class ExcelSyncer(Syncer):
    """Excel 数据同步类"""

    fetcher_cls: Type[ExcelFetcher] = ExcelFetcher
    notify_profile_init_password_dict: Dict[Profile, str] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        self._post_sync = False
        self._default_password_valid_days = int(ConfigProvider(self.category_id).get("password_valid_days"))
        self.fetcher: ExcelFetcher = self.get_fetcher()

    def sync(self, raw_data_file, is_overwrite, language=""):
        # Note: 对于Excel导入，语言涉及到表头的读取，DynamicFieldInfo的display_name将会根据语言自动输出对应语言的值
        if language:
            translation.activate(language)

        user_rows, departments = self.fetcher.fetch(raw_data_file)
        with transaction.atomic():
            self._sync_departments(departments)

        with transaction.atomic():
            self._sync_users(self.fetcher.parser_set, user_rows, is_overwrite)
            self._sync_leaders(self.fetcher.parser_set, user_rows)

        self._notify_init_passwords()

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

    def _department_profile_relation_handle(
        self,
        is_overwrite: bool,
        department_groups: str,
        profile_id: int,
        should_deleted_department_profile_relation_ids: list,
    ):
        cell_parser = DepartmentCellParser(self.category_id)
        # 已存在的用户-部门关系
        old_department_profile_relations = DepartmentThroughModel.objects.filter(profile_id=profile_id)
        # Note: 有新关系可能存在重复数据，所以这里使用不变的old_department_set用于后续判断是否存在的依据，
        # 而不使用后面会变更的old_department_relations数据
        old_department_set = {r.department_id for r in old_department_profile_relations}
        old_department_relations = {r.department_id: r.id for r in old_department_profile_relations}

        for department in cell_parser.parse_to_db_obj(department_groups):
            # 用户-部门关系已存在
            if department.pk in old_department_set:
                # Note: 可能本次更新里存在重复数据，dict无法重复移除
                if department.pk in old_department_relations:
                    del old_department_relations[department.pk]
                continue

            # 不存在则添加
            department_attachment = DepartmentThroughModel(department_id=department.pk, profile_id=profile_id)
            self.db_sync_manager.magic_add(department_attachment)

        # 已存在的数据从old_department_relations移除后，最后剩下的数据，表示多余的，即本次更新里不存在的用户部门关系
        # 如果是覆盖，则记录需要删除多余数据
        if is_overwrite and len(old_department_relations) > 0:
            should_deleted_department_profile_relation_ids.extend(old_department_relations.values())

    def _sync_users(self, parser_set: "ParserSet", users: list, is_overwrite: bool = False):
        """在内存中操作&判断数据，bulk 插入"""
        logger.info("=========== trying to load profiles into memory ===========")

        # to record failed records
        failed_records = []
        success_count = 0

        total = len(users)
        should_deleted_department_profile_relation_ids: list = []
        for index, user_raw_info in enumerate(users):
            if self._judge_data_all_none(user_raw_info):
                logger.debug("empty line, skipping")
                continue

            # 拼接 profile 参数，生成 Profile 对象
            try:
                profile_params = parser_set.parse_row(
                    user_raw_info,
                    skip_keys=["department_name", "leader", "create_time", "last_login_time"],
                )
                logger.debug("profile_params: %s", profile_params)
                # NOTE: 解析后, 非必填的字段 status=NORMAL, staff_status=IN, position=0
            except ParseFailedException as e:
                # 同步上级解析字段 <username> 失败: u123456 不符合格式要求. [user_raw_info=()]
                logger.exception(f"同步用户解析字段 <{e.field_name}> 失败: {e.reason}. [user_raw_info={user_raw_info}]")
                failed_records.append(
                    {
                        "index": index,
                        "field": e.field_name,
                        "reason": e.reason,
                        "data": user_raw_info,
                    }
                )
                continue
            except Exception:  # pylint: disable=broad-except
                logger.exception("同步用户解析字段异常. [user_raw_info=%s]", user_raw_info)
                failed_records.append(
                    {
                        "index": index,
                        "field": "unknown",
                        "reason": "parse failed",
                        "data": user_raw_info,
                    }
                )
                continue

            success_count += 1

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
                # 已存在的用户：如果未勾选 <进行覆盖更新>（即is_overwrite为false）=》则忽略，反之则更新该 profile
                if not is_overwrite:
                    logger.debug(
                        "username %s exist, and is_overwrite is false, so will not do update for this user, skip",
                        username,
                    )
                    continue
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
                raw_password, should_notify = make_password_by_config(self.category_id, return_raw=True)
                initial_params = {
                    "id": profile_id,
                    "status": ProfileStatus.NORMAL.name,
                    "staff_status": StaffStatus.IN.name,
                    "extras": {},
                    "enabled": True,
                    "category_id": self.category_id,
                    "domain": self.category.domain,
                    "password_valid_days": self._default_password_valid_days,
                    "password": make_password(raw_password),
                }
                initial_params.update(profile_params)

                adding_profile = Profile(**initial_params)
                self.db_sync_manager.magic_add(adding_profile)
                logger.debug("(%s/%s): adding profile %s", index, total, username)
                if should_notify:
                    self.notify_profile_init_password_dict[adding_profile] = raw_password

            # 2 获取关联的部门DB实例，创建关联对象
            progress(index, total, "adding profile & department relation")
            department_groups = parser_set.get_cell_data("department_name", user_raw_info)
            self._department_profile_relation_handle(
                is_overwrite, department_groups, profile_id, should_deleted_department_profile_relation_ids
            )

        if len(should_deleted_department_profile_relation_ids) > 0:
            DepartmentThroughModel.objects.filter(id__in=should_deleted_department_profile_relation_ids).delete()

        # 需要在处理 leader 之前全部插入 DB
        self.db_sync_manager[Profile].sync_to_db()
        self.db_sync_manager[DepartmentThroughModel].sync_to_db()

        failed_count = len(failed_records)
        if failed_count > 0:
            message = _("导入执行完成: 成功 {} 条记录, 失败 {} 条记录, 失败详情 {}").format(
                success_count, failed_count, _failed_records_error_message(failed_records)
            )
            raise Exception(message)

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

    def _notify_init_passwords(self) -> None:
        # 是否发送初始化密码邮件
        if self.notify_profile_init_password_dict:
            for instance, password in self.notify_profile_init_password_dict.items():
                try:
                    send_password_by_email.delay(instance.id, raw_password=password, init=True)
                except Exception:  # pylint: disable=broad-except
                    logger.exception(
                        "failed to send init password via email. [profile.id=%s, profile.username=%s",
                        instance.id,
                        instance.username,
                    )


@dataclass
class ParserSet:
    # 用户提供的中文表头信息
    titles: List[str]
    cell_parsers: Dict[str, "CellParser"]
    column_parsers: Dict[str, "ColumnParser"]

    def __post_init__(self):
        fields = DynamicFieldInfo.objects.filter(enabled=True)
        fields_display_name_map = {x.display_name: x for x in fields}

        missing_names = set(self.titles) - set(fields_display_name_map.keys())
        if missing_names:
            raise ValueError(_("找不到 {} 对应的字段信息, 请检查用户字段设置").format(",".join(list(missing_names))))

        self.fields = OrderedDict({fields_display_name_map[x].name: fields_display_name_map[x] for x in self.titles})

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
            EmailCellParser,
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

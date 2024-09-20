# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from itertools import groupby
from typing import Dict, List

from django.conf import settings
from openpyxl.reader.excel import load_workbook
from openpyxl.styles import Alignment, Font, colors
from openpyxl.styles.numbers import FORMAT_TEXT
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantUserCustomField


class DataSourceUserExporter:
    """导出数据源用户 & 组织信息"""

    workbook: Workbook
    sheet: Worksheet
    # 模板中字段名行索引
    col_name_row_idx = 2
    # 新增的列的默认宽度
    default_column_width = 40

    def __init__(self, data_source: DataSource):
        self.data_source = data_source
        self.users = DataSourceUser.objects.filter(data_source=data_source)
        self.custom_fields = TenantUserCustomField.objects.filter(tenant_id=data_source.owner_tenant_id)
        self._load_template()

    def get_template(self) -> Workbook:
        # 填充自定义字段默认值以供参考
        extras = [",".join(f.default) if isinstance(f.default, list) else str(f.default) for f in self.custom_fields]
        self.sheet.append(  # noqa: PERF401 sheet isn't a list
            ("zhangsan", "张三", "zhangsan@qq.com", "+8613512345678", "公司/部门A,公司/部门B", "lisi,wangwu", *extras)
        )
        return self.workbook

    def export(self) -> Workbook:
        dept_org_map = self._build_dept_org_map()
        user_departments_map = self._build_user_departments_map()
        user_leaders_map = self._build_user_leaders_map()
        user_username_map = self._build_user_username_map()

        for u in self.users:
            extras = []
            # 自定义字段的值，不一定是字符串类型，需要做下转换
            for field in self.custom_fields:
                # 导出数据时，若自定义字段不存在或为空值，则替换为 ""
                value = u.extras.get(field.name) or ""
                value = ",".join(value) if isinstance(value, list) else str(value)  # type: ignore
                extras.append(value)

            self.sheet.append(  # noqa: PERF401 sheet isn't a list
                (
                    # 用户名
                    u.username,
                    # 姓名
                    u.full_name,
                    # 邮箱
                    u.email,
                    # 手机号
                    f"+{u.phone_country_code}{u.phone}" if u.phone else "",
                    # 组织信息
                    ",".join(dept_org_map.get(dept_id, "") for dept_id in user_departments_map.get(u.id, [])),
                    # 直接上级
                    ",".join(user_username_map.get(leader_id, "") for leader_id in user_leaders_map.get(u.id, [])),
                    # 自定义字段
                    *extras,
                )
            )

        self._set_all_columns_to_text_format()
        return self.workbook

    def _load_template(self):
        self.workbook = load_workbook(settings.EXPORT_ORG_TEMPLATE)
        self.sheet = self.workbook["users"]
        # 设置表格样式
        self.sheet.alignment = Alignment(wrapText=True)
        # 补充租户用户自定义字段
        self._update_sheet_custom_field_columns()
        # 将所有单元格设置为文本格式
        self._set_all_columns_to_text_format()

    def _update_sheet_custom_field_columns(self):
        """在模版中补充自定义字段"""
        builtin_columns_length = len(list(self.sheet.columns))
        for col_idx, field in enumerate(self.custom_fields, start=builtin_columns_length):
            # NOTE：openpyxl 行/列数字索引是从 1 开始的...
            name_cell = self.sheet.cell(row=self.col_name_row_idx, column=col_idx + 1)
            name_cell.value = f"{field.display_name}/{field.name}"
            # 设置为垂直居中 + 自动换行
            name_cell.alignment = Alignment(vertical="center", wrapText=True)
            # 如果是必填列，列名设置为红色
            if field.required:
                name_cell.font = Font(color=colors.COLOR_INDEX[2])

            # 自定义字段提示信息（位置是字段名的上一行）
            tips_cell = self.sheet.cell(row=self.col_name_row_idx - 1, column=col_idx + 1)
            opts = ", ".join(opt["id"] for opt in field.options)
            if field.data_type == UserFieldDataType.ENUM:
                tips_cell.value = f"单选枚举（One of {opts}）"
            elif field.data_type == UserFieldDataType.MULTI_ENUM:
                tips_cell.value = f"多选枚举，多个值以英文逗号分隔（Any of {opts}, separated by commas）"
            elif field.data_type == UserFieldDataType.NUMBER:
                tips_cell.value = "数据类型：数值（DataType: Number）"
            elif field.data_type == UserFieldDataType.STRING:
                tips_cell.value = "数据类型：字符串（DataType: String）"
            # 设置吸底 + 自动换行
            tips_cell.alignment = Alignment(vertical="bottom", wrapText=True)

            # 设置默认列宽
            self.sheet.column_dimensions[self._gen_sheet_col_idx(col_idx)].width = self.default_column_width

    def _set_all_columns_to_text_format(self):
        # 将单元格设置为纯文本模式，防止出现类型转换
        # ref: https://stackoverflow.com/questions/57492559
        for idx, _ in enumerate(self.sheet.columns):
            self.sheet.column_dimensions[self._gen_sheet_col_idx(idx)].number_format = FORMAT_TEXT

    @staticmethod
    def _gen_sheet_col_idx(idx: int) -> str:
        """
        在 excel 表中，列的 index 是 A，B，C，D ...，
        该函数可以将数字索引转换为列索引，利用的是 ascii 码顺序
        """
        return chr(ord("A") + idx)

    def _build_dept_org_map(self) -> Dict[int, str]:
        """
        获取部门与组织关系的映射表

        :returns: {dept_id: organization} 例如：{1: "总公司", 2: "总公司/深圳总部"}
        """
        dept_name_map = dict(
            DataSourceDepartment.objects.filter(data_source=self.data_source).values_list("id", "name")
        )
        relations = DataSourceDepartmentRelation.objects.filter(data_source=self.data_source)

        dept_org_map = {}

        def _build_by_recursive(rel: DataSourceDepartmentRelation, parent_org: str):
            dept_id = int(rel.department_id)
            dept_name = dept_name_map[dept_id]

            current_org = "/".join([parent_org, dept_name]) if parent_org else dept_name
            dept_org_map[dept_id] = current_org

            for child in rel.get_children():
                _build_by_recursive(child, current_org)

        # 使用 cached_tree 避免在后续使用 get_children 时候触发 DB 查询
        # 注：get_ascendants 无法使用 mptt 自带的缓存，暂不考虑在查询部门组织信息时使用
        for rel in relations.get_cached_trees():
            _build_by_recursive(rel, "")

        return dept_org_map

    def _build_user_departments_map(self) -> Dict[int, List[int]]:
        """
        获取用户与部门关系的映射表

        :returns: {user_id: [dept_id1, dept_id2, ...]}
        """
        relations = (
            DataSourceDepartmentUserRelation.objects.filter(user__in=self.users)
            .order_by("user_id")
            .values("user_id", "department_id")
        )
        return {
            user_id: sorted([r["department_id"] for r in group])
            for user_id, group in groupby(relations, key=lambda r: r["user_id"])
        }

    def _build_user_leaders_map(self) -> Dict[int, List[int]]:
        """
        获取用户与 leader 关系的映射表

        :returns: {user_id: [leader_id1, leader_id2, ...]}
        """
        relations = (
            DataSourceUserLeaderRelation.objects.filter(user__in=self.users)
            .order_by("user_id")
            .values("user_id", "leader_id")
        )
        return {
            user_id: sorted([r["leader_id"] for r in group])
            for user_id, group in groupby(relations, key=lambda r: r["user_id"])
        }

    def _build_user_username_map(self) -> Dict[int, str]:
        """获取用户与用户名的映射表"""
        return dict(self.users.values_list("id", "username"))

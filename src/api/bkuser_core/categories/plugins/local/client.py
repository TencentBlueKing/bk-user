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
from dataclasses import dataclass
from typing import Optional

from openpyxl import load_workbook


@dataclass
class ExcelHelper:
    """Excel操作小帮手"""

    excel_file: Optional[list] = None
    sheet_values: Optional[list] = None
    sheet_index: int = 0

    def set_sheet_values(self, excel_file, sheet_index=0):
        excel = load_workbook(excel_file)
        worksheet = excel.worksheets[sheet_index]
        self.excel_file = excel_file
        self.sheet_values = list(worksheet.values)

    def get_titles(self) -> list:
        """获取表头数据"""
        if self.sheet_values is None:
            raise ValueError("should set sheet values first")

        return [x for x in self.sheet_values[1] if x]

    def get_values(self, line_start: int = 2) -> list:
        """获取表单数据"""
        if self.sheet_values is None:
            raise ValueError("should set sheet values first")

        return self.sheet_values[line_start:]

    def get_column_values(self, column_index: int, line_start: int = 2) -> list:
        """获取某一列数据"""
        values = self.get_values(line_start)
        return [x[column_index] for x in values]

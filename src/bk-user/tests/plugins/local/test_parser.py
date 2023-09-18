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
import pytest
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook

# TODO (su) 补充 parser 的单元测试


@pytest.fixture()
def user_workbook() -> Workbook:
    return load_workbook("./tmp.xlsx")


class TestLocalDataSourceDataParser:
    def test_validate_case_xx(self):
        ...

    def test_get_departments(self):
        ...

    def test_get_users(self):
        ...

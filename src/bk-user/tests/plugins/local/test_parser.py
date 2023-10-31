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
from typing import List

import pytest
from bkuser.plugins.local.exceptions import (
    CustomColumnNameInvalid,
    DuplicateColumnName,
    DuplicateUsername,
    InvalidLeader,
    InvalidUsername,
    RequiredFieldIsEmpty,
    SheetColumnsNotMatch,
    UserSheetNotExists,
)
from bkuser.plugins.local.parser import LocalDataSourceDataParser
from bkuser.plugins.local.utils import gen_code
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser


class TestLocalDataSourceDataParser:
    def test_validate_case_not_user_sheet(self, user_wk):
        # 删除 user sheet，导致空数据
        user_wk.remove(user_wk["users"])
        with pytest.raises(UserSheetNotExists):
            LocalDataSourceDataParser(user_wk).parse()

    def test_validate_case_columns_not_match(self, user_wk):
        # 修改列名，导致与内建字段不匹配
        user_wk["users"]["B2"].value = "这不是姓名/not_full_name"
        with pytest.raises(SheetColumnsNotMatch):
            LocalDataSourceDataParser(user_wk).parse()

    def test_validate_case_custom_column_name_invalid(self, user_wk):
        # 修改列名，导致自定义列名不合法
        user_wk["users"]["G2"].value = "年龄@45"
        with pytest.raises(CustomColumnNameInvalid):
            LocalDataSourceDataParser(user_wk).parse()

    def test_validate_case_duplicate_column_name(self, user_wk):
        # 修改列名，导致自定义列名重复
        user_wk["users"]["H2"].value = "年龄/age"
        with pytest.raises(DuplicateColumnName):
            LocalDataSourceDataParser(user_wk).parse()

    def test_validate_case_required_field_is_empty(self, user_wk):
        # 修改表格数据，导致必填字段为空
        user_wk["users"]["A3"].value = ""
        with pytest.raises(RequiredFieldIsEmpty):
            LocalDataSourceDataParser(user_wk).parse()

    def test_validate_case_invalid_username_chinese(self, user_wk):
        # 修改表格数据，导致用户名非法
        user_wk["users"]["A4"].value = "张三"
        with pytest.raises(InvalidUsername):
            LocalDataSourceDataParser(user_wk).parse()

    def test_validate_case_invalid_username_punctuation(self, user_wk):
        # 修改表格数据，导致用户名非法
        user_wk["users"]["A4"].value = "zhangsan@m.com"
        with pytest.raises(InvalidUsername):
            LocalDataSourceDataParser(user_wk).parse()

    def test_validate_case_invalid_leader(self, user_wk):
        # 修改表格数据，导致用户是自己的 leader
        user_wk["users"]["F4"].value = "zhangsan, lisi,wangwu"
        with pytest.raises(InvalidLeader):
            LocalDataSourceDataParser(user_wk).parse()

    def test_validate_case_duplicate_username(self, user_wk):
        # 修改表格数据，导致用户名重复
        user_wk["users"]["A6"].value = "zhangsan"
        with pytest.raises(DuplicateUsername):
            LocalDataSourceDataParser(user_wk).parse()

    def test_validate_case_duplicate_username_case_insensitive(self, user_wk):
        # 修改表格数据，导致用户名重复（大小写不敏感的检查）
        user_wk["users"]["A6"].value = "ZhangSan"
        with pytest.raises(DuplicateUsername):
            LocalDataSourceDataParser(user_wk).parse()

    def test_get_departments(self, user_wk):
        parser = LocalDataSourceDataParser(user_wk)
        parser.parse()

        company_code = gen_code("公司")
        dept_a_code = gen_code("公司/部门A")
        dept_b_code = gen_code("公司/部门B")
        dept_c_code = gen_code("公司/部门C")
        center_aa_code = gen_code("公司/部门A/中心AA")
        center_ab_code = gen_code("公司/部门A/中心AB")
        group_aaa_code = gen_code("公司/部门A/中心AA/小组AAA")
        group_aba_code = gen_code("公司/部门A/中心AB/小组ABA")
        center_ba_code = gen_code("公司/部门B/中心BA")
        group_baa_code = gen_code("公司/部门B/中心BA/小组BAA")
        center_ca_code = gen_code("公司/部门C/中心CA")
        group_caa_code = gen_code("公司/部门C/中心CA/小组CAA")

        assert sorted(parser.get_departments(), key=lambda d: d.name) == [
            RawDataSourceDepartment(code=center_aa_code, name="中心AA", parent=dept_a_code),
            RawDataSourceDepartment(code=center_ab_code, name="中心AB", parent=dept_a_code),
            RawDataSourceDepartment(code=center_ba_code, name="中心BA", parent=dept_b_code),
            RawDataSourceDepartment(code=center_ca_code, name="中心CA", parent=dept_c_code),
            RawDataSourceDepartment(code=company_code, name="公司", parent=None),
            RawDataSourceDepartment(code=group_aaa_code, name="小组AAA", parent=center_aa_code),
            RawDataSourceDepartment(code=group_aba_code, name="小组ABA", parent=center_ab_code),
            RawDataSourceDepartment(code=group_baa_code, name="小组BAA", parent=center_ba_code),
            RawDataSourceDepartment(code=group_caa_code, name="小组CAA", parent=center_ca_code),
            RawDataSourceDepartment(code=dept_a_code, name="部门A", parent=company_code),
            RawDataSourceDepartment(code=dept_b_code, name="部门B", parent=company_code),
            RawDataSourceDepartment(code=dept_c_code, name="部门C", parent=company_code),
        ]

    def test_get_users(self, user_wk):
        parser = LocalDataSourceDataParser(user_wk)
        parser.parse()

        def gen_depts(orgs: List[str]) -> List[str]:
            return [gen_code(o) for o in orgs]

        assert sorted(parser.get_users(), key=lambda u: u.properties["age"]) == [
            RawDataSourceUser(
                code="zhangsan",
                properties={
                    "username": "zhangsan",
                    "full_name": "张三",
                    "email": "zhangsan@m.com",
                    "age": "20",
                    "gender": "male",
                    "region": "region-0",
                    "phone": "13512345671",
                    "phone_country_code": "86",
                },
                leaders=[],
                departments=gen_depts(["公司"]),
            ),
            RawDataSourceUser(
                code="lisi",
                properties={
                    "username": "lisi",
                    "full_name": "李四",
                    "email": "lisi@m.com",
                    "age": "21",
                    "gender": "female",
                    "region": "region-1",
                    "phone": "13512345672",
                    "phone_country_code": "86",
                },
                leaders=["zhangsan"],
                departments=gen_depts(["公司/部门A", "公司/部门A/中心AA"]),
            ),
            RawDataSourceUser(
                code="wangwu",
                properties={
                    "username": "wangwu",
                    "full_name": "王五",
                    "email": "wangwu@m.com",
                    "age": "22",
                    "gender": "male",
                    "region": "region-2",
                    "phone": "13512345673",
                    "phone_country_code": "63",
                },
                leaders=["zhangsan"],
                departments=gen_depts(["公司/部门A", "公司/部门B"]),
            ),
            RawDataSourceUser(
                code="zhaoliu",
                properties={
                    "username": "zhaoliu",
                    "full_name": "赵六",
                    "email": "zhaoliu@m.com",
                    "age": "23",
                    "gender": "male",
                    "region": "region-3",
                    "phone": "13512345674",
                    "phone_country_code": "86",
                },
                leaders=["lisi"],
                departments=gen_depts(["公司/部门A/中心AA"]),
            ),
            RawDataSourceUser(
                code="liuqi",
                properties={
                    "username": "liuqi",
                    "full_name": "柳七",
                    "email": "liuqi@m.com",
                    "age": "24",
                    "gender": "female",
                    "region": "region-4",
                    "phone": "13512345675",
                    "phone_country_code": "63",
                },
                leaders=["zhaoliu"],
                departments=gen_depts(["公司/部门A/中心AA/小组AAA"]),
            ),
            RawDataSourceUser(
                code="maiba",
                properties={
                    "username": "maiba",
                    "full_name": "麦八",
                    "email": "maiba@m.com",
                    "age": "25",
                    "gender": "male",
                    "region": "region-5",
                    "phone": "13512345676",
                    "phone_country_code": "86",
                },
                leaders=["lisi", "wangwu"],
                departments=gen_depts(["公司/部门A/中心AB"]),
            ),
            RawDataSourceUser(
                code="yangjiu",
                properties={
                    "username": "yangjiu",
                    "full_name": "杨九",
                    "email": "yangjiu@m.com",
                    "age": "26",
                    "gender": "female",
                    "region": "region-6",
                    "phone": "13512345677",
                    "phone_country_code": "86",
                },
                leaders=["wangwu"],
                departments=gen_depts(["公司/部门A/中心AB"]),
            ),
            RawDataSourceUser(
                code="lushi",
                properties={
                    "username": "lushi",
                    "full_name": "鲁十",
                    "email": "lushi@m.com",
                    "age": "27",
                    "gender": "male",
                    "region": "region-7",
                    "phone": "13512345678",
                    "phone_country_code": "86",
                },
                leaders=["wangwu", "maiba"],
                departments=gen_depts(["公司/部门B/中心BA", "公司/部门A/中心AB/小组ABA"]),
            ),
            RawDataSourceUser(
                code="linshiyi",
                properties={
                    "username": "linshiyi",
                    "full_name": "林十一",
                    "email": "linshiyi@m.com",
                    "age": "28",
                    "gender": "female",
                    "region": "region-8",
                    "phone": "13512345679",
                    "phone_country_code": "86",
                },
                leaders=["lushi"],
                departments=gen_depts(["公司/部门A/中心AB/小组ABA"]),
            ),
            RawDataSourceUser(
                code="baishier",
                properties={
                    "username": "baishier",
                    "full_name": "白十二",
                    "email": "baishier@m.com",
                    "age": "29",
                    "gender": "male",
                    "region": "region-9",
                    "phone": "13512345670",
                    "phone_country_code": "86",
                },
                leaders=["lushi"],
                departments=gen_depts(["公司/部门B/中心BA/小组BAA"]),
            ),
            RawDataSourceUser(
                code="qinshisan",
                properties={
                    "username": "qinshisan",
                    "full_name": "秦十三",
                    "email": "qinshisan@m.com",
                    "age": "30",
                    "gender": "female",
                    "region": "region-10",
                    "phone": "13512245671",
                    "phone_country_code": "86",
                },
                leaders=["lisi"],
                departments=gen_depts(["公司/部门C/中心CA/小组CAA"]),
            ),
            RawDataSourceUser(
                code="freedom",
                properties={
                    "username": "freedom",
                    "full_name": "自由人",
                    "email": "freedom@m.com",
                    "age": "666",
                    "gender": "other",
                    "region": "solar-system",
                    "phone": "1351234567",
                    "phone_country_code": "49",
                },
                leaders=[],
                departments=[],
            ),
        ]

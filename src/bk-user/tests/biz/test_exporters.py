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
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.biz.exporters import DataSourceUserExporter

pytestmark = pytest.mark.django_db


class TestDataSourceExporter:
    """测试用户数据导出 & 模板获取"""

    def test_get_template(self, bare_local_data_source, tenant_user_custom_fields):
        exporter = DataSourceUserExporter(bare_local_data_source)
        tmpl = exporter.get_template()

        assert "users" in tmpl.sheetnames
        assert [cell.value for cell in tmpl["users"][exporter.col_name_row_idx]] == [
            "用户名/username",
            "姓名/full_name",
            "邮箱/email",
            "手机号/phone_number",
            "组织/organizations",
            "直接上级/leaders",
            "年龄/age",
            "性别/gender",
            "籍贯/region",
        ]

    def test_export(self, full_local_data_source, tenant_user_custom_fields):
        # 初始化数据中，是没有 extras 的值的，这里更新下，以便于验证导出器的功能
        exists_users = DataSourceUser.objects.filter(data_source=full_local_data_source)
        for idx, user in enumerate(exists_users):
            user.extras = {"age": str(20 + idx), "gender": "male", "region": "region-" + str(idx)}
            user.save()

        # 导出数据，确认数据准确性，特别是自定义字段
        wk = DataSourceUserExporter(full_local_data_source).export()
        assert "users" in wk.sheetnames

        # 表格中第三行开始才是数据
        min_data_row_index = 3
        for idx, row in enumerate(wk["users"].iter_rows(min_row=min_data_row_index)):
            assert row[0].value == exists_users[idx].username
            assert row[1].value == exists_users[idx].full_name
            assert row[2].value == exists_users[idx].email
            assert row[3].value == f"+{exists_users[idx].phone_country_code}{exists_users[idx].phone}"
            # 第四第五列分别是组织，直接上级，不在这个循环做检查
            assert row[6].value == str(20 + idx)
            assert row[7].value == "male"
            assert row[8].value == "region-" + str(idx)

        # 检查组织信息
        assert [cell.value for cell in wk["users"]["E"][2:]] == [
            "公司",
            "公司/部门A, 公司/部门A/中心AA",
            "公司/部门A, 公司/部门B",
            "公司/部门A/中心AA",
            "公司/部门A/中心AA/小组AAA",
            "公司/部门A/中心AB",
            "公司/部门A/中心AB",
            "公司/部门B/中心BA, 公司/部门A/中心AB/小组ABA",
            "公司/部门A/中心AB/小组ABA",
            "公司/部门B/中心BA/小组BAA",
            "",
        ]

        # 检查 leader 信息
        assert [cell.value for cell in wk["users"]["F"][2:]] == [
            "",
            "zhangsan",
            "zhangsan",
            "lisi",
            "zhaoliu",
            "lisi, wangwu",
            "wangwu",
            "wangwu, maiba",
            "lushi",
            "lushi",
            "",
        ]

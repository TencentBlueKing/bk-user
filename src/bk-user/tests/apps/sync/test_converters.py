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
from bkuser.apps.data_source.constants import FieldMappingOperation
from bkuser.apps.data_source.data_models import DataSourceUserFieldMapping
from bkuser.apps.sync.context import TaskLogger
from bkuser.apps.sync.converters import DataSourceUserConverter
from bkuser.plugins.models import RawDataSourceUser

pytestmark = pytest.mark.django_db


class TestDataSourceUserConverter:
    """测试将 RawDataSourceUser 转换成 DataSourceUser 对象"""

    @pytest.fixture()
    def logger(self) -> TaskLogger:
        return TaskLogger()

    def test_get_field_mapping_from_data_source(self, bare_general_data_source, logger):
        bare_general_data_source.field_mapping = [
            {
                "source_field": "username",
                "mapping_operation": FieldMappingOperation.DIRECT,
                "target_field": "username",
            },
            {
                "source_field": "full_name",
                "mapping_operation": FieldMappingOperation.DIRECT,
                "target_field": "full_name",
            },
        ]
        bare_general_data_source.save()

        assert DataSourceUserConverter(bare_general_data_source, logger).field_mapping == [
            DataSourceUserFieldMapping(
                source_field="username",
                mapping_operation=FieldMappingOperation.DIRECT,
                target_field="username",
            ),
            DataSourceUserFieldMapping(
                source_field="full_name",
                mapping_operation=FieldMappingOperation.DIRECT,
                target_field="full_name",
            ),
        ]

    def test_get_field_mapping_from_tenant_user_fields(
        self, bare_local_data_source, tenant_user_custom_fields, logger
    ):
        assert DataSourceUserConverter(bare_local_data_source, logger).field_mapping == [
            DataSourceUserFieldMapping(source_field=f, mapping_operation=FieldMappingOperation.DIRECT, target_field=f)
            for f in ["username", "full_name", "email", "phone", "phone_country_code", "age", "gender", "region"]
        ]

    def test_convert_case_1(self, bare_local_data_source, tenant_user_custom_fields, logger):
        raw_zhangsan = RawDataSourceUser(
            code="zhangsan",
            properties={
                "username": "zhangsan",
                "full_name": "张三",
                "email": "zhangsan@m.com",
                "phone": "13512345671",
                "age": "18",
                "region": "beijing",
            },
            leaders=[],
            departments=["company"],
        )

        zhangsan = DataSourceUserConverter(bare_local_data_source, logger).convert(raw_zhangsan)
        assert zhangsan.code == "zhangsan"
        assert zhangsan.username == "zhangsan"
        assert zhangsan.full_name == "张三"
        assert zhangsan.email == "zhangsan@m.com"
        assert zhangsan.phone == "13512345671"
        assert zhangsan.phone_country_code == "86"
        assert zhangsan.extras == {"age": "18", "gender": "male", "region": "beijing"}

    def test_convert_case_2(self, bare_local_data_source, tenant_user_custom_fields, logger):
        raw_lisi = RawDataSourceUser(
            code="lisi",
            properties={
                "username": "lisi",
                "full_name": "李四",
                "email": "lisi@m.com",
                "phone": "13512345672",
                "phone_country_code": "63",
                "age": "28",
                "gender": "female",
            },
            leaders=["zhangsan"],
            departments=["dept_a", "center_aa"],
        )

        lisi = DataSourceUserConverter(bare_local_data_source, logger).convert(raw_lisi)
        assert lisi.code == "lisi"
        assert lisi.username == "lisi"
        assert lisi.full_name == "李四"
        assert lisi.email == "lisi@m.com"
        assert lisi.phone == "13512345672"
        assert lisi.phone_country_code == "63"
        assert lisi.extras == {"age": "28", "gender": "female", "region": ""}

    def test_convert_case_not_same_field_name_mapping(self, bare_local_data_source, tenant_user_custom_fields, logger):
        raw_lisi = RawDataSourceUser(
            code="lisi",
            properties={
                "username": "lisi",
                "full_name": "李四",
                "email": "lisi@m.com",
                "phone": "13512345672",
                "phone_country_code": "63",
                "age": "28",
                "gender": "female",
                "region": "shanghai",
            },
            leaders=["zhangsan"],
            departments=["dept_a", "center_aa"],
        )

        converter = DataSourceUserConverter(bare_local_data_source, logger)
        # 修改数据以生成不同字段名映射的比较麻烦，这里采用的是直接修改 Converter 的 field_mapping 属性
        converter.field_mapping[-1].target_field = "custom_region"

        lisi = converter.convert(raw_lisi)
        assert lisi.extras == {"age": "28", "gender": "female", "custom_region": "shanghai"}

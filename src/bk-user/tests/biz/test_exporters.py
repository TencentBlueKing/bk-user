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

pytestmark = pytest.mark.django_db


class TestDataSourceExporter:
    def test_get_template(self, bare_local_data_source, tenant_user_custom_fields):
        # TODO (su) 获取模板，确认模板列名，自定义字段列
        ...

    def test_export(self, full_local_data_source, tenant_user_custom_fields):
        # 初始化数据中，是没有 extras 的值的，这里更新下，以便于验证导出器的功能
        DataSourceUser.objects.filter(data_source=full_local_data_source).update(
            extras={"age": "20", "gender": "male", "region": "guangdong"}
        )
        # TODO (su) 导出数据，确认数据准确性，特别是自定义字段

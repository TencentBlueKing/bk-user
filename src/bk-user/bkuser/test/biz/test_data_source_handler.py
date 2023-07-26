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
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.biz.data_source_handler import data_source_handler

pytestmark = pytest.mark.django_db


class TestDataSourceHandler:

    def test_default_local_data_source(self, default_tenant) -> DataSource:
        instance = data_source_handler.create_data_source(name="test_default_local_data_source", owner=default_tenant.id)
        return instance

    def test_default_local_data_source_users(self, default_local_data_source):
        test_users_data = [
            {
                "username": "fake_user_1",
                "telephone": "12345678901",
                "email": "fake_user_1@qq.com",
                "display_name": "fake_user_1",
            },
            {
                "username": "fake_user_2",
                "telephone": "12345678902",
                "email": "fake_user_2@qq.com",
                "display_name": "fake_user_2",
            },
            {
                "username": "fake_user_3",
                "telephone": "12345678903",
                "email": "fake_user_3@qq.com",
                "display_name": "fake_user_3",
            },
            {
                "username": "fake_user_4",
                "telephone": "12345678904",
                "email": "fake_user_4@qq.com",
                "display_name": "fake_user_4",
            },
        ]
        username_list = data_source_handler.create_data_source_users(
            instance=default_local_data_source, users=test_users_data
        )

        assert username_list == [item["username"] for item in test_users_data]
        assert DataSourceUser.objects.filter(data_source_id=default_local_data_source.id).exists()
        assert DataSourceUser.objects.filter(data_source_id=default_local_data_source.id).count() == len(
            test_users_data
        )
        return [
            {"id": item["id"], "username": item["username"]}
            for item in DataSourceUser.objects.filter(data_source_id=default_local_data_source.id).values(
                "id", "username"
            )
        ]

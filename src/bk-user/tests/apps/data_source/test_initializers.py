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
from bkuser.apps.data_source.initializers import LocalDataSourceIdentityInfoInitializer
from bkuser.apps.data_source.models import DataSourceUser, LocalDataSourceIdentityInfo

pytestmark = pytest.mark.django_db


class TestLocalDataSourceIdentityInfoInitializer:
    """测试本地数据源账密初始化"""

    def test_sync(self, full_local_data_source):
        """批量同步的情况"""
        LocalDataSourceIdentityInfoInitializer(full_local_data_source).initialize()
        assert (
            LocalDataSourceIdentityInfo.objects.filter(data_source=full_local_data_source).count()
            == DataSourceUser.objects.filter(data_source=full_local_data_source).count()
        )

    def test_initialize(self, full_local_data_source):
        """单个初始化的情况"""
        users = DataSourceUser.objects.filter(data_source=full_local_data_source, username__in=["zhangsan", "cck"])
        LocalDataSourceIdentityInfoInitializer(full_local_data_source).initialize(users)
        assert LocalDataSourceIdentityInfo.objects.filter(data_source=full_local_data_source).count() == 1

    def test_skip_not_local_data_source(self, full_general_data_source):
        """不是本地数据源的，同步不会生效"""
        LocalDataSourceIdentityInfoInitializer(full_general_data_source).initialize()
        assert not LocalDataSourceIdentityInfo.objects.filter(data_source=full_general_data_source).exists()

    def test_skip_not_account_password_login_data_source(self, full_local_data_source):
        """没有启用账密登录的，同步不会生效"""
        full_local_data_source.plugin_config["enable_account_password_login"] = False
        full_local_data_source.save()

        LocalDataSourceIdentityInfoInitializer(full_local_data_source).initialize()
        assert not LocalDataSourceIdentityInfo.objects.filter(data_source=full_local_data_source).exists()

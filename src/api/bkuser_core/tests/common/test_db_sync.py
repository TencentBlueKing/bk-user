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

from bkuser_core.common.db_sync import SyncModelManager, SyncModelMeta
from bkuser_core.profiles.models import Profile


class TestModelSet:
    @pytest.fixture(scope="class")
    def model_manager(self):
        class TestSyncModelMeta(SyncModelMeta):
            target_model = Profile

        class TestModelManager(SyncModelManager):
            """测试"""

        return TestModelManager(meta=TestSyncModelMeta)

    def test_short_slice(self, model_manager):
        """测试短列表切片"""
        short_list = range(1000)
        slices = model_manager.make_slices(list(short_list))
        assert len(slices) == 1
        assert len(slices[0]) == 1000

    def test_long_slice(self, model_manager):
        """测试长列表切片"""
        long_list = range(120002)
        slices = model_manager.make_slices(list(long_list))
        assert len(slices) == 121
        assert len(slices[0]) == model_manager.meta.sharding_size
        assert len(slices[1]) == model_manager.meta.sharding_size
        assert len(slices[-1]) == 2

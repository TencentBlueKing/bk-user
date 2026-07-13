# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import pytest
from bkuser.apps.data_source.models import DataSourceUsernameGenerateConfig
from bkuser.apps.data_source.transform import UsernameTransformer

pytestmark = pytest.mark.django_db


class TestUsernameTransformer:
    """测试 UsernameTransformer"""

    def test_encode_identity(self):
        transform = UsernameTransformer()
        assert transform.to_stored("zhangsan") == "zhangsan"

    def test_encode_with_prefix(self):
        transform = UsernameTransformer(prefix="corp_")
        assert transform.to_stored("zhangsan") == "corp_zhangsan"

    def test_encode_with_suffix(self):
        transform = UsernameTransformer(suffix="_ext")
        assert transform.to_stored("zhangsan") == "zhangsan_ext"

    def test_decode_identity(self):
        transform = UsernameTransformer()
        assert transform.to_raw("zhangsan") == "zhangsan"

    def test_decode_strip_prefix(self):
        transform = UsernameTransformer(prefix="corp_")
        assert transform.to_raw("corp_zhangsan") == "zhangsan"

    def test_decode_strip_suffix(self):
        transform = UsernameTransformer(suffix="_ext")
        assert transform.to_raw("zhangsan_ext") == "zhangsan"

    @pytest.mark.parametrize(
        ("prefix", "suffix"),
        [
            ("", ""),
            ("corp_", ""),
            ("", "_ext"),
        ],
    )
    def test_encode_decode_round_trip(self, prefix, suffix):
        transform = UsernameTransformer(prefix=prefix, suffix=suffix)
        original = "zhangsan"
        assert transform.to_raw(transform.to_stored(original)) == original

    def test_load_no_config(self, bare_local_data_source):
        transform = UsernameTransformer.load(bare_local_data_source.id)
        assert transform.unchanged
        assert transform.to_stored("zhangsan") == "zhangsan"

    def test_load_with_config(self, bare_local_data_source):
        DataSourceUsernameGenerateConfig.objects.create(
            data_source=bare_local_data_source,
            rule="add_affix",
            prefix="corp_",
        )
        transform = UsernameTransformer.load(bare_local_data_source.id)
        assert not transform.unchanged
        assert transform.to_stored("zhangsan") == "corp_zhangsan"

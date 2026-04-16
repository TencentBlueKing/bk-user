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
from bkuser.apps.data_source.constants import DataSourceUsernameGenerateRule
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.biz.data_source import DataSourceUsernameHandler

pytestmark = pytest.mark.django_db


def update_username_generate_config(data_source, *, rule, prefix="", suffix=""):
    cfg = data_source.username_generate_config
    cfg.rule = rule
    cfg.prefix = prefix
    cfg.suffix = suffix
    cfg.save(update_fields=["rule", "prefix", "suffix", "updated_at"])


class TestDataSourceUsernameHandler:
    """测试 DataSourceUsernameHandler"""

    def test_generate_keep_original(self, bare_local_data_source):
        assert DataSourceUsernameHandler.generate(bare_local_data_source, "zhangsan") == "zhangsan"

    def test_generate_add_affix(self, bare_local_data_source):
        update_username_generate_config(
            bare_local_data_source,
            rule=DataSourceUsernameGenerateRule.ADD_AFFIX,
            prefix="corp_",
        )
        assert DataSourceUsernameHandler.generate(bare_local_data_source, "zhangsan") == "corp_zhangsan"

        update_username_generate_config(
            bare_local_data_source,
            rule=DataSourceUsernameGenerateRule.ADD_AFFIX,
            suffix="_ext",
        )
        assert DataSourceUsernameHandler.generate(bare_local_data_source, "zhangsan") == "zhangsan_ext"

    def test_parse_keep_original(self, bare_local_data_source):
        assert DataSourceUsernameHandler.parse(bare_local_data_source, "zhangsan") == "zhangsan"

    def test_parse_strip_prefix(self, bare_local_data_source):
        update_username_generate_config(
            bare_local_data_source,
            rule=DataSourceUsernameGenerateRule.ADD_AFFIX,
            prefix="corp_",
        )

        assert DataSourceUsernameHandler.parse(bare_local_data_source, "corp_zhangsan") == "zhangsan"

    @pytest.mark.parametrize(
        ("prefix", "suffix"),
        [
            ("", ""),
            ("corp_", ""),
            ("", "_ext"),
        ],
    )
    def test_generate_and_parse_round_trip(self, bare_local_data_source, prefix, suffix):
        """generate 和 parse 互逆"""
        rule = (
            DataSourceUsernameGenerateRule.ADD_AFFIX
            if (prefix or suffix)
            else DataSourceUsernameGenerateRule.KEEP_ORIGINAL
        )
        update_username_generate_config(
            bare_local_data_source,
            rule=rule,
            prefix=prefix,
            suffix=suffix,
        )

        original = "zhangsan"
        generated = DataSourceUsernameHandler.generate(bare_local_data_source, original)
        parsed = DataSourceUsernameHandler.parse(bare_local_data_source, generated)
        assert parsed == original

    def test_is_username_affix_exists_not_exists(self, bare_local_data_source):
        assert not DataSourceUsernameHandler.is_username_affix_exists(
            bare_local_data_source.owner_tenant_id,
            "corp_",
            "",
        )

    def test_is_username_affix_exists_exists(self, bare_local_data_source):
        update_username_generate_config(
            bare_local_data_source,
            rule=DataSourceUsernameGenerateRule.ADD_AFFIX,
            prefix="corp_",
        )

        assert DataSourceUsernameHandler.is_username_affix_exists(
            bare_local_data_source.owner_tenant_id,
            "corp_",
            "",
        )

    def test_is_username_affix_exists_different_affix_not_match(self, bare_local_data_source):
        update_username_generate_config(
            bare_local_data_source,
            rule=DataSourceUsernameGenerateRule.ADD_AFFIX,
            prefix="corp_",
        )

        assert not DataSourceUsernameHandler.is_username_affix_exists(
            bare_local_data_source.owner_tenant_id,
            "other_",
            "",
        )

    def test_is_username_exists_not_exists(self, bare_local_data_source):
        assert not DataSourceUsernameHandler.is_username_exists([bare_local_data_source.id], "nonexistent")

    def test_is_username_exists_exists(self, bare_local_data_source):
        DataSourceUser.objects.create(
            data_source=bare_local_data_source,
            code="u1",
            username="zhangsan",
            full_name="张三",
        )

        assert DataSourceUsernameHandler.is_username_exists([bare_local_data_source.id], "zhangsan")

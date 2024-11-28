# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
from bkuser.plugins.ldap.utils import has_parent_child_dn_relation


@pytest.mark.parametrize(
    ("dns", "expected"),
    [
        # 正常的情况
        (
            [
                "ou=center_aa,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
                "ou=group_aba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
                "ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
            ],
            False,
        ),
        # 正常的情况（等长）
        (
            [
                "ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
                "ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
            ],
            False,
        ),
        # 有后缀的情况
        (
            [
                "ou=company,dc=bk,dc=example,dc=com",
                "ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
                "ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
            ],
            True,
        ),
        # 重复的情况
        (
            [
                "ou=company,dc=bk,dc=example,dc=com",
                "ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
                "ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
            ],
            True,
        ),
    ],
)
def test_has_parent_child_dn_relation(dns, expected):
    assert has_parent_child_dn_relation(dns) == expected

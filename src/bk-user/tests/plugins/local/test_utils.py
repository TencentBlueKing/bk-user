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
from bkuser.plugins.local.utils import gen_code


@pytest.mark.parametrize(
    ("raw", "excepted"),
    [
        ("", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        ("公司", "e06ff957ed48e868a41b7e7e4460ce371e398108db542cf1cd1d61795b83e647"),
        ("公司/部门A", "2da9c820170b44354632bd3fe26ad09f4836b5977d2f6a5ff20afe7b143ac1e1"),
        ("公司/部门A/中心AA", "63986fb4ef27820413deb3f7c57cc36aef2ea898f03d8355e854d73b5c14e09c"),
        ("公司/部门A/中心AA/小组AAA ", "e75be6462a8ff8b9b843b3c2e419db455b4477023f98941508bc19cfa3982ec0"),
    ],
)
def test_gen_code(raw, excepted):
    # 重要：如果该单元测试挂了，说明修改了本地数据源部门的 Code 的生成规则
    # 该行为会导致新同步的数据，无法与 DB 中的数据匹配上，将会触发数据重建！！！
    assert gen_code(raw) == excepted

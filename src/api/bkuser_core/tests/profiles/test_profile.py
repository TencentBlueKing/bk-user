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

from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.tests.utils import make_simple_profile

pytestmark = pytest.mark.django_db


class TestProfile:
    def test_is_normal(
        self,
    ):
        profile = make_simple_profile("faker")
        assert profile.is_normal

        profile.enabled = False
        assert not profile.is_normal

        # 删除
        profile.enable()
        profile.delete()
        assert not profile.is_normal

        abnormal_status = [ProfileStatus.LOCKED.value, ProfileStatus.DISABLED.value, ProfileStatus.EXPIRED.value]
        for status in abnormal_status:
            profile.enable()
            profile.status = status
            assert not profile.is_normal

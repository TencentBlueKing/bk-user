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
import time

import pytest

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.plugins.base import Syncer
from bkuser_core.categories.plugins.plugin import DataSourcePlugin
from bkuser_core.user_settings.models import Setting, SettingMeta

pytestmark = pytest.mark.django_db


class TestPlugin:
    class FakeSyncerCls(Syncer):
        """Fake Syncer Class"""

    @pytest.fixture
    def plugin(self) -> DataSourcePlugin:
        return DataSourcePlugin(
            name="test",
            syncer_cls=self.FakeSyncerCls,
            login_handler_cls=None,
            allow_client_write=True,
            category_type="test",
        )

    @pytest.fixture
    def test_category(self) -> ProfileCategory:
        return ProfileCategory.objects.create(type="test", domain="test.com")

    @pytest.mark.parametrize(
        "settings,expected",
        [
            (
                {
                    "some-key": {"default": "some-default", "example": "some-example"},
                    "other-key": {"namespace": "foo", "region": "bar", "default": "qqq"},
                },
                {
                    "metas": [
                        {"key": "other-key", "default": "qqq", "example": "", "region": "bar", "namespace": "foo"},
                        {
                            "key": "some-key",
                            "default": "some-default",
                            "example": "some-example",
                            "region": "default",
                            "namespace": "general",
                        },
                    ],
                    "instances": [
                        {"meta__key": "other-key", "value": "qqq"},
                        {"meta__key": "some-key", "value": "some-default"},
                    ],
                },
            ),
            (
                {
                    "some-key": {"default": None, "example": "some-example"},
                },
                {
                    "metas": [
                        {
                            "key": "some-key",
                            "default": None,
                            "example": "some-example",
                            "region": "default",
                            "namespace": "general",
                        },
                    ],
                    "instances": [],
                },
            ),
        ],
    )
    def test_load_settings(self, plugin, test_category, settings, expected):
        """test load settings"""

        for key, meta_info in settings.items():
            plugin.init_settings(key, meta_info, {test_category.id: True})

        assert (
            list(
                SettingMeta.objects.filter(category_type="test").values(
                    "key", "default", "example", "region", "namespace"
                )
            )
            == expected["metas"]
        )
        assert (
            list(Setting.objects.filter(category=test_category).values("meta__key", "value")) == expected["instances"]
        )

    def test_load_no_update(self, plugin, test_category):
        """test load settings without updating"""
        meta = SettingMeta.objects.create(category_type="test", key="foo", region="a", namespace="b", default="wasd")
        update_time = meta.update_time

        time.sleep(0.1)
        plugin.init_settings("foo", {"region": "a", "namespace": "b", "default": "wasd"}, {test_category.id: True})
        new_update_time = SettingMeta.objects.get(category_type="test", key="foo", namespace="b").update_time

        assert update_time == new_update_time

        # region 可以被修改
        time.sleep(0.1)
        plugin.init_settings("foo", {"region": "www", "namespace": "b"}, {test_category.id: True})
        meta = SettingMeta.objects.get(category_type="test", key="foo", namespace="b")
        assert update_time != meta.update_time
        assert meta.region == "www"

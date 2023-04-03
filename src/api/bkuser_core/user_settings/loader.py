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
from dataclasses import dataclass, field

from .models import GlobalSettings, Setting
from bkuser_core.user_settings.exceptions import SettingHasBeenDisabledError


@dataclass
class ConfigProvider:
    """配置提供者"""

    category_id: int
    _config: dict = field(default_factory=dict)

    def __post_init__(self):
        self._refresh_config()

    def _refresh_config(self):
        settings = Setting.objects.prefetch_related("meta").filter(category_id=self.category_id)
        self._raws = {x.meta.key: x for x in settings}
        self._config = {x.meta.key: x.value for x in settings}

    def get(self, k, d=None):
        if k in self._raws and not self._raws.get(k).enabled:
            raise SettingHasBeenDisabledError(k)

        return self._config.get(k, d)

    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        _raw = self._raws[key]
        _raw.value = value
        _raw.save(update_fields=["value"])

        self._refresh_config()
        return


@dataclass
class GlobalConfigProvider:
    namespace: str
    _config: dict = field(default_factory=dict)

    def __post_init__(self):
        self._refresh_config()

    def _refresh_config(self):
        global_settings = GlobalSettings.objects.filter(namespace=self.namespace)
        self._raw = {setting.key: setting for setting in global_settings}
        self._config = {x.key: x.value for x in global_settings}

    def get(self, key):
        if key in self._raw and not self._raw.get(key).enabled:
            raise SettingHasBeenDisabledError(key)
        return self._config.get(key)

    def __getitem__(self, key):
        return self._config[key]

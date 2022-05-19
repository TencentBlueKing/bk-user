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
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from bkuser_shell.account.sites.default import ConfFixture as default_fixture


class _ConfFixture:
    def __init__(self, fixture_module):
        # store the module
        self._fixture = import_string(fixture_module)

    def __getattr__(self, name):
        # first, site fixture
        if hasattr(self._fixture, name):
            return getattr(self._fixture, name)

        # next, default fixture
        if hasattr(default_fixture, name):
            setting = getattr(default_fixture, name)
            if setting is None:
                raise ImproperlyConfigured(
                    "Requested %s, but ConfFixture are not configured. "
                    "You must set options in ConfFixture in right site.conf.py" % (name)
                )
            return setting

        raise KeyError("%s not exist" % name)


ConfFixture = _ConfFixture("bkuser_shell.account.sites.conf.ConfFixture")

AUTH_USER_MODEL = "account.User"

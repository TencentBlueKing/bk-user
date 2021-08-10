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
from typing import TYPE_CHECKING

from bkuser_core.user_settings.models import Setting, SettingMeta

if TYPE_CHECKING:
    from bkuser_core.categories.models import ProfileCategory


def make_default_settings(category: "ProfileCategory"):
    """创建默认配置"""
    all_metas = SettingMeta.objects.filter(category_type=category.type)

    for meta in all_metas:
        Setting.objects.create(meta=meta, category_id=category.id, value=meta.default or meta.example)

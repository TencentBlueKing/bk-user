"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from typing import Dict

from django.core.cache import caches

from .models import DynamicFieldInfo

LOCAL_CACHE_KEY_DEFAULT_EXTRAS_VALUES = "profile:extras:default"


def get_extras_default_from_local_cache() -> Dict:
    """
    change the performance for now, should refactor it
    """
    cache = caches["locmem"]

    values = cache.get(LOCAL_CACHE_KEY_DEFAULT_EXTRAS_VALUES)
    if values is not None:
        return values

    values = DynamicFieldInfo.objects.get_extras_default_values()
    cache.set(LOCAL_CACHE_KEY_DEFAULT_EXTRAS_VALUES, values, 1 * 60)
    return values

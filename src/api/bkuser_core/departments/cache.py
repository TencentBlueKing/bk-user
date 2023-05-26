"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from typing import Tuple

from django.core.cache import caches

LOCAL_CACHE_KEY_DEPARTMENT_FULL_NAME_PREFIX = "dept:full_name"
LOCAL_CACHE_KEY_DEPARTMENT_HAS_CHILDREN_PREFIX = "dept:has_children"


# pylint: disable=function-name-too-long
def get_department_full_name_from_local_cache(department_id: int) -> Tuple[bool, str]:
    if not department_id:
        return False, ""

    key = f"{LOCAL_CACHE_KEY_DEPARTMENT_FULL_NAME_PREFIX}:{department_id}"
    cache = caches["locmem"]
    full_name = cache.get(key)
    if full_name is not None:
        return True, full_name

    return False, ""


# pylint: disable=function-name-too-long
def set_department_full_name_to_local_cache(department_id: int, full_name: str, timeout: int = 5) -> None:
    if not department_id:
        return

    key = f"{LOCAL_CACHE_KEY_DEPARTMENT_FULL_NAME_PREFIX}:{department_id}"
    cache = caches["locmem"]
    cache.set(key, full_name, timeout)


# pylint: disable=function-name-too-long
def get_department_has_children_from_local_cache(department_id: int) -> Tuple[bool, bool]:
    if not department_id:
        return False, False

    key = f"{LOCAL_CACHE_KEY_DEPARTMENT_HAS_CHILDREN_PREFIX}:{department_id}"
    # NOTE: if you want to change to other backend, should make sure the unpickled value type is bool!
    cache = caches["locmem"]
    # NOTE: got bool here! the cache locmem based on pickle
    has_children = cache.get(key)
    if has_children is not None:
        return True, has_children

    return False, False


# pylint: disable=function-name-too-long
def set_department_has_children_to_local_cache(department_id: int, has_children: bool, timeout: int = 5) -> None:
    if not department_id:
        return

    key = f"{LOCAL_CACHE_KEY_DEPARTMENT_HAS_CHILDREN_PREFIX}:{department_id}"
    cache = caches["locmem"]
    cache.set(key, has_children, timeout)

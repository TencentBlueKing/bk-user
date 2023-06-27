"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.core.cache import caches

from .models import ProfileCategory

LOCAL_CACHE_KEY_DEFAULT_CATEGORY_ID = "cate:id"
LOCAL_CACHE_KEY_DEFAULT_CATEGORY_DOMAIN = "cate:domain"


# pylint: disable=function-name-too-long
def get_default_category_id_from_local_cache() -> int:
    """
    change the performance for now, should refactor it
    """
    cache = caches["locmem"]

    category_id = cache.get(LOCAL_CACHE_KEY_DEFAULT_CATEGORY_ID)
    if category_id is not None:
        return category_id

    category_id = ProfileCategory.objects.get_default().id
    cache.set(LOCAL_CACHE_KEY_DEFAULT_CATEGORY_ID, category_id, 1 * 60)
    return category_id


# pylint: disable=function-name-too-long
def get_default_category_domain_from_local_cache() -> str:
    cache = caches["locmem"]

    domain = cache.get(LOCAL_CACHE_KEY_DEFAULT_CATEGORY_DOMAIN)
    if domain is not None:
        return domain

    domain = ProfileCategory.objects.get_default().domain
    cache.set(LOCAL_CACHE_KEY_DEFAULT_CATEGORY_DOMAIN, domain, 1 * 60)
    return domain


# TODO: clean the cache after update the default category

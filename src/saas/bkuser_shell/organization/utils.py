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
import logging
from functools import reduce

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http.request import HttpRequest

logger = logging.getLogger(__name__)


def batch_expand_extra_fields(extra_fields, profiles):
    """批量展开"""
    expanded_profiles = []
    for profile in profiles:
        try:
            expanded_profiles.append(expand_extra_fields(extra_fields, profile))
        except Exception:  # pylint: disable=broad-except
            logger.exception("expand profile<%s> extras failed", profile)
            expanded_profiles.append(profile)

    return expanded_profiles


def expand_extra_fields(extra_fields, profile):
    """将 profile extra value 展开，作为 profile 字段展示"""
    available_values = profile.pop("extras")

    # TODO: 建模, 建模, 建模
    for extra_field in extra_fields:
        # 没有设置额外字段，则使用字段默认值
        profile[extra_field["name"]] = extra_field["default"]
        if not available_values:
            continue

        # 兼容旧的数据格式
        if isinstance(available_values, list):
            available_values = {x["key"]: x["value"] for x in available_values}

        profile[extra_field["name"]] = available_values.get(extra_field["name"])

    return profile


def get_options_values_by_key(options: list, keys: list):
    if not options:
        return None

    values = []
    for k in keys:
        for pair in options:
            if pair[0] == k:
                values.append(pair[1])

    return values


def url_path_join(parts: list) -> str:
    """拼接 url path"""
    return reduce(lambda a, b: a.rstrip("/") + "/" + b.lstrip("/"), parts) if parts else ""


def get_default_logo_url(request: HttpRequest):
    """获取默认头像"""
    return request.build_absolute_uri(
        url_path_join([settings.SITE_URL, staticfiles_storage.url(settings.DEFAULT_LOGO_URL)])
    )

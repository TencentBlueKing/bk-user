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

from django.conf import settings

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile
from bkuser_core.user_settings.models import SettingMeta

logger = logging.getLogger(__name__)


# FIXME: get it from request.user.username after merge saas into api
def get_username(request) -> str:
    username = request.META.get(settings.OPERATOR_HEADER, None)
    if not username:
        raise error_codes.USERNAME_MISSING
    return username


# FIXME: add memory cache here
def get_category_display_name_map():
    return dict(ProfileCategory.objects.values_list("id", "display_name").all())


# FIXME: add memory cache here
def get_default_category_id():
    return ProfileCategory.objects.get_default().id


def get_department(department_id: int) -> Department:
    try:
        return Department.objects.get(id=department_id)
    except Exception:
        logger.exception("cannot find department: %s", department_id)
        raise error_codes.CANNOT_FIND_DEPARTMENT


def get_category(category_id: int) -> ProfileCategory:
    try:
        return ProfileCategory.objects.get(id=category_id)
    except Exception:
        logger.exception("cannot find category: %s", category_id)
        raise error_codes.CANNOT_FIND_CATEGORY


def get_profile(profile_id: int) -> Profile:
    try:
        return Profile.objects.get(id=profile_id)
    except Exception:
        logger.exception("cannot find profile: %s", profile_id)
        raise error_codes.CANNOT_FIND_PROFILE


def list_setting_metas(category_type: str, region: str, namespace: str) -> list:
    """
    List setting metas.
    """
    queryset = SettingMeta.objects.filter(category_type=category_type)
    if region:
        queryset = queryset.filter(region=region)
    if namespace:
        queryset = queryset.filter(namespace=namespace)
    return queryset.all()

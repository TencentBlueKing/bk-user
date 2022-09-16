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
from typing import Dict

from django.conf import settings

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.password import PasswordValidator
from bkuser_core.profiles.utils import check_former_passwords
from bkuser_core.user_settings.exceptions import SettingHasBeenDisabledError
from bkuser_core.user_settings.loader import ConfigProvider
from bkuser_core.user_settings.models import SettingMeta

logger = logging.getLogger(__name__)


# FIXME: get it from request.user.username after merge saas into api
def get_operator(request) -> str:
    """
    NOTE: the `operator` should be the username with domain
    - default category: operator = username
    - not default category:  operator = username@domain
    """
    operator = request.META.get(settings.OPERATOR_HEADER, None)
    if not operator:
        raise error_codes.USERNAME_MISSING
    return operator


# FIXME: add memory cache here
def get_category_display_name_map() -> Dict[int, str]:
    return dict(ProfileCategory.objects.values_list("id", "display_name").all())


# FIXME: add memory cache here
def get_default_category_id() -> int:
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


def validate_password(profile: Profile, pending_password: str) -> None:
    config_loader = ConfigProvider(category_id=profile.category_id)
    try:
        max_password_history = config_loader.get("max_password_history", settings.DEFAULT_MAX_PASSWORD_HISTORY)
        if check_former_passwords(profile, pending_password, int(max_password_history)):
            raise error_codes.PASSWORD_DUPLICATED.f(max_password_history=max_password_history)
    except SettingHasBeenDisabledError:
        logger.info("category<%s> has disabled checking password", profile.category_id)

    PasswordValidator(
        min_length=int(config_loader["password_min_length"]),
        max_length=settings.PASSWORD_MAX_LENGTH,
        include_elements=config_loader["password_must_includes"],
        exclude_elements_config=config_loader["exclude_elements_config"],
    ).validate(pending_password)


def is_filter_means_any(ft) -> bool:
    return ft.deconstruct() == ("django.db.models.Q", (("pk__in", []),), {"_negated": True})

# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
import re
from typing import Any, Dict, List, Set

from django.conf import settings
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.sync.constants import DATA_SOURCE_USERNAME_REGEX, EMAIL_REGEX
from bkuser.biz.validators import validate_type_and_convert_field_data
from bkuser.common.validators import validate_phone_with_country_code


def validate_user_create_data(user_info: Dict[str, Any], data_source: DataSource) -> List[str]:
    """校验单个用户创建数据，返回错误列表"""
    errors: List[str] = []
    user_id = user_info.get("id", "?")

    username = user_info.get("username", "")
    if not username:
        errors.append(f"user [{user_id}]: username is required")
    elif not re.fullmatch(DATA_SOURCE_USERNAME_REGEX, username):
        errors.append(
            f"user [{user_id}]: username [{username}] not match pattern {DATA_SOURCE_USERNAME_REGEX.pattern}"
        )

    full_name = user_info.get("full_name", "")
    if not full_name:
        errors.append(f"user [{user_id}]: full_name is required")

    email = user_info.get("email", "")
    if email and not re.fullmatch(EMAIL_REGEX, email):
        errors.append(f"user [{user_id}]: email [{email}] format invalid")

    phone = user_info.get("phone", "")
    if phone:
        country_code = user_info.get("phone_country_code") or settings.DEFAULT_PHONE_COUNTRY_CODE
        try:
            validate_phone_with_country_code(phone, country_code)
        except ValueError as e:
            errors.append(f"user [{user_id}]: {e}")

    return errors


def validate_user_update_data(user_info: Dict[str, Any]) -> List[str]:  # noqa: C901
    """校验单个用户更新数据，返回错误列表"""
    errors: List[str] = []
    user_id = user_info.get("id", "?")

    if "username" in user_info:
        username = user_info["username"]
        if not username:
            errors.append(f"user [{user_id}]: username cannot be empty")
        elif not re.fullmatch(DATA_SOURCE_USERNAME_REGEX, username):
            errors.append(
                f"user [{user_id}]: username [{username}] not match pattern {DATA_SOURCE_USERNAME_REGEX.pattern}"
            )

    if "full_name" in user_info and not user_info["full_name"]:
        errors.append(f"user [{user_id}]: full_name cannot be empty")

    if "email" in user_info:
        email = user_info["email"]
        if email and not re.fullmatch(EMAIL_REGEX, email):
            errors.append(f"user [{user_id}]: email [{email}] format invalid")

    if "phone" in user_info:
        phone = user_info["phone"]
        if phone:
            country_code = user_info.get("phone_country_code") or settings.DEFAULT_PHONE_COUNTRY_CODE
            try:
                validate_phone_with_country_code(phone, country_code)
            except ValueError as e:
                errors.append(f"user [{user_id}]: {e}")

    return errors


def validate_user_extras(
    user_id: str,
    extras: Dict[str, Any],
    custom_fields,
    data_source_id: int,
    data_source_user_id: int | None = None,
) -> List[str]:
    """校验 extras 自定义字段，返回错误列表"""
    errors: List[str] = []

    for field in custom_fields:
        if field.name not in extras:
            continue

        value = extras[field.name]

        # 类型校验与转换
        try:
            value = validate_type_and_convert_field_data(field, value)
        except ValidationError as e:
            errors.append(f"user [{user_id}]: extras.{field.name} - {e.detail[0]}")
            continue

        # 必填性校验
        if field.required and value in ["", None]:
            errors.append(f"user [{user_id}]: extras.{field.name} is required")
            continue

        # 唯一性校验
        if field.unique and value not in ["", None]:
            queryset = DataSourceUser.objects.filter(data_source_id=data_source_id, **{f"extras__{field.name}": value})
            if data_source_user_id:
                queryset = queryset.exclude(id=data_source_user_id)
            if queryset.exists():
                errors.append(f"user [{user_id}]: extras.{field.name} value [{value}] is not unique")

        extras[field.name] = value

    return errors


def validate_create_users_unique(
    users_data: List[Dict[str, Any]],
    data_source: DataSource,
) -> List[str]:
    """校验批量创建用户的 id 和 username 唯一性"""
    errors: List[str] = []

    # 批次内 id 重复检查
    ids = [u["id"] for u in users_data]
    seen_ids: Set[str] = set()
    for uid in ids:
        if uid in seen_ids:
            errors.append(f"duplicate id [{uid}] in request")
        seen_ids.add(uid)

    # 批次内 username 重复检查
    usernames = [u["username"] for u in users_data if u.get("username")]
    seen_usernames: Set[str] = set()
    for uname in usernames:
        if uname in seen_usernames:
            errors.append(f"duplicate username [{uname}] in request")
        seen_usernames.add(uname)

    # 与数据库已有数据的重复检查
    existing_codes = set(
        DataSourceUser.objects.filter(data_source=data_source, code__in=ids).values_list("code", flat=True)
    )
    errors.extend(f"user id [{code}] already exists in data source" for code in existing_codes)

    existing_usernames = set(
        DataSourceUser.objects.filter(data_source=data_source, username__in=usernames).values_list(
            "username", flat=True
        )
    )
    errors.extend(f"username [{uname}] already exists in data source" for uname in existing_usernames)

    return errors


def validate_update_users_unique(
    users_data: List[Dict[str, Any]],
    data_source: DataSource,
) -> List[str]:
    """校验批量更新用户中 username 变更的唯一性"""
    errors: List[str] = []

    users_with_new_username = [(u["id"], u["username"]) for u in users_data if "username" in u]
    if not users_with_new_username:
        return errors

    # 批次内 username 重复检查
    new_usernames = [uname for _, uname in users_with_new_username]
    seen: Set[str] = set()
    for uname in new_usernames:
        if uname in seen:
            errors.append(f"duplicate username [{uname}] in request")
        seen.add(uname)

    # 与数据库已有数据的重复检查（排除自身）
    codes_to_update = [uid for uid, _ in users_with_new_username]
    existing_users = DataSourceUser.objects.filter(data_source=data_source, username__in=new_usernames).exclude(
        code__in=codes_to_update
    )
    errors.extend(f"username [{u.username}] already exists in data source" for u in existing_users)

    return errors


def raise_if_errors(errors: List[str]) -> None:
    """如有错误则抛出 ValidationError"""
    if errors:
        raise ValidationError(errors)

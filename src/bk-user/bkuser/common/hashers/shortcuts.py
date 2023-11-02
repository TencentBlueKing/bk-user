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
from django.conf import settings
from django.contrib.auth.hashers import check_password as dj_check_password
from django.contrib.auth.hashers import make_password as dj_make_password


def check_password(raw_password: str, encrypted_password: str) -> bool:
    """Return a boolean of whether the raw_password was correct. Handles hashing formats behind the scenes."""
    return dj_check_password(raw_password, encrypted_password, preferred=settings.PASSWORD_ENCRYPT_ALGORITHM)


def make_password(raw_password: str, salt: str | None = None) -> str:
    """Return a securely generated hash of the given plain-text password."""
    return dj_make_password(raw_password, salt=salt, hasher=settings.PASSWORD_ENCRYPT_ALGORITHM)

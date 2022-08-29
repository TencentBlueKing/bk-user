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

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes


# FIXME: get it from request.user.username after merge saas into api
def get_username(request) -> str:
    username = request.META.get(settings.OPERATOR_HEADER, None)
    if not username:
        raise error_codes.USERNAME_MISSING
    return username


# FIXME: add memory cache here
def get_category_display_name_map():
    return dict(ProfileCategory.objects.values_list('id', 'display_name').all())

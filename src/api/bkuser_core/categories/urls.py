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
from django.urls.conf import re_path

from . import views
from bkuser_core.apis.v2.constants import LOOKUP_FIELD_NAME

PVAR_PROFILE_ID = r"(?P<%s>[a-z0-9-]+)" % LOOKUP_FIELD_NAME


# FIXME: 统计调用量后, 删除

urlpatterns = [
    re_path(
        r"^api/v2/categories/$",
        views.CategoryViewSet.as_view(
            {
                # NOTE: login used
                "get": "list",
                # TODO: saas not used
                "post": "create",
            }
        ),
        name="categories",
    ),
    re_path(
        r"^api/v2/categories/%s/$" % PVAR_PROFILE_ID,
        views.CategoryViewSet.as_view(
            {
                # TODO: saas not used
                "get": "retrieve",
                # TODO: saas not used
                "put": "update",
                # TODO: saas not used
                "patch": "partial_update",
            }
        ),
        name="categories.action",
    ),
]

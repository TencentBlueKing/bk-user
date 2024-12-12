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
from django.urls import re_path

from . import views

urlpatterns = [
    # ============ Category ==============
    re_path(
        r"^api/iam/v1/categories/$",
        views.CategoryIAMViewSet.as_view({"post": "distribution"}),
        name="iam_categories",
    ),
    # ============ Field ==============
    re_path(
        r"^api/iam/v1/fields/$",
        views.DynamicFieldIAMViewSet.as_view({"post": "distribution"}),
        name="iam_fields",
    ),
    # ============ Department ==============
    re_path(
        r"^api/iam/v1/departments/$",
        views.DepartmentIAMViewSet.as_view({"post": "distribution"}),
        name="iam_departments",
    ),
]

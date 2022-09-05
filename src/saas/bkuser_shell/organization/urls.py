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
from django.conf.urls import url

from .views.departments import DepartmentViewSet
from .views.misc import SearchViewSet
from .views.profiles import ProfilesViewSet

PVAR_DEPARTMENT_ID = r"(?P<department_id>[a-z0-9-]+)"
PVAR_PROFILE_ID = r"(?P<profile_id>[a-z0-9-]+)"
PVAR_CATEGORY_ID = r"(?P<category_id>[\d]+)"

PVAR_ANOTHER_DEPARTMENT_ID = r"(?P<another_department_id>[a-z0-9-]+)"


urlpatterns = [
    ######################
    # Department related #
    ######################
    url(
        r"^api/v2/departments/%s/profiles/$" % PVAR_DEPARTMENT_ID,
        DepartmentViewSet.as_view({"get": "get_profiles", "post": "add_profiles"}),
        name="department.profiles",
    ),
    url(r"^api/v2/departments/$", DepartmentViewSet.as_view({"get": "list", "post": "create"}), name="departments"),
    url(
        r"^api/v2/categories/%s/departments/search/$" % PVAR_CATEGORY_ID,
        DepartmentViewSet.as_view({"get": "search_in_category"}),
        name="departments.search_in_category",
    ),
    url(
        r"^api/v2/departments/%s/$" % PVAR_DEPARTMENT_ID,
        DepartmentViewSet.as_view({"get": "retrieve", "delete": "delete", "patch": "update"}),
        name="department.actions",
    ),
    url(
        r"^api/v2/departments/%s/switch_order/%s/$" % (PVAR_DEPARTMENT_ID, PVAR_ANOTHER_DEPARTMENT_ID),
        DepartmentViewSet.as_view({"patch": "switch_order"}),
        name="department.switch_order",
    ),
    ###################
    # Profile related #
    ###################
    url(
        r"^api/v2/profiles/$",
        ProfilesViewSet.as_view({"post": "create"}),
        name="profiles",
    ),
    url(
        r"^api/v2/categories/%s/profiles/$" % PVAR_CATEGORY_ID,
        ProfilesViewSet.as_view({"get": "list"}),
        name="profiles",
    ),
    url(
        r"^api/v2/profiles/%s/$" % PVAR_PROFILE_ID,
        ProfilesViewSet.as_view({"get": "retrieve", "patch": "update"}),
        name="profiles.actions",
    ),
    url(
        r"^api/v2/profiles/%s/restoration/$" % PVAR_PROFILE_ID,
        ProfilesViewSet.as_view({"post": "restoration"}),
        name="profiles.restoration",
    ),
    url(
        r"^api/v2/batch/profiles/$",
        ProfilesViewSet.as_view({"patch": "multiple_update", "delete": "multiple_delete"}),
        name="profiles.batch.actions",
    ),
    ##########
    # search #
    ##########
    url(
        r"^api/v2/search/detail/$",
        SearchViewSet.as_view({"get": "search"}),
        name="profiles.login_info",
    ),
]

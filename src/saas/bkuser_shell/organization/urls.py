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


# GET /api/v2/departments/?only_enabled=false/true
# GET /api/v2/categories/1/profiles/?keyword=x&page=1&page_size=10
# GET /api/v2/departments/1/profiles/?page_size=6&page=1&recursive=true&keyword=


# /api/v2/search/detail/?keyword=xxxx&max_items=40&only_enabled=true
# /api/v2/departments/1/profiles/?page_size=6&page=1&recursive=false&keyword=
# DELETE /api/v2/batch/profiles/ [{"id":"1026"}]
# PATCH /api/v2/batch/profiles/  [{"id":1027,"departments":[1,20207]}]
# POST /api/v2/profiles/1/restoration/
# PATCH /api/v2/profiles/1027/
# {"leader":[1],"departments":[1,20207],"password_valid_days":-1,"display_name":"吴昆亮","email":"kunliangwu@tencent.com","telephone":"18128867661","iso_code":"cn","staff_status":"IN","position":0,"wx_userid":"","qq":"","staffTypeName":0,"age":null,"account_expiration_date":"2100-01-01","testa":"1"}

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

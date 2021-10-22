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
from bkuser_core.common.constants import LOOKUP_FIELD_NAME
from django.conf.urls import url

from . import views

PVAR_DEPARTMENT_ID = r"(?P<%s>[\w\-]+)" % LOOKUP_FIELD_NAME

urlpatterns = [
    url(
        r"^api/v2/departments/$",
        views.DepartmentViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="departments",
    ),
    url(
        r"^api/v2/departments/%s/$" % PVAR_DEPARTMENT_ID,
        views.DepartmentViewSet.as_view(
            {
                "get": "retrieve",
                "post": "update",
                "delete": "destroy",
                "patch": "partial_update",
            }
        ),
        name="departments.action",
    ),
    url(
        r"^api/v2/departments/%s/restoration/$" % PVAR_DEPARTMENT_ID,
        views.DepartmentViewSet.as_view(
            {
                "post": "restoration",
            }
        ),
        name="departments.restoration",
    ),
    url(
        r"^api/v2/departments/%s/ancestors/$" % PVAR_DEPARTMENT_ID,
        views.DepartmentViewSet.as_view(
            {
                "get": "get_ancestor",
            }
        ),
        name="departments.ancestors",
    ),
    url(
        r"^api/v2/departments/%s/children/$" % PVAR_DEPARTMENT_ID,
        views.DepartmentViewSet.as_view(
            {
                "get": "get_children",
            }
        ),
        name="departments.children",
    ),
    url(
        r"^api/v2/departments/%s/profiles/$" % PVAR_DEPARTMENT_ID,
        views.DepartmentViewSet.as_view({"get": "get_profiles", "post": "add_profiles"}),
        name="departments.profiles",
    ),
    #########
    # Batch #
    #########
    url(
        r"^api/v2/batch/departments/profiles/$",
        views.BatchDepartmentsViewSet.as_view(
            {
                "get": "multiple_retrieve_profiles",
            }
        ),
        name="department.batch",
    ),
    ########
    # Edge #
    ########
    url(
        r"^api/v2/edges/department_profile/$",
        views.DepartmentProfileEdgeViewSet.as_view({"get": "list"}),
        name="edge.department_profile",
    ),
    #############
    # shortcuts #
    #############
    url(
        r"^api/v2/shortcuts/departments/tops/$",
        views.DepartmentViewSet.as_view({"get": "list_tops"}),
        name="shortcuts.departments.list.tops",
    ),
]

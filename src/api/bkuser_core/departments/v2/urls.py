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

from bkuser_core.apis.v2.constants import LOOKUP_FIELD_NAME
from bkuser_core.departments.v2 import views

PVAR_DEPARTMENT_ID = r"(?P<%s>[\w\-\.]+)" % LOOKUP_FIELD_NAME

urlpatterns = [
    url(
        r"^api/v2/departments/$",
        views.DepartmentViewSet.as_view(
            {
                # NOTE: login used
                "get": "list",
                # NOTE: login used
                "post": "create",
            }
        ),
        name="departments",
    ),
    url(
        r"^api/v2/departments/%s/$" % PVAR_DEPARTMENT_ID,
        views.DepartmentViewSet.as_view(
            {
                # NOTE: login used
                "get": "retrieve",
                # NOTE: login used
                "post": "update",
                # TODO: saas removed this
                "delete": "destroy",
                # TODO: saas removed this
                "patch": "partial_update",
            }
        ),
        name="departments.action",
    ),
    url(
        r"^api/v2/departments/%s/ancestors/$" % PVAR_DEPARTMENT_ID,
        views.DepartmentViewSet.as_view(
            {
                # TODO: saas removed this
                "get": "get_ancestor",
            }
        ),
        name="departments.ancestors",
    ),
    url(
        r"^api/v2/departments/%s/children/$" % PVAR_DEPARTMENT_ID,
        views.DepartmentViewSet.as_view(
            {
                # TODO: saas removed this
                "get": "get_children",
            }
        ),
        name="departments.children",
    ),
    url(
        r"^api/v2/departments/%s/profiles/$" % PVAR_DEPARTMENT_ID,
        views.DepartmentViewSet.as_view(
            {
                # NOTE: login used
                "get": "get_profiles",
                # NOTE: login used
                "post": "add_profiles",
            }
        ),
        name="departments.profiles",
    ),
    ########
    # Edge #
    ########
    url(
        r"^api/v2/edges/department_profile/$",
        # NOTE: login used
        views.DepartmentProfileEdgeViewSet.as_view({"get": "list"}),
        name="edge.department_profile",
    ),
]

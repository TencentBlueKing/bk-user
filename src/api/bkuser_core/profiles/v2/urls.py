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

from . import views
from bkuser_core.apis.v2.constants import LOOKUP_FIELD_NAME

PVAR_PROFILE_ID = r"(?P<%s>[\w\-\@\.\$]+)" % LOOKUP_FIELD_NAME
PVAR_TOKEN = r"(?P<token>[\w]+)"

urlpatterns = [
    url(
        r"^api/v2/profiles/$",
        views.ProfileViewSet.as_view(
            {
                "get": "list",
                # TODO: saas has removed this
                "post": "create",
            }
        ),
        name="profiles",
    ),
    url(
        r"^api/v2/profiles/%s/$" % PVAR_PROFILE_ID,
        views.ProfileViewSet.as_view(
            {
                # NOTE: saas removed this
                "get": "retrieve",
                # NOTE: saas removed this
                "put": "update",
                # NOTE: saas removed this
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="profiles.action",
    ),
    url(
        r"^api/v2/profiles/%s/restoration/$" % PVAR_PROFILE_ID,
        views.ProfileViewSet.as_view(
            {
                # NOTE: saas has removed this
                "post": "restoration",
            }
        ),
        name="profiles.restoration",
    ),
    url(
        r"^api/v2/profiles/%s/departments/$" % PVAR_PROFILE_ID,
        views.ProfileViewSet.as_view(
            {
                "get": "get_departments",
            }
        ),
        name="profiles.departments",
    ),
    url(
        r"^api/v2/profiles/%s/leaders/$" % PVAR_PROFILE_ID,
        views.ProfileViewSet.as_view(
            {
                "get": "get_leaders",
            }
        ),
        name="profiles.leaders",
    ),
    url(
        r"^api/v2/profiles/%s/token/$" % PVAR_PROFILE_ID,
        views.ProfileViewSet.as_view(
            {
                "post": "generate_token",
            }
        ),
        name="profiles.generate_token",
    ),
    url(
        r"^api/v2/batch/profiles/$",
        views.BatchProfileViewSet.as_view(
            {
                "get": "multiple_retrieve",
                # TODO: saas has revmoved this
                "patch": "multiple_update",
                # TODO: saas has revmoved this
                "delete": "multiple_delete",
            }
        ),
        name="profiles.batch",
    ),
    url(
        r"^api/v2/token/%s/$" % PVAR_TOKEN,
        views.ProfileViewSet.as_view(
            {
                "get": "retrieve_by_token",
            }
        ),
        name="profiles.retrieve_by_token",
    ),
    url(
        r"^api/v2/profiles/%s/modify_password/$" % PVAR_PROFILE_ID,
        views.ProfileViewSet.as_view(
            {
                "post": "modify_password",
            }
        ),
        name="profiles.modify_password",
    ),
    ########
    # Edge #
    ########
    url(
        r"^api/v2/edges/leader/$",
        views.LeaderEdgeViewSet.as_view({"get": "list"}),
        name="edge.leader",
    ),
]

urlpatterns += [
    url(
        r"^api/v1/login/check/$",
        views.ProfileLoginViewSet.as_view({"post": "login"}),
        name="login.check",
    ),
    url(
        r"^api/v1/login/profile/$",
        views.ProfileLoginViewSet.as_view({"post": "upsert"}),
        name="login.upsert",
    ),
    url(
        r"^api/v1/login/profile/query/$",
        views.ProfileLoginViewSet.as_view({"post": "batch_query"}),
        name="login.batch_query",
    ),
]

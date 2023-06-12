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
                # NOTE: login used
                "get": "list",
                # NOTE: login used
                "post": "create",
            }
        ),
        name="profiles",
    ),
    url(
        r"^api/v2/profiles/%s/$" % PVAR_PROFILE_ID,
        views.ProfileViewSet.as_view(
            {
                # NOTE: login used
                "get": "retrieve",
                # NOTE: login used
                "put": "update",
                # TODO: saas removed this
                "patch": "partial_update",
                # TODO: saas removed this
                "delete": "destroy",
            }
        ),
        name="profiles.action",
    ),
    url(
        r"^api/v2/profiles/%s/languages/$" % PVAR_PROFILE_ID,
        views.ProfileViewSet.as_view(
            {
                # Note: This API allows all SaaS platforms to modify the language of their users
                "put": "update_language",
            }
        ),
        name="profiles.language",
    ),
    url(
        r"^api/v2/profiles/%s/departments/$" % PVAR_PROFILE_ID,
        views.ProfileViewSet.as_view(
            {
                # NOTE: login used
                "get": "get_departments",
            }
        ),
        name="profiles.departments",
    ),
    url(
        r"^api/v2/profiles/%s/leaders/$" % PVAR_PROFILE_ID,
        views.ProfileViewSet.as_view(
            {
                # TODO: saas removed this
                "get": "get_leaders",
            }
        ),
        name="profiles.leaders",
    ),
    ########
    # Edge #
    ########
    url(
        r"^api/v2/edges/leader/$",
        # NOTE: login used
        views.LeaderEdgeViewSet.as_view({"get": "list"}),
        name="edge.leader",
    ),
]

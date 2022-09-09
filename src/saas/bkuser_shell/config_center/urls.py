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

from .views import SettingsViewSet

PVAR_SETTING_ID = r"(?P<setting_id>[0-9]+)"
PVAR_CATEGORY_ID = r"(?P<category_id>[0-9]+)"
PVAR_NAMESPACE_NAME = r"(?P<namespace_name>[a-z0-9-]+)"


urlpatterns = [
    ############
    # settings #
    ############
    url(
        r"^api/v2/categories/%s/settings/$" % PVAR_CATEGORY_ID,
        SettingsViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="config_center.settings",
    ),
    # TODO: not used?
    url(
        r"^api/v2/categories/%s/settings/%s/$" % (PVAR_CATEGORY_ID, PVAR_SETTING_ID),
        SettingsViewSet.as_view(
            {
                "patch": "update",
                "delete": "delete",
            }
        ),
        name="config_center.settings.actions",
    ),
]

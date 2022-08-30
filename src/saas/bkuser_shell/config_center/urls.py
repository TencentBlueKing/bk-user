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

from .views import FieldsViewSet, SettingsNamespaceViewSet, SettingsViewSet

PVAR_FIELD_ID = r"(?P<field_id>[0-9]+)"
PVAR_SETTING_ID = r"(?P<setting_id>[0-9]+)"
NEW_PVAR_ORDER = r"(?P<new_order>[0-9]+)"
PVAR_CATEGORY_ID = r"(?P<category_id>[0-9]+)"
PVAR_MODULE_NAME = r"(?P<module_name>[a-z0-9-]+)"
PVAR_NAMESPACE_NAME = r"(?P<namespace_name>[a-z0-9-]+)"


urlpatterns = [
    ##########
    # fields #
    ##########
    url(
        r"^api/v2/fields/$",
        FieldsViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="config_center.fields",
    ),
    url(
        r"^api/v2/fields/visible/$",
        FieldsViewSet.as_view(
            {
                "patch": "update_visible",
            }
        ),
        name="config_center.fields.visible",
    ),
    url(
        r"^api/v2/fields/%s/$" % PVAR_FIELD_ID,
        FieldsViewSet.as_view(
            {
                "put": "update",
                "delete": "delete",
                "patch": "update",
            }
        ),
        name="config_center.fields.actions",
    ),
    url(
        r"^api/v2/fields/%s/order/%s/$" % (PVAR_FIELD_ID, NEW_PVAR_ORDER),
        FieldsViewSet.as_view(
            {
                "patch": "update_order",
            }
        ),
        name="config_center.fields.actions",
    ),
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
    ####################################
    # 针对 namespace 的批量 settings 操作 #
    ####################################
    url(
        r"^api/v2/categories/%s/settings/namespaces/%s/$" % (PVAR_CATEGORY_ID, PVAR_NAMESPACE_NAME),
        SettingsNamespaceViewSet.as_view({"get": "list", "post": "create", "put": "update", "delete": "delete"}),
        name="config_center.settings.namespaces",
    ),
    url(
        r"^api/v2/settings/metas/$",
        SettingsNamespaceViewSet.as_view(
            {
                "get": "list_defaults",
            }
        ),
        name="config_center.settings.namespaces.metas",
    ),
]

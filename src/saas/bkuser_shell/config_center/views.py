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
import logging

import bkuser_sdk
from . import serializers
from bkuser_global.drf_crown import inject_serializer
from bkuser_shell.apis.viewset import BkUserApiViewSet
from bkuser_shell.common.response import Response
from bkuser_shell.config_center.serializers import SettingSerializer
from bkuser_shell.proxy.proxy import BkUserApiProxy

logger = logging.getLogger(__name__)


class SettingsViewSet(BkUserApiViewSet, BkUserApiProxy):
    serializer_class = SettingSerializer

    # 这里不能通用配置, 因为retrieve/destroy等操作后台检查不支持, 也不能使用force_action_id, 后台检查会查settings
    # ACTION_ID = IAMAction.MANAGE_CATEGORY.value

    def list(self, request, *args, **kwargs):
        # in: api/v2/categories/%s/settings/
        # out: api/v1/web/categories/%s/settings/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        self.do_proxy(request, rewrite_path=api_path)

    @inject_serializer(
        body_in=serializers.CreateSettingsSerializer, out=serializers.SettingSerializer(), tags=["config_center"]
    )
    def create(self, request, category_id, validated_data):
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))
        category = api_instance.v2_categories_read(category_id)

        setting = bkuser_sdk.Setting(category=category, **validated_data)

        api_instance = bkuser_sdk.SettingsApi(self.get_api_client_by_request(request))
        return api_instance.v2_settings_create(body=setting)

    @inject_serializer(
        query_in=serializers.UpdateSettingSerializer(), out=serializers.SettingSerializer(), tags=["config_center"]
    )
    def update(self, request, category_id, setting_id, validated_data):
        api_instance = bkuser_sdk.SettingsApi(self.get_api_client_by_request(request))
        return api_instance.v2_settings_partial_update(body=validated_data, lookup_value=setting_id, lookup_field="id")

    @inject_serializer(tags=["config_center"])
    def delete(self, request, category_name, setting_id):
        api_instance = bkuser_sdk.SettingsApi(self.get_api_client_by_request(request))
        api_instance.v2_settings_delete(lookup_value=setting_id, lookup_field="id")

        return Response(data={})

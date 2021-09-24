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
from bkuser_sdk.rest import ApiException
from bkuser_shell.bkiam.constants import ActionEnum
from bkuser_shell.common.response import Response
from bkuser_shell.common.viewset import BkUserApiViewSet
from bkuser_shell.config_center.serializers import ProfileFieldsSerializer, SettingMetaSerializer, SettingSerializer
from rest_framework.permissions import IsAuthenticated

from bkuser_global.drf_crown import inject_serializer

from . import serializers

logger = logging.getLogger(__name__)


class FieldsViewSet(BkUserApiViewSet):
    serializer_class = ProfileFieldsSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    ACTION_ID = ActionEnum.MANAGE_FIELD.value

    def manageable(self, request):
        """检测是否能够管理用户字段"""
        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
        _ = api_instance.v2_dynamic_fields_list()
        return Response(data={})

    @inject_serializer(
        query_in=serializers.ListFieldsSerializer(),
        out=serializers.ProfileFieldsSerializer(many=True),
        tags=["config_center"],
    )
    def list(self, request, validated_data):
        """获取所有用户字段"""
        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request, no_auth=True))
        return self.get_paging_results(api_instance.v2_dynamic_fields_list)

    @inject_serializer(
        body_in=serializers.FieldsSaveSerializer(), out=serializers.ProfileFieldsSerializer(), tags=["config_center"]
    )
    def create(self, request, validated_data):
        """创建用户字段"""
        # 创建时默认设置为 0
        validated_data["order"] = 0
        field = bkuser_sdk.DynamicFields(**validated_data)
        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
        return api_instance.v2_dynamic_fields_create(body=field)

    @inject_serializer(
        body_in=serializers.FieldsUpdateSerializer, out=serializers.ProfileFieldsSerializer(), tags=["config_center"]
    )
    def update(self, request, field_id, validated_data):
        """更新用户字段"""
        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
        return api_instance.v2_dynamic_fields_partial_update(
            body=validated_data, lookup_value=field_id, lookup_field="id"
        )

    @inject_serializer(tags=["config_center"])
    def delete(self, request, field_id):
        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
        api_instance.v2_dynamic_fields_delete(lookup_value=field_id, lookup_field="id")
        return Response()

    @inject_serializer(
        body_in=serializers.FieldsUpdateSerializer, out=serializers.ProfileFieldsSerializer(), tags=["config_center"]
    )
    def update_order(self, request, field_id, new_order, validated_data):
        """更新用户字段排序"""
        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
        body = {"order": new_order}
        return api_instance.v2_dynamic_fields_partial_update(lookup_value=field_id, lookup_field="id", body=body)

    @inject_serializer(body_in=serializers.UpdateFieldsVisibleSerializer, tags=["config_center"])
    def update_visible(self, request, validated_data):
        """更新用户字段可见性"""
        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
        fields = self.get_paging_results(api_instance.v2_dynamic_fields_list)

        # 获取所有的 ids
        fields_full_ids = [x["id"] for x in fields]

        # 需要支持批量更新 API
        body = {"visible": True}
        updating_ids = validated_data["updating_ids"]

        for updating_id in updating_ids:
            api_instance.v2_dynamic_fields_partial_update(lookup_value=updating_id, lookup_field="id", body=body)

        # 未选中的字段则不展示
        body = {"visible": False}
        for updating_id in list(set(fields_full_ids) - set(updating_ids)):
            api_instance.v2_dynamic_fields_partial_update(lookup_value=updating_id, lookup_field="id", body=body)

        return Response(data={})


class SettingsViewSet(BkUserApiViewSet):
    serializer_class = SettingSerializer

    @inject_serializer(
        query_in=serializers.ListSettingsSerializer(),
        out=serializers.SettingSerializer(many=True),
        tags=["config_center"],
    )
    def list(self, request, category_id, validated_data):
        """获取所有配置"""
        api_instance = bkuser_sdk.SettingsApi(self.get_api_client_by_request(request))
        settings = api_instance.v2_settings_list(category_id=category_id, **validated_data)

        region = validated_data.get("region", None)
        if region:
            settings = [x for x in settings if x["region"] == region]

        return settings

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


class SettingsNamespaceViewSet(BkUserApiViewSet):
    """namespace 维度批量 settings 接口"""

    serializer_class = SettingMetaSerializer

    @inject_serializer(
        query_in=serializers.ListSettingsSerializer(),
        out=serializers.SettingSerializer(many=True),
        tags=["config_center"],
    )
    def list(self, request, category_id, namespace_name, validated_data):
        """获取 namespace 下的所有配置"""
        api_instance = bkuser_sdk.SettingsApi(self.get_api_client_by_request(request))
        settings = api_instance.v2_settings_list(category_id=category_id, namespace=namespace_name, **validated_data)

        region = validated_data.get("region", None)
        if region:
            settings = [x for x in settings if x["region"] == region]

        return settings

    @inject_serializer(
        query_in=serializers.ListSettingMetasSerializer(),
        out=serializers.SettingMetaSerializer(many=True),
        tags=["config_center"],
    )
    def list_defaults(self, request, validated_data):
        """获取 namespace 下的所有示例配置"""
        category_type = validated_data["category_type"]

        api_instance = bkuser_sdk.SettingMetasApi(self.get_api_client_by_request(request))
        setting_metas = self.get_paging_results(
            api_instance.v2_setting_metas_list, lookup_field="category_type", exact_lookups=[category_type]
        )

        filter_keys = ["region", "namespace"]
        for key in filter_keys:
            if not validated_data.get(key, None):
                continue

            setting_metas = [x for x in setting_metas if x[key] == validated_data[key]]

        return setting_metas

    @inject_serializer(
        body_in=serializers.UpdateNamespaceSettingSerializer(many=True),
        out=serializers.SettingSerializer(many=True),
        tags=["config_center"],
    )
    def update(self, request, category_id, namespace_name, validated_data):
        api_instance = bkuser_sdk.SettingsApi(self.get_api_client_by_request(request))
        settings = api_instance.v2_settings_list(category_id=category_id, namespace=namespace_name)

        setting_instances = {x.key: x for x in settings if x.namespace == namespace_name}

        # TODO:  后续改为批量接口
        result = []
        for setting_info in validated_data:
            body = {"value": setting_info["value"]}
            try:
                setting_id = setting_instances[setting_info["key"]].id
            except KeyError:
                logger.exception("找不到 Setting<%s>", setting_info["key"])
                continue

            try:
                api_response = api_instance.v2_settings_partial_update(body=body, lookup_value=setting_id)
            except ApiException:
                logger.exception("更新 Setting<%s> 失败", setting_info["id"])
                continue

            result.append(api_response)

        return result

    @inject_serializer(
        body_in=serializers.SettingSerializer(many=True),
        out=serializers.SettingSerializer(many=True),
        tags=["config_center"],
    )
    def create(self, request, category_id, namespace_name, validated_data):
        """批量创建一个 namespace 下的配置"""
        results = []
        # TODO:  后续改为批量接口
        api_instance = bkuser_sdk.SettingsApi(self.get_api_client_by_request(request))
        for setting_info in validated_data:
            # 兼容前端不传 ns 的情况
            setting_info["category_id"] = category_id
            if not setting_info.get("namespace", None):
                setting_info["namespace"] = namespace_name

            try:
                api_response = api_instance.v2_settings_create(setting_info)
            except ApiException:
                logger.exception("创建配置信息<%s-%s> 失败", namespace_name, setting_info["key"])
                continue

            if api_response:
                results.append(api_response)

        return results

    @inject_serializer(tags=["config_center"])
    def delete(self, request, category_name, namespace_name):
        raise NotImplementedError

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
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from openpyxl import load_workbook

import bkuser_sdk
from ..common.export import ProfileExcelExporter
from .constants import CategoryTypeEnum
from bkuser_global.drf_crown import inject_serializer
from bkuser_shell.apis.viewset import BkUserApiViewSet
from bkuser_shell.bkiam.constants import IAMAction
from bkuser_shell.categories.serializers import (
    CategoryExportSerializer,
    CategorySyncSerializer,
    DetailCategorySerializer,
)
from bkuser_shell.common.error_codes import error_codes
from bkuser_shell.common.response import Response
from bkuser_shell.common.serializers import EmptySerializer
from bkuser_shell.proxy.proxy import BkUserApiProxy

logger = logging.getLogger(__name__)


class CategoriesViewSet(BkUserApiViewSet, BkUserApiProxy):
    serializer_class = DetailCategorySerializer
    ACTION_ID = IAMAction.MANAGE_CATEGORY.value

    def get(self, request, category_id):
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))
        api_response = api_instance.v2_categories_read(lookup_field="id", lookup_value=category_id)

        return Response(data=DetailCategorySerializer(api_response).data)

    @inject_serializer(body_in=EmptySerializer, tags=["categories"])
    def switch_order(self, request, category_id, another_category_id):
        """更新组织顺序"""
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))

        categories = []
        for x_id in [category_id, another_category_id]:
            categories.append(api_instance.v2_categories_read(x_id))

        # 交换 order 字段
        category_a, category_b = categories
        for index, x_category in enumerate([category_b, category_a]):
            body = {"order": x_category.order}
            api_instance.v2_categories_partial_update(lookup_value=categories[index].id, body=body)

        return Response(data={})


class CategoriesSyncViewSet(BkUserApiViewSet):
    serializer_class = DetailCategorySerializer
    ACTION_ID = IAMAction.MANAGE_CATEGORY.value

    @inject_serializer(body_in=CategorySyncSerializer, tags=["categories"])
    def sync(self, request, category_id, validated_data):
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))
        category = api_instance.v2_categories_read(lookup_field="id", lookup_value=category_id)

        method = "v2_categories_sync"
        params = {"body": {}}
        if category.type == CategoryTypeEnum.LOCAL.value:
            if not validated_data.get("file"):
                raise error_codes.LOCAL_CATEGORY_NEEDS_EXCEL_FILE

            raw_data_file = validated_data.get("file")
            if raw_data_file:
                path = default_storage.save("tmp/raw_data_file", ContentFile(raw_data_file.read()))
                tmp_file = os.path.join(settings.MEDIA_ROOT, path)
                params = {"raw_data_file": tmp_file}
                method = "v2_categories_import_data_file"

        getattr(api_instance, method)(lookup_value=category_id, **params)
        return Response(data={})


class CategoriesExportViewSet(BkUserApiViewSet):
    ACTION_ID = IAMAction.MANAGE_CATEGORY.value

    @inject_serializer(query_in=CategoryExportSerializer, out=EmptySerializer, tags=["categories"])
    def export(self, request, category_id, validated_data):
        """导出组织架构"""
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))
        category = api_instance.v2_categories_read(lookup_field="id", lookup_value=category_id)

        if not category.type == CategoryTypeEnum.LOCAL.value:
            raise error_codes.LOCAL_CATEGORY_NEEDS_EXCEL_FILE

        department_ids = validated_data["department_ids"]
        api_instance = bkuser_sdk.BatchApi(self.get_api_client_by_request(request))
        field_api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
        all_profiles = api_instance.v2_batch_departments_multiple_retrieve_profiles(
            department_ids=department_ids, recursive=True
        )

        fields = self.get_paging_results(field_api_instance.v2_dynamic_fields_list)
        exporter = ProfileExcelExporter(
            load_workbook(settings.EXPORT_ORG_TEMPLATE), settings.EXPORT_EXCEL_FILENAME + "_org", fields
        )
        exporter.update_profiles(all_profiles)

        return exporter.to_response()

    @inject_serializer(out=EmptySerializer, tags=["categories"])
    def export_template(self, request, category_id):
        """生成excel导入模板样例文件"""
        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
        fields = self.get_paging_results(api_instance.v2_dynamic_fields_list)
        exporter = ProfileExcelExporter(
            load_workbook(settings.EXPORT_ORG_TEMPLATE), settings.EXPORT_EXCEL_FILENAME + "_org_tmpl", fields
        )

        return exporter.to_response()

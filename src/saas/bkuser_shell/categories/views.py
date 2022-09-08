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

from django.conf import settings
from openpyxl import load_workbook

import bkuser_sdk
from ..common.export import ProfileExcelExporter
from .constants import CategoryTypeEnum
from bkuser_global.drf_crown import inject_serializer
from bkuser_shell.apis.viewset import BkUserApiViewSet
from bkuser_shell.bkiam.constants import IAMAction
from bkuser_shell.categories.serializers import CategoryExportSerializer
from bkuser_shell.common.error_codes import error_codes
from bkuser_shell.common.serializers import EmptySerializer

logger = logging.getLogger(__name__)


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

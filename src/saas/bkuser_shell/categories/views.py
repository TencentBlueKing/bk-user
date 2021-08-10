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

import bkuser_sdk
from bkuser_shell.bkiam.constants import ActionEnum
from bkuser_shell.categories.serializers import (
    CategoryExportSerializer,
    CategoryMetaSLZ,
    CategorySyncSerializer,
    CategoryTestConnectionSerializer,
    CategoryTestFetchDataSerializer,
    CreateCategorySerializer,
    DetailCategorySerializer,
    ListCategorySerializer,
    UpdateCategorySerializer,
)
from bkuser_shell.common.error_codes import error_codes
from bkuser_shell.common.response import Response
from bkuser_shell.common.serializers import EmptySerializer
from bkuser_shell.common.viewset import BkUserApiViewSet
from bkuser_shell.config_center.constants import DynamicFieldTypeEnum
from bkuser_shell.organization.serializers.profiles import ProfileExportSerializer
from bkuser_shell.organization.utils import get_options_values_by_key
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http.response import HttpResponse
from django.utils.translation import ugettext_lazy as _
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, colors

from bkuser_global.drf_crown import inject_serializer

from .constants import TEST_CONNECTION_TYPES, CategoryStatus, CategoryTypeEnum

logger = logging.getLogger(__name__)


class CategoriesViewSet(BkUserApiViewSet):
    serializer_class = DetailCategorySerializer
    ACTION_ID = ActionEnum.MANAGE_CATEGORY.value

    def list_metas(self, request):
        """获取目录基本信息列表"""
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))
        api_response = api_instance.v2_categories_list_metas()
        return Response(data=CategoryMetaSLZ(api_response, many=True).data)

    def get(self, request, category_id):
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))
        api_response = api_instance.v2_categories_read(lookup_field="id", lookup_value=category_id)

        return Response(data=DetailCategorySerializer(api_response).data)

    @inject_serializer(out=DetailCategorySerializer, tags=["categories"])
    def get_default(self, request):
        api_instance = bkuser_sdk.CategoriesApi(
            self.get_api_client_by_request(request, force_action_id=ActionEnum.VIEW_CATEGORY.value)
        )
        api_response = self.get_paging_results(
            api_instance.v2_categories_list, lookup_field="default", exact_lookups=[True]
        )

        if not api_response:
            raise error_codes.CANNOT_FIND_DEFAULT_CATEGORY

        # 正常情况下 default 就只有一个
        return api_response[0]

    @inject_serializer(query_in=ListCategorySerializer, out=DetailCategorySerializer(many=True), tags=["categories"])
    def list(self, request, validated_data):
        lookup_params = {}
        if validated_data["only_enable"]:
            lookup_params = {
                "lookup_field": "enabled",
                "exact_lookups": [True],
            }

        api_instance = bkuser_sdk.CategoriesApi(
            self.get_api_client_by_request(request, force_action_id=ActionEnum.VIEW_CATEGORY.value)
        )
        return self.get_paging_results(api_instance.v2_categories_list, **lookup_params)

    @inject_serializer(body_in=UpdateCategorySerializer, out=DetailCategorySerializer, tags=["categories"])
    def update(self, request, category_id, validated_data):
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))
        category = api_instance.v2_categories_read(lookup_value=category_id)

        activated = validated_data.pop("activated")
        category.status = CategoryStatus.NORMAL.value if activated else CategoryStatus.INACTIVE.value

        # update category
        for key, value in validated_data.items():
            setattr(category, key, value)

        return api_instance.v2_categories_partial_update(body=category, lookup_value=category_id)

    @inject_serializer(body_in=UpdateCategorySerializer, tags=["categories"])
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

    @inject_serializer(tags=["categories"])
    def delete(self, request, category_id):
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))
        api_instance.v2_categories_delete(lookup_value=category_id)
        return Response()

    @inject_serializer(body_in=CreateCategorySerializer, out=DetailCategorySerializer, tags=["categories"])
    def create(self, request, validated_data):
        activated = validated_data.pop("activated")
        validated_data["status"] = CategoryStatus.NORMAL.value if activated else CategoryStatus.INACTIVE.value

        category = bkuser_sdk.Category(**validated_data)

        api_instance = bkuser_sdk.CategoriesApi(
            self.get_api_client_by_request(
                request,
                force_action_id=ActionEnum.get_action_by_category_type(category.type).value,
            )
        )
        return api_instance.v2_categories_create(body=category)


class CategoriesSyncViewSet(BkUserApiViewSet):
    serializer_class = DetailCategorySerializer
    ACTION_ID = ActionEnum.MANAGE_CATEGORY.value

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

    @inject_serializer(body_in=CategoryTestConnectionSerializer, tags=["categories"])
    def test_connection(self, request, category_id, validated_data):
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))
        category = api_instance.v2_categories_read(lookup_field="id", lookup_value=category_id)

        if category.type not in TEST_CONNECTION_TYPES:
            raise error_codes.CATEGORY_CANNOT_TEST_CONNECTION

        api_instance.v2_categories_test_connection(lookup_value=category_id, body=validated_data)
        return Response(data={})

    @inject_serializer(body_in=CategoryTestFetchDataSerializer, tags=["categories"])
    def test_fetch_data(self, request, category_id, validated_data):
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))
        category = api_instance.v2_categories_read(lookup_field="id", lookup_value=category_id)

        if category.type not in TEST_CONNECTION_TYPES:
            raise error_codes.CATEGORY_CANNOT_TEST_CONNECTION

        api_instance.v2_categories_test_fetch_data(lookup_value=category_id, body=validated_data)
        return Response(data={})


class CategoriesExportViewSet(BkUserApiViewSet):
    ACTION_ID = ActionEnum.MANAGE_CATEGORY.value

    @inject_serializer(query_in=CategoryExportSerializer, out=EmptySerializer, tags=["categories"])
    def export(self, request, category_id, validated_data):
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request))
        category = api_instance.v2_categories_read(lookup_field="id", lookup_value=category_id)

        if not category.type == CategoryTypeEnum.LOCAL.value:
            raise error_codes.LOCAL_CATEGORY_NEEDS_EXCEL_FILE

        department_ids = validated_data["department_ids"]
        api_instance = bkuser_sdk.BatchApi(self.get_api_client_by_request(request))
        all_profiles = api_instance.v2_batch_departments_multiple_retrieve_profiles(
            department_ids=department_ids, recursive=True
        )

        try:
            export_template = self.load_export_template()
            first_sheet = export_template.worksheets[0]
            first_sheet.alignment = Alignment(wrapText=True)
        except Exception:
            logger.exception("读取模版文件失败, Category<%s>", category_id)
            raise error_codes.CATEGORY_EXPORT_FAILED.f(_("读取模版文件失败, 请联系管理员"))

        try:
            all_profiles = ProfileExportSerializer(all_profiles, many=True).data
            fields_api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
            required_fields, not_required_fields = self._get_fields(fields_api_instance)
            self._update_sheet_titles(required_fields, not_required_fields, first_sheet)
            all_fields = required_fields + not_required_fields
        except Exception:
            logger.exception("导出 Category<%s> 失败", category_id)
            raise error_codes.CATEGORY_EXPORT_FAILED.f(_("获取用户信息字段失败, 请联系管理员"))

        # 写用户数据
        for row_index, row_data in enumerate(all_profiles):
            for index, field in enumerate(all_fields):
                # 对于任意包含 options 值的内容
                try:
                    if field["builtin"]:
                        raw_value = row_data[field["name"]]
                    else:
                        raw_value = row_data["extras"][field["name"]]
                except Exception:  # pylint: disable=broad-except
                    logger.exception("failed to get value from field<%s>", field)
                    continue

                value = raw_value
                # options 存储值为 key， 但是 Excel 交互值为 value
                if field["type"] == DynamicFieldTypeEnum.ONE_ENUM.value:
                    value = ",".join(get_options_values_by_key(field["options"], [raw_value]))
                elif field["type"] == DynamicFieldTypeEnum.MULTI_ENUM.value:
                    value = ",".join(get_options_values_by_key(field["options"], raw_value))

                # 为电话添加国际号码段
                if field["name"] == "telephone":
                    value = f'+{row_data["country_code"]}{row_data[field["name"]]}'

                try:
                    first_sheet.cell(row=row_index + 3, column=index + 1, value=value)
                except Exception:  # pylint: disable=broad-except
                    logger.exception("写入表格数据失败 Category<%s>-Profile<%s>", category_id, row_data)
                    continue

        response = self.make_excel_response(settings.EXPORT_EXCEL_FILENAME)
        export_template.save(response)
        return response

    @inject_serializer(query_in=CategoryExportSerializer, out=EmptySerializer, tags=["categories"])
    def export_template(self, request, category_id, validated_data):
        """生成excel导入模板样例文件"""

        export_template = self.load_export_template()
        first_sheet = export_template.worksheets[0]
        first_sheet.alignment = Alignment(wrapText=True)

        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
        required_fields, not_required_fields = self._get_fields(api_instance)
        self._update_sheet_titles(required_fields, not_required_fields, first_sheet)

        response = self.make_excel_response(settings.EXPORT_EXCEL_FILENAME + "_template")
        export_template.save(response)
        return response

    @staticmethod
    def make_excel_response(file_name: str):
        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = f"attachment;filename={file_name}.xlsx"
        return response

    @staticmethod
    def load_export_template():
        return load_workbook(settings.EXPORT_EXCEL_TEMPLATE)

    def _get_fields(self, api_instance):
        """获取所有的字段"""
        fields = self.get_paging_results(api_instance.v2_dynamic_fields_list)

        required_fields = [x for x in fields if x["require"]]
        not_required_fields = [x for x in fields if not x["require"]]
        return required_fields, not_required_fields

    @staticmethod
    def _update_sheet_titles(required_fields, not_required_fields, sheet, title_row_index=2):
        """更新表格标题"""
        required_field_names = [x["display_name"] for x in required_fields]
        not_required_field_names = [x["display_name"] for x in not_required_fields]

        red_ft = Font(color=colors.RED)
        black_ft = Font(color=colors.BLACK)
        for index, field_name in enumerate(required_field_names):
            _cell = sheet.cell(
                row=title_row_index,
                column=index + 1,
                value=field_name,
            )
            _cell.font = red_ft

        for index, field_name in enumerate(not_required_field_names):
            _cell = sheet.cell(
                row=title_row_index,
                column=index + 1 + len(required_field_names),
                value=field_name,
            )
            _cell.font = black_ft

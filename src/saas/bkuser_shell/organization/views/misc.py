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
from bkuser_shell.bkiam.constants import ActionEnum
from bkuser_shell.common.error_codes import error_codes
from bkuser_shell.common.response import Response
from bkuser_shell.common.viewset import BkUserApiViewSet
from bkuser_shell.organization.constants import ProfileWildSearchFieldEnum
from bkuser_shell.organization.serializers.departments import DepartmentSerializer
from bkuser_shell.organization.serializers.misc import SearchResultSerializer, SearchSerializer
from bkuser_shell.organization.utils import expand_extra_fields
from django.conf import settings
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from bkuser_global.drf_crown import inject_serializer

logger = logging.getLogger(__name__)


class SearchViewSet(BkUserApiViewSet):
    @inject_serializer(
        query_in=SearchSerializer,
        out=SearchResultSerializer(many=True),
        tags=["misc"],
    )
    def search(self, request, validated_data):
        fields_api_instance = bkuser_sdk.DynamicFieldsApi(
            self.get_api_client_by_request(request, force_action_id=ActionEnum.MANAGE_FIELD.value, no_auth=True)
        )
        profiles_api_instance = bkuser_sdk.ProfilesApi(
            self.get_api_client_by_request(request, force_action_id=ActionEnum.MANAGE_DEPARTMENT.value)
        )
        departments_api_instance = bkuser_sdk.DepartmentsApi(
            self.get_api_client_by_request(request, force_action_id=ActionEnum.MANAGE_DEPARTMENT.value)
        )
        categories_api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request, no_auth=True))

        max_items = validated_data.get("max_items", 20)
        keyword = validated_data["keyword"]
        if not keyword:
            return Response(data=[])

        # 1. 获取当前目录信息
        categories = self.get_paging_results(categories_api_instance.v2_categories_list)
        _cached_categories_map = {x["id"]: x["display_name"] for x in categories}

        # 2. 获取动态字段信息
        fields = fields_api_instance.v2_dynamic_fields_list()["results"]
        extra_fields = [x for x in fields if not x["builtin"]]

        # 分页，保证搜索速度
        hit_profiles = profiles_api_instance.v2_profiles_list(
            page=1,
            page_size=max_items,
            wildcard_search=keyword,
            wildcard_search_fields=ProfileWildSearchFieldEnum.to_list(),
        )
        if hit_profiles:
            hit_profiles = hit_profiles.get("results")

        hit_type_map = {
            field: {
                "type": field,
                "display_name": ProfileWildSearchFieldEnum.get_choice_label(field),
                "items": [],
            }
            for field in ProfileWildSearchFieldEnum.to_list()
        }

        for profile in hit_profiles:
            for field in ProfileWildSearchFieldEnum.to_list():
                if keyword in profile.get(field, ""):
                    profile = expand_extra_fields(extra_fields, profile)
                    if _cached_categories_map.get(profile["category_id"]):
                        profile["category_name"] = _cached_categories_map.get(profile["category_id"])
                        hit_type_map[field]["items"].append(profile)
                        # 只匹配一种类型
                        break

        # department 只有一种类型
        hit_departments = departments_api_instance.v2_departments_list(
            page=1,
            page_size=max_items,
            wildcard_search=keyword,
            wildcard_search_fields=["name"],
        )
        # 避免过多的搜索内容
        hit_departments = hit_departments.get("results")[:max_items]
        for d in hit_departments:
            d["category_name"] = _cached_categories_map[d["category_id"]]

        hit_type_map["department"] = {
            "type": "department",
            "display_name": _("组织"),
            "items": DepartmentSerializer(hit_departments, many=True).data,
        }
        return Response(data=hit_type_map.values())


class WebPageViewSet(BkUserApiViewSet):

    serializer_class = None

    permission_classes: list = []

    def index(self, request):
        try:
            return TemplateResponse(request=request, template=get_template("index.html"))
        except TemplateDoesNotExist:
            raise error_codes.CANNOT_FIND_TEMPLATE


class HeaderFooterViewSet(BkUserApiViewSet):

    permission_classes: list = []

    def get(self, request):
        """获取动态的 header & footer 内容"""
        return Response(data=settings.FOOTER_CONFIG)

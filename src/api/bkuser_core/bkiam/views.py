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
from .base import BaseIAMViewSet
from .constants import ResourceType
from .serializers import DepartmentInstanceRespSLZ
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.serializers import CategorySerializer
from bkuser_core.departments.models import Department
from bkuser_core.departments.v2.serializers import DepartmentSerializer
from bkuser_core.profiles.models import DynamicFieldInfo
from bkuser_core.profiles.v2.serializers import DynamicFieldsSerializer


class DynamicFieldIAMViewSet(BaseIAMViewSet):
    """动态字段 IAM 回调"""

    resource_type = ResourceType.FIELD  # type: ignore
    serializer_class = DynamicFieldsSerializer
    available_attr = ["name", "display_name"]
    queryset = DynamicFieldInfo.objects.filter(enabled=True)


class CategoryIAMViewSet(BaseIAMViewSet):
    """用户目录 IAM 回调"""

    resource_type = ResourceType.CATEGORY  # type: ignore
    serializer_class = CategorySerializer
    available_attr = ["name", "type", "display_name"]
    queryset = ProfileCategory.objects.filter(enabled=True)


class DepartmentIAMViewSet(BaseIAMViewSet):
    """组织 IAM 回调"""

    resource_type = ResourceType.DEPARTMENT  # type: ignore
    serializer_class = DepartmentSerializer
    available_attr = ["id", "name", "category_id", "level"]
    queryset = Department.objects.filter(enabled=True)
    parent_field_map = {"department": "parent_id", "category": "category_id"}
    instance_serializer_class = DepartmentInstanceRespSLZ

    def get_parent_queries(self, parent_params: dict) -> dict:
        queries: dict = {}
        if parent_params["type"] == "category":
            queries[self.parent_field_map["department"]] = None

        queries[self.parent_field_map[parent_params["type"]]] = int(parent_params["id"])
        return queries

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
import functools
from operator import or_

from django.db.models import Q
from rest_framework import generics

from bkuser_core.api.web.recycle_bin.constants import RECYCLE_BIN_OBJECT_MAP
from bkuser_core.api.web.recycle_bin.serializers import (
    RecycleBinCategoryOutputSlZ,
    RecycleBinDepartmentOutputSlZ,
    RecycleBinProfileOutputSlZ,
    RecycleBinSearchInputSlZ,
)
from bkuser_core.api.web.viewset import CustomPagination
from bkuser_core.recycle_bin.constants import RecycleBinObjectStatus, RecycleBinObjectType
from bkuser_core.recycle_bin.models import RecycleBin


class RecycleBinBaseListApi(generics.ListAPIView):
    """
    回收站展示基础类
    """

    object_type: str = ""
    search_fields: list = []
    queryset = RecycleBin.objects.filter(status=RecycleBinObjectStatus.SOFT_DELETED.value)
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = self.queryset.filter(object_type=self.object_type)
        input_slz = RecycleBinSearchInputSlZ(data=self.request.query_params)
        input_slz.is_valid(raise_exception=True)
        data = input_slz.validated_data

        keyword = data.get("keyword")
        if keyword:
            # Q 连接对应search_filed 和 keyword
            condition_combos = [Q(**{"{}__icontains".format(filed): keyword}) for filed in self.search_fields]
            query = functools.reduce(or_, condition_combos)
            object_ids = RECYCLE_BIN_OBJECT_MAP[self.object_type].objects.filter(query).values_list("id", flat=True)
            queryset = queryset.filter(object_id__in=object_ids)
        return queryset

    def list(self, request, *args, **kwargs):
        return super(RecycleBinBaseListApi, self).list(request, *args, **kwargs)


class RecycleBinCategoryListApi(RecycleBinBaseListApi):
    """
    回收站：目录展示
    """

    object_type = RecycleBinObjectType.CATEGORY.value
    serializer_class = RecycleBinCategoryOutputSlZ
    search_fields = ["domain", "display_name"]


class RecycleBinDepartmentListApi(RecycleBinBaseListApi):
    """
    回收站：组织展示
    """

    object_type = RecycleBinObjectType.DEPARTMENT.value
    serializer_class = RecycleBinDepartmentOutputSlZ
    search_fields = ["name"]


class RecycleBinProfileListApi(RecycleBinBaseListApi):
    """
    回收站：人员展示
    """

    object_type = RecycleBinObjectType.PROFILE.value
    serializer_class = RecycleBinProfileOutputSlZ
    search_fields = ["username", "display_name"]

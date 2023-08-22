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
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status

from bkuser.apis.web.data_source.serializers import DepartmentSearchInputSLZ, DepartmentSearchOutputSLZ
from bkuser.apps.data_source.models import DataSource, DataSourceDepartment
from bkuser.common.error_codes import error_codes


class DataSourceDepartmentsListApi(generics.ListAPIView):
    serializer_class = DepartmentSearchOutputSLZ

    def get_queryset(self):
        data_source_id = self.kwargs["id"]
        slz = DepartmentSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 校验数据源是否存在
        try:
            data_source = DataSource.objects.get(id=data_source_id)
        except Exception:
            raise error_codes.DATA_SOURCE_NOT_EXIST

        queryset = DataSourceDepartment.objects.filter(data_source=data_source)

        if name := data.get("name"):
            queryset = queryset.filter(name__icontains=name)

        return queryset

    @swagger_auto_schema(
        operation_description="数据源部门列表",
        query_serializer=DepartmentSearchInputSLZ(),
        responses={status.HTTP_200_OK: DepartmentSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

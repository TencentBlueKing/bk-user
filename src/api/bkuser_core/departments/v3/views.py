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

from rest_framework import filters, viewsets
from rest_framework.generics import ListAPIView

from .serializers import PaginatedDeptSerializer, QueryDeptSerializer
from bkuser_core.apis.v3.exceptions import QueryTooLong
from bkuser_core.apis.v3.filters import MultipleFieldFilter
from bkuser_core.apis.v3.serializers import AdvancedPagination
from bkuser_core.bkiam.exceptions import IAMPermissionDenied
from bkuser_core.bkiam.permissions import IAMPermission
from bkuser_core.common.error_codes import error_codes
from bkuser_core.departments.models import Department
from bkuser_global.drf_crown.crown import inject_serializer

logger = logging.getLogger(__name__)


class DepartmentViewSet(viewsets.ModelViewSet, ListAPIView):
    queryset = Department.objects.all()
    permission_classes = [IAMPermission]
    filter_backends = [filters.OrderingFilter]
    pagination_class = AdvancedPagination
    ordering = "id"

    foreign_fields = ["parent", "children"]

    @inject_serializer(query_in=QueryDeptSerializer, out=PaginatedDeptSerializer)
    def list(self, request, validated_data: dict, *args, **kwargs):
        """获取用户列表"""
        self.check_permissions(request)

        try:
            queryset = MultipleFieldFilter().filter_by_params(
                self.filter_queryset(self.get_queryset()), validated_data, self
            )
        except IAMPermissionDenied:
            raise
        except QueryTooLong as e:
            raise error_codes.QUERIES_TOO_LONG.f(e)
        except Exception:
            logger.exception("failed to get department list with validated_data: %s", validated_data)
            raise error_codes.QUERY_PARAMS_ERROR

        return self.get_paginated_response(self.paginate_queryset(queryset))

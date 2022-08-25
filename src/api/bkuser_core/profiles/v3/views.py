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

from rest_framework import filters
from rest_framework.generics import ListAPIView

from bkuser_core.apis.v2.viewset import AdvancedModelViewSet
from bkuser_core.apis.v3.exceptions import QueryTooLong
from bkuser_core.apis.v3.filters import MultipleFieldFilter
from bkuser_core.apis.v3.serializers import AdvancedPagination
from bkuser_core.bkiam.exceptions import IAMPermissionDenied
from bkuser_core.bkiam.permissions import IAMPermission
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.v3.serializers import PaginatedProfileSerializer, QueryProfileSerializer
from bkuser_global.drf_crown.crown import inject_serializer

logger = logging.getLogger(__name__)


# class ProfileViewSet(viewsets.ModelViewSet, ListAPIView):
class ProfileViewSet(AdvancedModelViewSet, ListAPIView):
    """获取用户数据"""

    queryset = Profile.objects.all()
    permission_classes = [IAMPermission]
    filter_backends = [filters.OrderingFilter]
    pagination_class = AdvancedPagination
    ordering = "id"

    foreign_fields = ["departments", "leader"]
    in_fields = ["username__in", "staff_status__in", "status__in"]

    # 使用 filter 进行过滤的操作
    iam_filter_actions: tuple = ("list",)

    @inject_serializer(query_in=QueryProfileSerializer, out=PaginatedProfileSerializer)
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
            raise error_codes.QUERY_TOO_LONG.f(e)
        except Exception:
            logger.exception("failed to get profile list")
            raise error_codes.QUERY_PARAMS_ERROR

        return self.get_paginated_response(self.paginate_queryset(queryset))

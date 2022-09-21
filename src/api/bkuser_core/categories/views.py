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

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.response import Response

from bkuser_core.apis.v2.viewset import AdvancedListAPIView, AdvancedModelViewSet, AdvancedSearchFilter
from bkuser_core.audit.constants import OperationType
from bkuser_core.audit.utils import audit_general_log
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.serializers import CategorySerializer, CreateCategorySerializer
from bkuser_core.categories.signals import post_category_create
from bkuser_core.common.cache import clear_cache_if_succeed
from bkuser_core.common.error_codes import error_codes

logger = logging.getLogger(__name__)


class CategoryViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    queryset = ProfileCategory.objects.filter()
    serializer_class = CategorySerializer
    lookup_field = "id"
    filter_backends = [
        AdvancedSearchFilter,
        filters.OrderingFilter,
    ]

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(request_body=CreateCategorySerializer, responses={"200": CategorySerializer()})
    def create(self, request, *args, **kwargs):
        """
        创建用户目录
        """
        self.check_permissions(request)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)

        # 默认添加到最后 TODO: 需要一个更优雅的实现
        max_order = ProfileCategory.objects.get_max_order()
        instance.order = max_order + 1
        instance.save(update_fields=["order"])
        post_category_create.send_robust(
            sender=self, instance=instance, operator=request.operator, extra_values={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer(self, *args, **kwargs):
        if self.action in ["create"]:
            return CreateCategorySerializer(*args, **kwargs)
        else:
            return self.serializer_class(*args, **kwargs)

    @audit_general_log(operate_type=OperationType.UPDATE.value)
    @method_decorator(clear_cache_if_succeed)
    def update(self, request, *args, **kwargs):
        """
        更新用户目录
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        self.check_object_permissions(request, instance)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        updating_domain = serializer.validated_data.get("domain")
        if updating_domain and not updating_domain == instance.domain:
            raise error_codes.CANNOT_UPDATE_DOMAIN

        if instance.default and any(serializer.validated_data.get(x) is False for x in ["enabled", "status"]):
            raise error_codes.CANNOT_DISABLE_DOMAIN

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
import logging

from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status

from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apis.open_v3.serializers.user import (
    TenantUserDisplayNameListInputSLZ,
    TenantUserDisplayNameListOutputSLZ,
    TenantUserLeaderListOutputSLZ,
    TenantUserRetrieveOutputSLZ,
)
from bkuser.apps.data_source.models import DataSourceUserLeaderRelation
from bkuser.apps.tenant.models import TenantUser
from bkuser.common.error_codes import error_codes

logger = logging.getLogger(__name__)


class TenantUserDisplayNameListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    批量根据用户 bk_username 获取用户展示名
    TODO: 性能较高，只查询所需字段，后续开发 DisplayName 支持表达式配置时添加 Cache 方案
    """

    pagination_class = None

    serializer_class = TenantUserDisplayNameListOutputSLZ

    def get_queryset(self):
        slz = TenantUserDisplayNameListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # TODO: 由于目前 DisplayName 渲染只与 full_name 相关，所以只查询 full_name
        # 后续支持表达式，则需要查询表达式可配置的所有字段
        return (
            TenantUser.objects.filter(id__in=data["bk_usernames"])
            .select_related("data_source_user")
            .only("id", "data_source_user__full_name")
        )

    @swagger_auto_schema(
        tags=["open_v3.user"],
        operation_id="batch_query_user_display_name",
        operation_description="批量查询用户展示名",
        query_serializer=TenantUserDisplayNameListInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserDisplayNameListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TenantUserRetrieveApi(OpenApiCommonMixin, generics.RetrieveAPIView):
    """
    根据用户 bk_username 获取用户信息
    """

    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    serializer_class = TenantUserRetrieveOutputSLZ

    @swagger_auto_schema(
        tags=["open_v3.user"],
        operation_id="retrieve_user",
        operation_description="查询用户信息",
        responses={status.HTTP_200_OK: TenantUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TenantUserLeaderListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    根据用户 bk_username 获取用户 Leader 列表信息
    """

    pagination_class = None

    serializer_class = TenantUserLeaderListOutputSLZ

    def get_queryset(self):
        tenant_user = TenantUser.objects.select_related("data_source_user").filter(id=self.kwargs["id"]).first()

        if not tenant_user:
            raise error_codes.TENANT_USER_NOT_EXIST.f(_("租户用户不存在"))

        return self._get_user_leader(tenant_user)

    @staticmethod
    def _get_user_leader(tenant_user: TenantUser):
        user_leader_relation = DataSourceUserLeaderRelation.objects.filter(user=tenant_user.data_source_user)

        if not user_leader_relation:
            return []

        return TenantUser.objects.filter(
            data_source_user_id__in=[relation.leader_id for relation in user_leader_relation],
            tenant_id=tenant_user.tenant_id,
        )

    @swagger_auto_schema(
        tags=["open_v3.user"],
        operation_id="query_user_leader",
        operation_description="查询用户 Leader 列表",
        responses={status.HTTP_200_OK: TenantUserDisplayNameListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

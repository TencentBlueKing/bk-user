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
from typing import List

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.person_center.serializers import (
    NaturalUserRelatedTenantUserListOutputSLZ,
    TenantUserRetrieveOutputSLZ,
)
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.natural_user import NaturalUserWithTenantUsers, NatureUserHandler, TenantBaseInfo, TenantUserBaseInfo


class NaturalUserTenantUserListApi(CurrentUserTenantMixin, generics.ListAPIView):
    pagination_class = None

    @swagger_auto_schema(
        tags=["user-center"],
        operation_description="个人中心-关联账户列表",
        responses={status.HTTP_200_OK: NaturalUserRelatedTenantUserListOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        current_tenant_user = self.get_current_tenant_user()

        # 获取当前登录的租户用户的自然人
        nature_user = NatureUserHandler.get_nature_user_by_tenant_user_id(current_tenant_user.id)

        # 未绑定自然人，则返回当用户所属数据源用户
        data_source_user_ids: List = [current_tenant_user.data_source_user_id]

        # 当前租户用户的数据源用户绑定了自然人，返回自然人绑定数据源用户
        if nature_user is not None:
            data_source_user_ids += nature_user.data_source_user_ids
        else:
            # 未绑定自然人，则返回当用户所属数据源用户
            data_source_user_ids = [current_tenant_user.data_source_user_id]

        # 将当前登录置顶
        # 通过比对租户用户id, 当等于当前登录用户的租户id，将其排序到查询集的顶部, 否则排序到查询集的底部
        tenant_users = TenantUser.objects.filter(data_source_user_id__in=data_source_user_ids)
        sorted_tenant_users = sorted(tenant_users, key=lambda t: t.id != current_tenant_user.id)

        # 响应数据组装
        # 当前登录的用户，未绑定自然人，(伪)自然人为当前租户用户
        data = NaturalUserWithTenantUsers(
            id=nature_user.id if nature_user else current_tenant_user.id,
            full_name=nature_user.full_name if nature_user else current_tenant_user.data_source_user.full_name,
            tenant_users=[
                TenantUserBaseInfo(
                    id=user.id,
                    username=user.data_source_user.username,
                    full_name=user.data_source_user.full_name,
                    tenant=TenantBaseInfo(id=user.tenant_id, name=user.tenant.name),
                )
                for user in sorted_tenant_users
            ],
        )

        return Response(NaturalUserRelatedTenantUserListOutputSLZ(data).data)


class TenantUserRetrieveApi(generics.RetrieveAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    serializer_class = TenantUserRetrieveOutputSLZ

    @swagger_auto_schema(
        tags=["user-center"],
        operation_description="个人中心-关联账户详情",
        responses={status.HTTP_200_OK: TenantUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

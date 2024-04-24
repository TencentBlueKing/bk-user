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
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.organization.serializers import (
    TenantUserBatchCopyInputSLZ,
    TenantUserBatchCreateInputSLZ,
    TenantUserBatchDeleteInputSLZ,
    TenantUserBatchMoveInputSLZ,
)
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.data_source.utils import gen_tenant_user_id
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.common.error_codes import error_codes


class TenantUserBatchCreateApi(CurrentUserTenantMixin, generics.CreateAPIView):
    """批量创建租户用户"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="租户用户快速录入",
        request_body=TenantUserBatchCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: ""},
    )
    def post(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()

        data_source = DataSource.objects.filter(owner_tenant_id=cur_tenant_id, type=DataSourceTypeEnum.REAL).first()
        if not data_source:
            raise error_codes.DATA_SOURCE_NOT_EXIST.f(_("当前租户不存在实名用户的本地数据源"))
        if not data_source.is_local:
            raise error_codes.TENANT_USER_CREATE_FAILED.f(_("仅本地数据源支持操作用户"))

        slz = TenantUserBatchCreateInputSLZ(
            data=request.data,
            context={"tenant_id": cur_tenant_id, "data_source_id": data_source.id},
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_dept = TenantDepartment.objects.filter(id=data["department_id"], tenant_id=cur_tenant_id).first()
        if not tenant_dept:
            raise error_codes.TENANT_USER_CREATE_FAILED.f(_("指定的租户部门不存在"))

        with transaction.atomic():
            # 新建数据源用户
            data_source_users = [
                DataSourceUser(
                    data_source=data_source,
                    code=info["username"],
                    username=info["username"],
                    full_name=info["full_name"],
                    email=info["email"],
                    phone=info["phone"],
                    phone_country_code=info["phone_country_code"],
                    extras=info["extras"],
                )
                for info in data["user_infos"]
            ]
            DataSourceUser.objects.bulk_create(data_source_users)

            # 重新从 DB 查询以获取带 ID 的数据源用户
            data_source_users = DataSourceUser.objects.filter(code__in=[u["username"] for u in data["user_infos"]])

            # 绑定数据源部门 - 用户
            relations = [
                DataSourceDepartmentUserRelation(
                    user=user, department=tenant_dept.data_source_department, data_source=data_source
                )
                for user in data_source_users
            ]
            DataSourceDepartmentUserRelation.objects.bulk_create(relations)

            # 新建租户用户
            # FIXME (su) 支持协同后，要对协同的租户也立即创建租户用户（目前只是对数据源所属租户做创建）
            tenant_users = [
                TenantUser(
                    id=gen_tenant_user_id(cur_tenant_id, data_source, user),
                    tenant_id=tenant_dept.tenant_id,
                    data_source=data_source,
                    data_source_user=user,
                )
                for user in data_source_users
            ]
            TenantUser.objects.bulk_create(tenant_users)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserBatchCopyApi(CurrentUserTenantMixin, generics.CreateAPIView):
    """批量添加 / 拉取租户用户"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="租户用户 - 从其他组织拉取 / 添加到其他组织",
        request_body=TenantUserBatchCopyInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()

        data_source = DataSource.objects.filter(owner_tenant_id=cur_tenant_id, type=DataSourceTypeEnum.REAL).first()
        if not data_source:
            raise error_codes.DATA_SOURCE_NOT_EXIST.f(_("当前租户不存在实名用户的本地数据源"))
        if not data_source.is_local:
            raise error_codes.TENANT_USER_CREATE_FAILED.f(_("仅本地数据源支持操作用户"))

        slz = TenantUserBatchCopyInputSLZ(data=request.data, context={"tenant_id": cur_tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source_dept_ids = TenantDepartment.objects.filter(
            tenant_id=cur_tenant_id,
            id__in=data["department_ids"],
        ).values_list("data_source_department_id", flat=True)

        data_source_user_ids = TenantUser.objects.filter(
            tenant_id=cur_tenant_id,
            id__in=data["user_ids"],
        ).values_list("data_source_user_id", flat=True)

        # 复制操作：为数据源部门 & 用户添加关联边，但是不会影响存量的关联边
        relations = [
            DataSourceDepartmentUserRelation(user_id=user_id, department_id=dept_id, data_source=data_source)
            for dept_id, user_id in zip(data_source_dept_ids, data_source_user_ids)
        ]
        # 由于复制操作不会影响存量的关联边，所以需要忽略冲突，避免出现用户复选的情况
        DataSourceDepartmentUserRelation.objects.bulk_create(relations, ignore_conflicts=True)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserBatchMoveApi(CurrentUserTenantMixin, generics.CreateAPIView):
    """批量移动租户用户"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="租户用户 - 移动到其他组织",
        request_body=TenantUserBatchMoveInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()

        data_source = DataSource.objects.filter(owner_tenant_id=cur_tenant_id, type=DataSourceTypeEnum.REAL).first()
        if not data_source:
            raise error_codes.DATA_SOURCE_NOT_EXIST.f(_("当前租户不存在实名用户数据源"))
        if not data_source.is_local:
            raise error_codes.TENANT_USER_CREATE_FAILED.f(_("仅本地数据源支持操作用户"))

        slz = TenantUserBatchMoveInputSLZ(data=request.data, context={"tenant_id": self.get_current_tenant_id()})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source_dept_ids = TenantDepartment.objects.filter(
            tenant_id=cur_tenant_id,
            id__in=data["department_ids"],
        ).values_list("data_source_department_id", flat=True)

        data_source_user_ids = TenantUser.objects.filter(
            tenant_id=cur_tenant_id,
            id__in=data["user_ids"],
        ).values_list("data_source_user_id", flat=True)

        # 移动操作：为数据源部门 & 用户添加关联边，但是会删除这批用户所有的存量关联边
        with transaction.atomic():
            # 先删除
            DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids).delete()
            # 再添加
            relations = [
                DataSourceDepartmentUserRelation(user_id=user_id, department_id=dept_id, data_source=data_source)
                for dept_id, user_id in zip(data_source_dept_ids, data_source_user_ids)
            ]
            DataSourceDepartmentUserRelation.objects.bulk_create(relations)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserBatchDeleteApi(CurrentUserTenantMixin, generics.DestroyAPIView):
    """批量删除租户用户"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="租户用户 - 批量删除",
        request_body=TenantUserBatchDeleteInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()

        slz = TenantUserBatchDeleteInputSLZ(data=request.query_params, context={"tenant_id": cur_tenant_id})
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        # 注：直接计算待删除的数据源用户 ID 列表，不要使用 .values_list("data_source_user_id", flat=True)
        # 原因是：惰性求值会导致租户用户删除后，后续无法计算数据源用户 ID 列表，导致数据清理失败
        # 而且最后才删除租户用户也不合适，因为租户用户是下游数据，应该最先被回收
        data_source_user_ids = [
            u.data_source_user_id
            for u in TenantUser.objects.filter(id__in=params["user_ids"], tenant_id=cur_tenant_id)
        ]

        with transaction.atomic():
            # 删除用户意味着租户用户 & 数据源用户都删除，前面检查过权限，
            # 因此这里所有协同产生的租户用户也需要删除（不等同步，立即生效）
            TenantUser.objects.filter(data_source_user_id__in=data_source_user_ids).delete()
            # 删除部门 - 用户关系中，用户是待删除用户的
            DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids).delete()
            # 删除用户 - leader 关系中，用户是待删除用户的
            DataSourceUserLeaderRelation.objects.filter(user_id__in=data_source_user_ids).delete()
            # 删除用户 - leader 关系中，leader 是待删除用户的
            DataSourceUserLeaderRelation.objects.filter(leader_id__in=data_source_user_ids).delete()
            # 最后才是批量回收数据源用户
            DataSourceUser.objects.filter(id__in=data_source_user_ids).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

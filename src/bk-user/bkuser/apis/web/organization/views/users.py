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
from collections import defaultdict
from datetime import timedelta
from typing import Dict, List, Set

from django.conf import settings
from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.organization.serializers import (
    OptionalTenantUserListInputSLZ,
    OptionalTenantUserListOutputSLZ,
    TenantUserBatchCopyInputSLZ,
    TenantUserBatchCreateInputSLZ,
    TenantUserBatchDeleteInputSLZ,
    TenantUserBatchMoveInputSLZ,
    TenantUserCreateInputSLZ,
    TenantUserCreateOutputSLZ,
    TenantUserListInputSLZ,
    TenantUserListOutputSLZ,
    TenantUserOrganizationPathOutputSLZ,
    TenantUserPasswordResetInputSLZ,
    TenantUserRetrieveOutputSLZ,
    TenantUserSearchInputSLZ,
    TenantUserSearchOutputSLZ,
    TenantUserStatusUpdateOutputSLZ,
    TenantUserUpdateInputSLZ,
)
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.data_source.utils import gen_tenant_user_id
from bkuser.apps.notification.tasks import send_reset_password_to_user
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.sync.tasks import initialize_identity_info_and_send_notification
from bkuser.apps.tenant.constants import TenantUserStatus
from bkuser.apps.tenant.models import (
    Tenant,
    TenantDepartment,
    TenantUser,
    TenantUserCustomField,
    TenantUserValidityPeriodConfig,
    UserBuiltinField,
)
from bkuser.biz.organization import DataSourceUserHandler
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin


class OptionalTenantUserListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """可选租户用户列表（下拉框数据用）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = OptionalTenantUserListOutputSLZ

    def get_queryset(self) -> QuerySet[TenantUser]:
        # FIXME (su) 和 search api 一样，需要限制 limit = 20，不分页
        slz = OptionalTenantUserListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        queryset = TenantUser.objects.filter(
            data_source__owner_tenant_id=self.get_current_tenant_id(),
        ).select_related("data_source_user")
        if kw := params.get("keyword"):
            queryset = queryset.filter(
                Q(data_source_user__username__icontains=kw) | Q(data_source_user__full_name__icontains=kw)
            )

        if excluded_user_id := params.get("excluded_user_id"):
            queryset = queryset.exclude(id=excluded_user_id)

        return queryset.order_by("data_source_user__username")

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TenantUserSearchApi(CurrentUserTenantMixin, generics.ListAPIView):
    """搜索租户用户"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None
    # 限制搜索结果，只提供前 N 条记录，如果展示不完全，需要用户细化搜索条件
    search_limit = settings.ORGANIZATION_SEARCH_API_LIMIT

    def get_queryset(self) -> QuerySet[TenantUser]:
        slz = TenantUserSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        keyword = slz.validated_data["keyword"]

        # FIXME (su) 手机 & 邮箱过滤在 DB 加密后不可用，到时候再调整
        return (
            TenantUser.objects.filter(tenant_id=self.get_current_tenant_id())
            .filter(
                Q(data_source_user__username__icontains=keyword)
                | Q(data_source_user__full_name__icontains=keyword)
                | Q(data_source_user__email__icontains=keyword)
                | Q(data_source_user__phone__icontains=keyword)
            )
            .select_related("data_source", "data_source_user")[: self.search_limit]
        )

    def _get_user_organization_paths_map(self, tenant_users: QuerySet[TenantUser]) -> Dict[str, List[str]]:
        """获取租户部门的组织路径信息"""
        data_source_user_ids = [tenant_user.data_source_user_id for tenant_user in tenant_users]

        # 数据源用户 ID -> [数据源部门 ID1， 数据源部门 ID2]
        user_dept_id_map = defaultdict(list)
        for relation in DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids):
            user_dept_id_map[relation.user_id].append(relation.department_id)

        # 数据源部门 ID 集合
        data_source_dept_ids: Set[int] = set().union(*user_dept_id_map.values())

        # 数据源部门 ID -> 组织路径
        org_path_map = {}
        for dept_relation in DataSourceDepartmentRelation.objects.filter(
            department_id__in=data_source_dept_ids
        ).select_related("department"):
            dept_names = list(
                dept_relation.get_ancestors(include_self=True).values_list("department__name", flat=True)
            )
            org_path_map[dept_relation.department_id] = "/".join(dept_names)

        # 租户用户 ID -> 组织路径列表
        return {
            user.id: [
                org_path_map[dept_id]
                for dept_id in user_dept_id_map[user.data_source_user_id]
                if dept_id in org_path_map
            ]
            for user in tenant_users
        }

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="搜索租户用户",
        query_serializer=TenantUserSearchInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_users = self.get_queryset()
        context = {
            "tenant_name_map": {tenant.id: tenant.name for tenant in Tenant.objects.all()},
            "org_path_map": self._get_user_organization_paths_map(tenant_users),
        }
        resp_data = TenantUserSearchOutputSLZ(tenant_users, many=True, context=context).data
        return Response(resp_data, status=status.HTTP_200_OK)


class TenantUserListCreateApi(CurrentUserTenantMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    def get_queryset(self) -> QuerySet[TenantUser]:
        slz = TenantUserListInputSLZ(
            data=self.request.query_params,
            context={"tenant_id": self.get_current_tenant_id()},
        )
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        queryset = TenantUser.objects.select_related("data_source_user").filter(
            tenant_id=self.get_current_tenant_id(), data_source__owner_tenant_id=self.kwargs["id"]
        )
        if kw := params.get("keyword"):
            queryset = queryset.filter(
                Q(data_source_user__username__icontains=kw) | Q(data_source_user__full_name__icontains=kw)
            )

        tenant_dept_id = params["department_id"]
        # FIXME (su) 目前好像没办法只过滤不属于任何部门的用户？如果不指定部门就全捞出来吧
        recursive = params["recursive"] if tenant_dept_id else True

        if tenant_dept_id:
            tenant_dept = TenantDepartment.objects.get(id=tenant_dept_id, tenant_id=self.get_current_tenant_id())

            filter_dept_ids = [tenant_dept.data_source_department_id]
            # 如果指定递归查询，则需要找出所有子部门的 ID，用于后续过滤
            if recursive:
                dept_relation = DataSourceDepartmentRelation.objects.get(
                    department_id=tenant_dept.data_source_department_id
                )
                filter_dept_ids = list(
                    dept_relation.get_descendants(include_self=True).values_list("department_id", flat=True)
                )

            data_source_user_ids = DataSourceDepartmentUserRelation.objects.filter(
                department_id__in=filter_dept_ids
            ).values_list("user_id", flat=True)
            queryset = queryset.filter(data_source_user_id__in=data_source_user_ids)

        return queryset.order_by("data_source_user__username")

    def _get_tenant_users_depts_map(self, tenant_users: List[TenantUser]) -> Dict[str, List[str]]:
        """
        获取一批租户用户的部门信息

        :return: {租户用户 ID: [部门名称]}
        """
        tenant_id = self.get_current_tenant_id()

        # {数据源部门 ID: 数据源部门名称}
        data_source_dept_id_name_map = {
            dept.data_source_department_id: dept.data_source_department.name
            for dept in TenantDepartment.objects.filter(tenant_id=tenant_id).select_related("data_source_department")
        }

        data_source_user_ids = [u.data_source_user_id for u in tenant_users]
        # {数据源用户 ID: [数据源部门 ID1, 数据源部门 ID2]}
        data_source_user_dept_ids_map = defaultdict(list)
        for rel in DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids):
            data_source_user_dept_ids_map[rel.user_id].append(rel.department_id)

        return {
            user.id: [
                data_source_dept_id_name_map[dept_id]
                for dept_id in data_source_user_dept_ids_map.get(user.data_source_user_id, [])
            ]
            for user in tenant_users
        }

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="租户用户列表",
        query_serializer=TenantUserListInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_users = self.paginate_queryset(self.get_queryset())
        context = {"tenant_user_depts_map": self._get_tenant_users_depts_map(tenant_users)}
        return self.get_paginated_response(TenantUserListOutputSLZ(tenant_users, many=True, context=context).data)

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="创建租户用户",
        request_body=TenantUserCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: TenantUserCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()
        if self.kwargs["id"] != cur_tenant_id:
            raise error_codes.TENANT_USER_CREATE_FAILED.f(_("仅可创建属于当前租户的用户"))

        # 必须存在实名用户数据源才可以创建租户部门
        data_source = DataSource.objects.filter(owner_tenant_id=cur_tenant_id, type=DataSourceTypeEnum.REAL).first()
        if not data_source:
            raise error_codes.DATA_SOURCE_NOT_EXIST.f(_("当前租户不存在实名用户数据源"))
        if not data_source.is_local:
            raise error_codes.TENANT_USER_CREATE_FAILED.f(_("仅本地数据源支持创建用户"))

        # 创建租户用户参数校验
        slz = TenantUserCreateInputSLZ(
            data=request.data, context={"tenant_id": cur_tenant_id, "data_source_id": data_source.id}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        with transaction.atomic():
            # 创建数据源用户
            data_source_user = DataSourceUser.objects.create(
                data_source=data_source,
                code=data["username"],
                username=data["username"],
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                phone_country_code=data["phone_country_code"],
                logo=data["logo"],
                extras=data["extras"],
            )

            # 创建部门 - 用户关联边
            # 租户部门 ID —> 数据源部门 ID
            data_source_dept_ids = TenantDepartment.objects.filter(
                data_source=data_source, id__in=data["department_ids"]
            ).values_list("data_source_department_id", flat=True)
            dept_user_relations = [
                DataSourceDepartmentUserRelation(
                    department_id=dept_id, user_id=data_source_user.id, data_source=data_source
                )
                for dept_id in data_source_dept_ids
            ]
            if dept_user_relations:
                DataSourceDepartmentUserRelation.objects.bulk_create(dept_user_relations)

            # 创建用户 - 上级关联边
            # 租户用户 ID -> 数据源用户 ID
            data_source_leader_ids = TenantUser.objects.filter(
                data_source=data_source, id__in=data["leader_ids"]
            ).values_list("data_source_user_id", flat=True)
            user_leader_relations = [
                DataSourceUserLeaderRelation(user_id=data_source_user.id, leader_id=leader_id, data_source=data_source)
                for leader_id in data_source_leader_ids
            ]
            if user_leader_relations:
                DataSourceUserLeaderRelation.objects.bulk_create(user_leader_relations)

            # FIXME (su) 支持协同后，要对协同的租户也立即创建租户用户（目前只是对数据源所属租户做创建）
            # 创建租户用户
            tenant_user = TenantUser(
                id=gen_tenant_user_id(cur_tenant_id, data_source, data_source_user),
                tenant_id=cur_tenant_id,
                data_source=data_source,
                data_source_user=data_source_user,
            )
            cfg = TenantUserValidityPeriodConfig.objects.get(tenant_id=cur_tenant_id)
            if cfg.enabled and cfg.validity_period > 0:
                tenant_user.account_expired_at = timezone.now() + timedelta(days=cfg.validity_period)

            tenant_user.save()

        # 对新增的用户进行账密信息初始化 & 发送密码通知
        initialize_identity_info_and_send_notification.delay(data_source.id)
        return Response(TenantUserCreateOutputSLZ(tenant_user).data, status=status.HTTP_201_CREATED)


class TenantUserRetrieveUpdateDestroyApi(
    CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"
    serializer_class = TenantUserRetrieveOutputSLZ

    def get_queryset(self) -> QuerySet[TenantUser]:
        return TenantUser.objects.filter(
            tenant_id=self.get_current_tenant_id(),
        ).select_related("data_source", "data_source_user")

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="获取租户用户详情",
        responses={status.HTTP_200_OK: TenantUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def _update_user_department_relations(self, user: DataSourceUser, dept_ids: List[int]) -> None:
        exists_dept_ids = DataSourceDepartmentUserRelation.objects.filter(
            user=user,
        ).values_list("department_id", flat=True)

        waiting_create_dept_ids = set(dept_ids) - set(exists_dept_ids)
        waiting_delete_dept_ids = set(exists_dept_ids) - set(dept_ids)

        if waiting_create_dept_ids:
            relations = [
                DataSourceDepartmentUserRelation(department_id=dept_id, user=user, data_source=user.data_source)
                for dept_id in waiting_create_dept_ids
            ]
            DataSourceDepartmentUserRelation.objects.bulk_create(relations)

        if waiting_delete_dept_ids:
            DataSourceDepartmentUserRelation.objects.filter(
                user=user, department_id__in=waiting_delete_dept_ids
            ).delete()

    def _update_user_leader_relations(self, user: DataSourceUser, leader_ids: List[int]) -> None:
        exists_leader_ids = DataSourceUserLeaderRelation.objects.filter(user=user).values_list("leader_id", flat=True)

        waiting_create_leader_ids = set(leader_ids) - set(exists_leader_ids)
        waiting_delete_leader_ids = set(exists_leader_ids) - set(leader_ids)

        if waiting_create_leader_ids:
            relations = [
                DataSourceUserLeaderRelation(user=user, leader_id=leader_id, data_source=user.data_source)
                for leader_id in waiting_create_leader_ids
            ]
            DataSourceUserLeaderRelation.objects.bulk_create(relations)

        if waiting_delete_leader_ids:
            DataSourceUserLeaderRelation.objects.filter(user=user, leader_id__in=waiting_delete_leader_ids).delete()

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="更新租户用户信息",
        request_body=TenantUserUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()
        tenant_user = self.get_object()
        data_source = tenant_user.data_source
        data_source_user = tenant_user.data_source_user

        if not (data_source.is_local and data_source.is_real_type):
            raise error_codes.TENANT_USER_UPDATE_FAILED.f(_("仅本地实名数据源支持更新用户信息"))
        # 如果数据源不是当前租户的，说明该租户用户是协同产生的
        if data_source.owner_tenant_id != cur_tenant_id:
            raise error_codes.TENANT_USER_UPDATE_FAILED.f(_("仅可删除非协同产生的租户用户"))

        slz = TenantUserUpdateInputSLZ(
            data=request.data,
            context={
                "tenant_id": cur_tenant_id,
                "tenant_user_id": tenant_user.id,
                "data_source_id": data_source.id,
                "data_source_user_id": data_source_user.id,
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 特殊逻辑：部分历史数据不允许更新用户名
        if data_source.is_username_frozen and data["username"] != data_source_user.username:
            raise error_codes.TENANT_USER_UPDATE_FAILED.f(_("当前用户不允许更新用户名"))

        # 提前将参数中的租户部门/ Leader 用户 ID 转换成数据源部门/ Leader 用户 ID
        data_source_dept_ids = TenantDepartment.objects.filter(
            data_source=data_source, id__in=data["department_ids"]
        ).values_list("data_source_department_id", flat=True)
        data_source_leader_ids = TenantUser.objects.filter(
            data_source=data_source, id__in=data["leader_ids"]
        ).values_list("data_source_user_id", flat=True)

        with transaction.atomic():
            data_source_user.username = data["username"]
            data_source_user.full_name = data["full_name"]
            data_source_user.email = data["email"]
            data_source_user.phone = data["phone"]
            data_source_user.phone_country_code = data["phone_country_code"]
            data_source_user.logo = data["logo"]
            data_source_user.extras = data["extras"]
            data_source_user.save()
            # 更新 部门 - 用户，Leader - 用户 关联表信息
            self._update_user_department_relations(data_source_user, data_source_dept_ids)
            self._update_user_leader_relations(data_source_user, data_source_leader_ids)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        data_source = tenant_user.data_source

        if not (data_source.is_local and data_source.is_real_type):
            raise error_codes.TENANT_USER_DELETE_FAILED.f(_("仅本地实名数据源支持删除用户"))
        # 如果数据源不是当前租户的，说明该租户用户是协同产生的
        if data_source.owner_tenant_id != self.get_current_tenant_id():
            raise error_codes.TENANT_USER_DELETE_FAILED.f(_("仅可删除非协同产生的租户用户"))

        data_source_user = tenant_user.data_source_user
        with transaction.atomic():
            # 删除用户意味着租户用户 & 数据源用户都删除，前面检查过权限，
            # 因此这里所有协同产生的租户用户也需要删除（不等同步，立即生效）
            TenantUser.objects.filter(data_source_user=data_source_user).delete()
            DataSourceDepartmentUserRelation.objects.filter(user=data_source_user).delete()
            DataSourceUserLeaderRelation.objects.filter(user=data_source_user).delete()
            DataSourceUserLeaderRelation.objects.filter(leader=data_source_user).delete()
            data_source_user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserPasswordResetApi(CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[TenantUser]:
        return TenantUser.objects.filter(tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="重置租户用户密码",
        request_body=TenantUserPasswordResetInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        data_source_user = tenant_user.data_source_user
        data_source = tenant_user.data_source
        plugin_config = data_source.get_plugin_cfg()

        if not (data_source.is_local and data_source.is_real_type and plugin_config.enable_password):
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(
                _("仅可以重置 已经启用密码功能 的 本地数据源 的用户密码")
            )

        slz = TenantUserPasswordResetInputSLZ(
            data=request.data,
            context={
                "plugin_config": plugin_config,
                "data_source_user_id": data_source_user.id,
            },
        )
        slz.is_valid(raise_exception=True)
        raw_password = slz.validated_data["password"]

        DataSourceUserHandler.update_password(
            data_source_user=data_source_user,
            password=raw_password,
            valid_days=plugin_config.password_expire.valid_time,
            operator=request.user.username,
        )

        # 发送新密码通知到用户
        send_reset_password_to_user.delay(data_source_user.id, raw_password)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserOrganizationPathListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """获取租户用户所属部门组织路径"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[TenantUser]:
        return TenantUser.objects.filter(tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="租户用户所属部门的部门路径",
        responses={status.HTTP_200_OK: TenantUserOrganizationPathOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant_user = self.get_object()

        data_source_dept_ids = DataSourceDepartmentUserRelation.objects.filter(
            user_id=tenant_user.data_source_user.id,
        ).values_list("department_id", flat=True)

        organization_paths: List[str] = []
        # NOTE: 用户部门数量不会很多，且该 API 调用不频繁，这里的 N+1 问题可以先不处理
        for dept_relation in DataSourceDepartmentRelation.objects.filter(department_id__in=data_source_dept_ids):
            dept_names = list(
                dept_relation.get_ancestors(include_self=True).values_list("department__name", flat=True)
            )
            organization_paths.append("/".join(dept_names))

        return Response(
            TenantUserOrganizationPathOutputSLZ({"organization_paths": organization_paths}).data,
            status=status.HTTP_200_OK,
        )


class TenantUserStatusUpdateApi(CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    """修改租户用户状态"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[TenantUser]:
        return TenantUser.objects.filter(tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="修改租户用户状态",
        responses={status.HTTP_200_OK: TenantUserStatusUpdateOutputSLZ()},
    )
    def put(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        # 正常 / 过期的租户用户都可以停用
        if tenant_user.status in [TenantUserStatus.ENABLED, TenantUserStatus.EXPIRED]:
            tenant_user.status = TenantUserStatus.DISABLED

        elif tenant_user.status == TenantUserStatus.DISABLED:
            # 启用的时候需要根据租户有效期判断，如果过期则转换为过期，否则转换为正常
            if timezone.now() > tenant_user.account_expired_at:
                tenant_user.status = TenantUserStatus.EXPIRED
            else:
                tenant_user.status = TenantUserStatus.ENABLED

        tenant_user.updater = request.user.username
        tenant_user.save(update_fields=["status", "updater", "updated_at"])
        return Response(TenantUserStatusUpdateOutputSLZ(tenant_user).data, status=status.HTTP_200_OK)


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

        slz = TenantUserBatchCreateInputSLZ(
            data=request.data,
            context={
                # 默认的内置字段，虽然邮箱 & 手机在 DB 中不是必填，但是在
                # 快速录入场景中要求必填，手机国际区号与手机号合并，不需要单独提供
                "required_builtin_fields": UserBuiltinField.objects.exclude(name="phone_country_code"),
                "required_custom_fields": TenantUserCustomField.objects.filter(tenant_id=cur_tenant_id, required=True),
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_dept = (
            TenantDepartment.objects.select_related("data_source")
            .filter(id=data["department_id"], tenant_id=cur_tenant_id)
            .first()
        )
        if not tenant_dept:
            raise error_codes.TENANT_USER_CREATE_FAILED.f(_("指定的租户部门不存在"))

        tenant_id = tenant_dept.tenant_id
        data_source = tenant_dept.data_source
        data_source_dept = tenant_dept.data_source_department

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
                DataSourceDepartmentUserRelation(user=user, department=data_source_dept, data_source=data_source)
                for user in data_source_users
            ]
            DataSourceDepartmentUserRelation.objects.bulk_create(relations)

            # 新建租户用户
            # FIXME (su) 支持协同后，要对协同的租户也立即创建租户用户（目前只是对数据源所属租户做创建）
            tenant_users = [
                TenantUser(
                    id=gen_tenant_user_id(tenant_id, data_source, user),
                    tenant_id=tenant_dept.tenant_id,
                    data_source=data_source,
                    data_source_user=user,
                )
                for user in data_source_users
            ]
            TenantUser.objects.bulk_create(tenant_users)

        return Response(status=status.HTTP_201_CREATED)


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

        data_source_user_ids = TenantUser.objects.filter(
            id__in=params["user_ids"], tenant_id=cur_tenant_id
        ).values_list("data_source_user", flat=True)

        with transaction.atomic():
            # 删除用户意味着租户用户 & 数据源用户都删除，前面检查过权限，
            # 因此这里所有协同产生的租户用户也需要删除（不等同步，立即生效）
            TenantUser.objects.filter(data_source_user_id__in=data_source_user_ids).delete()
            DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids).delete()
            DataSourceUserLeaderRelation.objects.filter(user_id__in=data_source_user_ids).delete()
            DataSourceUserLeaderRelation.objects.filter(leader_id__in=data_source_user_ids).delete()
            DataSourceUser.objects.filter(id__in=data_source_user_ids).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

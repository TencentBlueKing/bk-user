# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except
in compliance with the License. You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific language governing permissions and
limitations under the License.

We undertake not to change the open source license (MIT license) applicable
to the current version of the project delivered to anyone in the future.
"""
import logging

from rest_framework.permissions import BasePermission

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.natural_user.models import DataSourceUserNaturalUserRelation
from bkuser.apps.permission.constants import PermAction, UserRole
from bkuser.apps.tenant.models import Tenant, TenantManager, TenantUser

logger = logging.getLogger(__name__)


def perm_class(action: PermAction):  # noqa: C901
    """构建 DRF 可用的应用权限类"""

    class Permission(BasePermission):
        def has_permission(self, request, view):
            username = request.user.username
            cur_tenant_id = request.user.get_property("tenant_id")

            if action == PermAction.MANAGE_PLATFORM:
                return is_super_manager(cur_tenant_id, username)
            if action == PermAction.MANAGE_TENANT:
                return is_tenant_manager(cur_tenant_id, username)
            if action == PermAction.USE_PLATFORM:
                # 平台使用的情况，需要用具体的 object 来判断权限
                return True

            return False

        def has_object_permission(self, request, view, obj):
            if isinstance(obj, Tenant):
                tenant_id = obj.id
            elif hasattr(obj, "tenant_id"):
                tenant_id = obj.tenant_id
            elif isinstance(obj, DataSource):
                # TODO (su) 考虑数据源协同的情况
                tenant_id = obj.owner_tenant_id
            elif hasattr(obj, "data_source"):
                # TODO (su) 考虑数据源协同的情况
                tenant_id = obj.data_source.owner_tenant_id
            else:
                logger.exception("failed to get tenant id, obj: %s", obj)
                return False

            username = request.user.username
            cur_tenant_id = request.user.get_property("tenant_id")
            if action == PermAction.MANAGE_PLATFORM:
                return is_super_manager(tenant_id, username)
            if action == PermAction.MANAGE_TENANT:
                return is_tenant_manager(tenant_id, username)
            if action == PermAction.USE_PLATFORM:
                # 当前平台使用（普通用户）能编辑的资源只有 TenantUser
                if not isinstance(obj, TenantUser):
                    return False

                return is_same_nature_user(obj.id, cur_tenant_id, username)

            return False

    return Permission


def is_super_manager(tenant_id: str, username: str) -> bool:
    """默认租户的管理员，有管理平台的权限（超级管理员）"""
    tenant = Tenant.objects.get(id=tenant_id)
    if not tenant.is_default:
        return False

    return TenantManager.objects.filter(tenant=tenant, tenant_user_id=username).exists()


def is_tenant_manager(tenant_id: str, username: str) -> bool:
    """本租户的管理员，拥有管理当前租户配置的权限"""
    tenant = Tenant.objects.get(id=tenant_id)
    return TenantManager.objects.filter(tenant=tenant, tenant_user_id=username).exists()


def is_same_nature_user(req_username: str, cur_tenant_id: str, username: str) -> bool:
    """判断是否同一自然人（可以跨租户访问属于同一自然人/数据源用户的数据）

    :param req_username: 待访问租户用户名
    :param cur_tenant_id: 当前用户的租户 ID
    :param username: 当前用户的用户名
    """
    cur_tenant_user = TenantUser.objects.filter(tenant_id=cur_tenant_id, id=username).first()
    # 当前登录的，连租户用户都不是，自然不是自然人
    if not cur_tenant_user:
        return False

    # 数据用户源若绑定到自然人，只可能有一条记录
    relation = DataSourceUserNaturalUserRelation.objects.filter(
        data_source_user=cur_tenant_user.data_source_user
    ).first()

    # 如果没有绑定自然人，则将同一数据源用户关联的租户用户，都视作一个自然人
    if not relation:
        return TenantUser.objects.filter(id=req_username, data_source_user=cur_tenant_user.data_source_user).exists()

    data_source_user_ids = DataSourceUserNaturalUserRelation.objects.filter(
        natural_user=relation.natural_user
    ).values_list("data_source_user_id", flat=True)
    return TenantUser.objects.filter(id=req_username, data_source_user__in=data_source_user_ids).exists()


def get_user_role(tenant_id: str, username: str) -> UserRole:
    """获取用户角色，因目前超级管理员必定是租户管理员，租户管理员必定是普通用户，因此返回最高级的角色即可"""
    tenant = Tenant.objects.get(id=tenant_id)

    if TenantManager.objects.filter(tenant=tenant, tenant_user_id=username).exists():
        if tenant.is_default:
            return UserRole.SUPER_MANAGER

        return UserRole.TENANT_MANAGER

    return UserRole.NATURAL_USER

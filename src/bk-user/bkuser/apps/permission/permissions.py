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

from bkuser.apps.data_source.models import DataSource, DataSourcePlugin
from bkuser.apps.idp.models import Idp, IdpPlugin
from bkuser.apps.natural_user.models import DataSourceUserNaturalUserRelation
from bkuser.apps.permission.constants import PermAction, UserRole
from bkuser.apps.tenant.models import CollaborationStrategy, Tenant, TenantManager, TenantUser

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

        def has_object_permission(self, request, view, obj):  # noqa: C901
            username = request.user.username
            cur_tenant_id = request.user.get_property("tenant_id")

            # 校验平台权限，只需要校验是否超级管理员，与数据对象无关
            if action == PermAction.MANAGE_PLATFORM:
                return is_super_manager(cur_tenant_id, username)

            # 普通用户权限
            if action == PermAction.USE_PLATFORM:
                # 当前平台使用（普通用户）能编辑的资源只有 TenantUser
                if not isinstance(obj, TenantUser):
                    return False

                return is_same_nature_user(obj.id, cur_tenant_id, username)

            # 租户权限与具体对象有关系的，需要根据具体对象确定关联的租户后再鉴权
            if action == PermAction.MANAGE_TENANT:
                # 协作策略比较特殊，只要是源 / 目标租户的管理员即可（Views 层会具体过滤）
                if isinstance(obj, CollaborationStrategy):
                    is_source_tenant_mgr = is_tenant_manager(obj.source_tenant_id, username)
                    is_target_tenant_mgr = is_tenant_manager(obj.target_tenant_id, username)
                    return is_source_tenant_mgr or is_target_tenant_mgr

                if isinstance(obj, Tenant):
                    tenant_id = obj.id
                elif hasattr(obj, "tenant_id"):
                    tenant_id = obj.tenant_id
                elif isinstance(obj, DataSource):
                    tenant_id = obj.owner_tenant_id
                elif hasattr(obj, "data_source"):
                    tenant_id = obj.data_source.owner_tenant_id
                elif isinstance(obj, Idp):
                    tenant_id = obj.owner_tenant_id
                elif isinstance(obj, (DataSourcePlugin, IdpPlugin)):
                    # 认证源插件和数据源插件的配置信息、默认配置等可能包含一些低敏感级别的信息，
                    # 所以需要确保用户可管理租户才可看到
                    tenant_id = cur_tenant_id
                else:
                    logger.exception("failed to get tenant id, obj: %s", obj)
                    return False

                return is_tenant_manager(tenant_id, username)

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
    return TenantManager.objects.filter(tenant_id=tenant_id, tenant_user_id=username).exists()


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

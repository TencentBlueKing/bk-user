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
import uuid

from bkuser.apps.data_source.constants import DEFAULT_DATA_SOURCE_NAME
from bkuser.apps.tenant.models import Tenant, TenantDataSourceRelationShip, TenantManager, TenantUser
from bkuser.biz.data_source_handler import data_source_handler
from bkuser.common.error_codes import error_codes
from django.db import transaction

from bkuser.utils.uuid import generate_uuid_str

logger = logging.getLogger(__name__)


class TenantHandler:

    def _is_exist(self, tenant_id: str) -> bool:
        """
        根据提供的租户id，判断租户是否存在
        """
        return Tenant.objects.filter(id=tenant_id).exists()

    def create_tenant(self, base_tenant_info: dict) -> Tenant:
        """
        创建租户
        """
        try:
            logger.info(f"Creating Tenant<{base_tenant_info['id']}-{base_tenant_info['name']}>")
            instance = Tenant.objects.create(
                id=base_tenant_info["id"],
                name=base_tenant_info["name"],
                enabled_user_count_display=base_tenant_info["enabled_user_count_display"],
                logo=base_tenant_info.get("logo", ""),
            )
            return instance
        except Exception as e:
            logger.exception(
                f"Creating Tenant<{base_tenant_info['id']}-{base_tenant_info['name']}> Failed, exception:{e}")
            raise error_codes.CREATE_TENANT_FAILED

    def data_source_bind_tenant(self, tenant_id: str, data_source_id: int, is_init=False):
        if not is_init and not self._is_exist(tenant_id):
            logger.error(f"Tenant<{tenant_id}> is not existed")
            raise error_codes.TENANT_NOT_EXIST
        logger.info(f"Binding data_source<{data_source_id}> to tenant<{tenant_id}>")
        TenantDataSourceRelationShip.objects.create(tenant_id=tenant_id, data_source_id=data_source_id)

    def data_source_users_bind_tenant(
            self, tenant_id: str, data_source_users: list[dict], is_init=False
    ) -> list[TenantUser]:
        """
        数据源用户绑定租户
        """
        if not is_init and not self._is_exist(tenant_id):
            logger.error(f"Tenant<{tenant_id}> is not existed")
            raise error_codes.TENANT_NOT_EXIST
        tenant_user_objects: list[TenantUser] = [
            TenantUser(
                id=generate_uuid_str(),
                tenant_id=tenant_id,
                data_source_user_id=user["id"],
                username=user["username"],
            )
            for user in data_source_users
        ]
        try:
            tenant_users = TenantUser.objects.bulk_create(tenant_user_objects)
            return tenant_users
        except Exception as e:
            logger.exception(f"Binding user to Tenant<{tenant_id}> failed, exception:{e}")
            raise error_codes.BIND_TENANT_USER_FAILED

    def update_tenant_managers(self, tenant_id: str, users: list[str], is_init=False) -> list[TenantManager]:
        """
        更新租户管理员
        """
        if not is_init and not self._is_exist(tenant_id):
            logger.error(f"Tenant<{tenant_id}> is not existed")
            raise error_codes.TENANT_NOT_EXIST

        tenant_users = TenantUser.objects.filter(id__in=users, tenant_id=tenant_id).values_list("id", flat=True)
        not_exist_users = set(list(tenant_users)) - set(users)
        if not_exist_users:
            logger.error(f"update managers for tenant failed, get not_exist_user. counts: {len(not_exist_users)}")
            raise error_codes.TENANT_USER_NOT_EXIST

        current_managers = TenantManager.objects.filter(
            tenant_user_id__in=users,
            tenant_id=tenant_id
        ).values_list("tenant_user_id", flat=True)
        # 新旧租户管理员比对
        # 移除管理员
        manager_to_del = list(set(current_managers) - set(users))
        if manager_to_del:
            TenantManager.objects.filter(tenant_id=tenant_id, tenant_user_id__in=manager_to_del).delete()

        # 过滤出新管理员
        new_manager = list(set(users) - set(current_managers))
        if new_manager:
            logger.info(f"new managers<count:{len(new_manager)}> for tenant<{tenant_id}>")
            tenant_managers_objects: list[TenantManager] = []
            for manager_id in new_manager:
                tenant_managers_objects.append(TenantManager(tenant_id=tenant_id, tenant_user_id=manager_id))
            try:
                tenant_managers = TenantManager.objects.bulk_create(tenant_managers_objects)
                return tenant_managers
            except Exception as e:
                logger.exception(f"update managers for tenant<{tenant_id}> failed, exception: {e}")
                raise error_codes.UPDATE_TENANT_MANAGERS_FAILED

    def update_tenant(self, tenant: Tenant, update_data: dict) -> Tenant:
        """
        更新租户基础信息
        """
        # 限制不能更新租户ID
        model_fields_keys = [x.name for x in tenant._meta.get_fields() if x.name != "id"]
        for key, new_value in update_data.items():
            if key not in model_fields_keys:
                continue
            value = getattr(tenant, key)
            if value != new_value:
                setattr(tenant, key, new_value)
        try:
            tenant.save()
            return tenant
        except Exception as e:
            logger.exception(f"update tenant info failed, exception: {e}")
            raise error_codes.UPDATE_TENANT_FAILED

    def init_tenant_with_managers(self, init_tenant_data: dict) -> Tenant:

        with transaction.atomic():
            # 初始化租户
            tenant = tenant_handler.create_tenant(init_tenant_data)
            # 初始化本地数据源（密码配置初始化，需要根据tenant_data的manager_password进行，owner为当前租户，命名为本地数据源）
            data_source = data_source_handler.create_data_source(name=DEFAULT_DATA_SOURCE_NAME, owner=tenant.id)
            # 更新初始化后的数据源密码配置
            password_settings: dict = init_tenant_data["password_settings"]
            data_source_handler.update_plugin_config(
                instance=data_source,
                update_settings=password_settings,
                namespace="password"
            )

        with transaction.atomic():
            # 初始化管理员在数据源的信息
            # 创建数据源用户
            new_users: list[dict] = init_tenant_data["managers"]
            username_list = data_source_handler.create_data_source_users(data_source, new_users)

        # 租户用户初始化
        data_source_users = data_source_handler.filter_users(
            data_source_id=data_source.id, username__in=username_list
        ).values("id", "username")
        with transaction.atomic():
            # 绑定到数据源到租户
            tenant_handler.data_source_bind_tenant(data_source_id=data_source.id, tenant_id=tenant.id)
            # 从数据源绑定管理员到租户
            tenant_users = tenant_handler.data_source_users_bind_tenant(tenant.id, data_source_users, is_init=True)
            # 绑定权限
            manager_ids = [user.id for user in tenant_users]
            tenant_handler.update_tenant_managers(tenant.id, manager_ids, is_init=True)

        return tenant


tenant_handler = TenantHandler()

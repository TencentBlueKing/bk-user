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

from bkuser.apps.tenant.models import Tenant, TenantUser, TenantManager, TenantDataSourceRelationShip
from bkuser.common.error_codes import error_codes

logger = logging.getLogger(__name__)


class TenantHandler:
    def _generate_uuid(self):
        return str(uuid.uuid1())

    def _is_existed(self, tenant_id: str) -> bool:
        return Tenant.objects.filter(id=tenant_id).exists()

    def create_tenant(self, tenant: dict) -> Tenant:
        """
        创建租户
        """
        try:
            instance = Tenant.objects.create(
                id=tenant["id"],
                name=tenant["name"],
                enabled_user_count_display=tenant["enabled_user_count_display"],
                logo=tenant.get("logo", ""),
            )
            return instance
        except Exception as e:
            logger.exception(f"Creating Tenant<{tenant['id']}-{tenant['name']}> Failed, exception:{e}")
            raise error_codes.CREATE_TENANT_FAILED

    def data_source_bind_tenant(self, tenant_id: str, data_source_id: int, is_init=False):
        if not is_init and not self._is_existed(tenant_id):
            raise error_codes.TENANT_NOT_EXIST
        return TenantDataSourceRelationShip.objects.create(tenant_id=tenant_id, data_source_id=data_source_id)

    def data_source_users_bind_tenant(
        self, tenant_id: str, data_source_users: list[dict], is_init=False
    ) -> list[TenantUser]:
        """
        数据源用户绑定租户
        """
        if not is_init and not self._is_existed(tenant_id):
            raise error_codes.TENANT_NOT_EXIST
        tenant_user_objects: list[TenantUser] = [
            TenantUser(
                id=self._generate_uuid(),
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
        if not is_init and not self._is_existed(tenant_id):
            raise error_codes.TENANT_NOT_EXIST

        tenant_users = TenantUser.objects.filter(id__in=users, tenant_id=tenant_id).values_list("id", flat=True)
        not_exist_users = set([str(item) for item in tenant_users]) - set(users)
        if not_exist_users:
            logger.error(f"update managers for tenant failed, get not_exist_users: {len(not_exist_users)}")
            raise error_codes.TENANT_USER_NOT_EXIST

        # 新旧租户管理员比对
        current_managers = TenantManager.objects.filter(tenant_user_id__in=users, tenant_id=tenant_id)

        manager_to_del = set(current_managers) - set(users)
        if manager_to_del:
            TenantManager.objects.filter(tenant_id=tenant_id, tenant_user_id__in=manager_to_del).delete()

        # 过滤出新管理员
        new_manager = set(users) - set(tenant_users)
        if new_manager:
            tenant_managers_objects: list[TenantManager] = []
            for manager_id in list(new_manager):
                tenant_managers_objects.append(TenantManager(tenant_id=tenant_id, tenant_user_id=manager_id))
            try:
                tenant_managers = TenantManager.objects.bulk_create(tenant_managers_objects)
                return tenant_managers
            except Exception as e:
                logger.exception(f"update managers for tenant<{tenant_id}> failed, exception: {e}")
                raise error_codes.UPDATE_TENANT_MANAGERS_FAILED

    def update_tenant(self, tenant: Tenant, update_data: dict):
        model_fields_keys = [x.name for x in tenant._meta.get_fields() if x.name != "id"]
        # 限制不能更新租户ID
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


tenant_handler = TenantHandler()

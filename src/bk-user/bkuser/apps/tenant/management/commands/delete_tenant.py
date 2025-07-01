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

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceSensitiveInfo,
    DataSourceUser,
    DataSourceUserLeaderRelation,
    DepartmentRelationMPTTTree,
)
from bkuser.apps.idp.models import Idp, IdpSensitiveInfo
from bkuser.apps.tenant.models import (
    CollaborationStrategy,
    Tenant,
    TenantCommonVariable,
    TenantDepartment,
    TenantDepartmentIDRecord,
    TenantManager,
    TenantUser,
    TenantUserCustomField,
    TenantUserDisplayNameExpressionConfig,
    TenantUserIDGenerateConfig,
    TenantUserIDRecord,
    TenantUserValidityPeriodConfig,
    VirtualUserAppRelation,
    VirtualUserOwnerRelation,
)


class Command(BaseCommand):
    """
    Delete tenant and all related data
    $ python manage.py delete_tenant
    """

    def add_arguments(self, parser):
        parser.add_argument("--tenant_id", type=str, help="Tenant ID to delete", required=True)

    def handle(self, *args, **options):
        tenant_id = options["tenant_id"]

        # Check if tenant exists
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            raise CommandError(f"Tenant {tenant_id} does not exist")

        self.stdout.write(f"\nDeleting tenant '{tenant.name}' ({tenant.id})")

        # Execute deletion
        try:
            self._delete_tenant_and_related_data(tenant)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully deleted tenant '{tenant.name}' ({tenant_id}) and all related data")
            )
        except Exception as e:
            raise CommandError(f"Failed to delete tenant: {e}")

    def _delete_tenant_and_related_data(self, tenant: Tenant):
        """Delete tenant and all related data"""
        with transaction.atomic():
            # 1. Delete virtual user relations
            tenant_user_ids = list(TenantUser.objects.filter(tenant=tenant).values_list("id", flat=True))
            VirtualUserAppRelation.objects.filter(tenant_user_id__in=tenant_user_ids).delete()
            VirtualUserOwnerRelation.objects.filter(
                Q(tenant_user_id__in=tenant_user_ids) | Q(owner_id__in=tenant_user_ids)
            ).delete()

            # 2. Delete tenant user custom fields
            TenantUserCustomField.objects.filter(tenant=tenant).delete()

            # 3. Delete tenant configurations
            try:
                TenantUserValidityPeriodConfig.objects.get(tenant=tenant).delete()
            except TenantUserValidityPeriodConfig.DoesNotExist:
                pass

            try:
                TenantUserDisplayNameExpressionConfig.objects.get(tenant=tenant).delete()
            except TenantUserDisplayNameExpressionConfig.DoesNotExist:
                pass

            # 4. Delete tenant managers
            TenantManager.objects.filter(tenant=tenant).delete()

            # 5. Delete collaboration strategies
            CollaborationStrategy.objects.filter(Q(source_tenant=tenant) | Q(target_tenant=tenant)).delete()

            # 6. Delete identity providers and sensitive info
            idps = Idp.objects.filter(owner_tenant_id=tenant.id)
            idp_ids = list(idps.values_list("id", flat=True))
            IdpSensitiveInfo.objects.filter(idp_id__in=idp_ids).delete()
            idps.delete()

            # 7. Delete data sources and related resources (includes all tenant users and departments)
            data_sources = DataSource.objects.filter(owner_tenant_id=tenant.id)
            for data_source in data_sources:
                try:
                    self._delete_data_source_and_related_resources(data_source)
                except Exception:
                    pass

            # 8. Delete tenant user ID records
            TenantUserIDRecord.objects.filter(tenant=tenant).delete()

            # 9. Delete tenant department ID records
            TenantDepartmentIDRecord.objects.filter(tenant=tenant).delete()

            # 10. Delete tenant user ID generation configs
            TenantUserIDGenerateConfig.objects.filter(target_tenant=tenant).delete()

            # 11. Delete tenant common variables
            TenantCommonVariable.objects.filter(tenant=tenant).delete()

            # 12. Finally delete the tenant itself
            tenant.delete()

    def _delete_data_source_and_related_resources(self, data_source: DataSource):
        """Delete data source and all related resources"""
        # Delete tenant-related model data
        TenantDepartment.objects.filter(data_source=data_source).delete()
        TenantUser.objects.filter(data_source=data_source).delete()
        TenantUserIDGenerateConfig.objects.filter(data_source=data_source).delete()
        TenantUserIDRecord.objects.filter(data_source=data_source).delete()
        TenantDepartmentIDRecord.objects.filter(data_source=data_source).delete()

        # Delete data source-related model data
        DataSourceDepartmentUserRelation.objects.filter(data_source=data_source).delete()
        DataSourceDepartmentRelation.objects.filter(data_source=data_source).delete()
        DataSourceDepartment.objects.filter(data_source=data_source).delete()
        DataSourceUserLeaderRelation.objects.filter(data_source=data_source).delete()
        DataSourceUser.objects.filter(data_source=data_source).delete()
        DepartmentRelationMPTTTree.objects.filter(data_source=data_source).delete()
        DataSourceSensitiveInfo.objects.filter(data_source=data_source).delete()
        data_source.delete()

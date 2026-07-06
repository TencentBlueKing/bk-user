# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from datetime import timedelta
from typing import List

from django.db import transaction
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.open_provider.constants import PROVIDER_BATCH_SIZE
from bkuser.apis.open_provider.mixins import ProviderApiCommonMixin
from bkuser.apis.open_provider.serializers.user import (
    UserBatchCreateInputSLZ,
    UserBatchDeleteInputSLZ,
    UserBatchUpdateInputSLZ,
)
from bkuser.apis.open_provider.validators import (
    raise_if_errors,
    validate_create_users_unique,
    validate_update_users_unique,
    validate_user_create_data,
    validate_user_extras,
    validate_user_update_data,
)
from bkuser.apps.data_source.models import (
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.constants import CollaborationStrategyStatus
from bkuser.apps.tenant.models import (
    CollaborationStrategy,
    TenantUser,
    TenantUserCustomField,
    TenantUserValidityPeriodConfig,
)
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.common.constants import PERMANENT_TIME

logger = logging.getLogger(__name__)


class UserBatchApi(ProviderApiCommonMixin, generics.GenericAPIView):
    """用户批量增删改"""

    BULK_CREATE_BATCH_SIZE = PROVIDER_BATCH_SIZE

    @swagger_auto_schema(
        tags=["open_provider.user"],
        operation_id="provider_batch_create_user",
        operation_description="批量创建用户",
        request_body=UserBatchCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: ""},
    )
    def post(self, request, *args, **kwargs):
        slz = UserBatchCreateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.data_source
        tenant_id = self.tenant_id

        # 字段格式校验
        errors: List[str] = []
        custom_fields = TenantUserCustomField.objects.filter(tenant_id=tenant_id)
        for user_info in data["users"]:
            errors += validate_user_create_data(user_info, data_source)
            if user_info.get("extras"):
                errors += validate_user_extras(user_info["id"], user_info["extras"], custom_fields, data_source.id)

        # 唯一性校验
        errors += validate_create_users_unique(data["users"], data_source)
        raise_if_errors(errors)

        with transaction.atomic():
            data_source_users = [
                DataSourceUser(
                    data_source=data_source,
                    code=user_info["id"],
                    username=user_info["username"],
                    full_name=user_info["full_name"],
                    email=user_info["email"],
                    phone=user_info["phone"],
                    phone_country_code=user_info["phone_country_code"],
                    extras=user_info["extras"],
                )
                for user_info in data["users"]
            ]
            DataSourceUser.objects.bulk_create(data_source_users, batch_size=self.BULK_CREATE_BATCH_SIZE)

            codes = [u["id"] for u in data["users"]]
            data_source_users = DataSourceUser.objects.filter(data_source=data_source, code__in=codes)

            self._bulk_create_tenant_users(tenant_id, data_source, data_source_users)

        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=["open_provider.user"],
        operation_id="provider_batch_update_user",
        operation_description="批量更新用户",
        request_body=UserBatchUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = UserBatchUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.data_source
        tenant_id = self.tenant_id

        # 字段格式校验
        errors: List[str] = []
        custom_fields = TenantUserCustomField.objects.filter(tenant_id=tenant_id)
        for user_info in data["users"]:
            errors += validate_user_update_data(user_info)
            if "extras" in user_info and user_info["extras"]:
                # 更新时需要知道对应的 data_source_user_id 以便唯一性排除自身
                ds_user = DataSourceUser.objects.filter(data_source=data_source, code=user_info["id"]).first()
                ds_user_id = ds_user.id if ds_user else None
                errors += validate_user_extras(
                    user_info["id"], user_info["extras"], custom_fields, data_source.id, ds_user_id
                )

        # username 唯一性校验
        errors += validate_update_users_unique(data["users"], data_source)
        raise_if_errors(errors)

        codes = [u["id"] for u in data["users"]]
        ds_users = DataSourceUser.objects.filter(data_source=data_source, code__in=codes)
        ds_user_map = {u.code: u for u in ds_users}

        users_to_update = self._apply_user_updates(data["users"], ds_user_map)

        with transaction.atomic():
            if users_to_update:
                DataSourceUser.objects.bulk_update(
                    users_to_update,
                    fields=["username", "full_name", "email", "phone", "phone_country_code", "extras", "updated_at"],
                    batch_size=self.BULK_CREATE_BATCH_SIZE,
                )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _apply_user_updates(users_data: List[dict], ds_user_map: dict) -> List[DataSourceUser]:
        """将更新数据应用到数据源用户对象上"""
        users_to_update: List[DataSourceUser] = []
        updatable_fields = ("username", "full_name", "email", "phone", "phone_country_code", "extras")
        for user_info in users_data:
            ds_user = ds_user_map.get(user_info["id"])
            if not ds_user:
                continue

            for field in updatable_fields:
                if field in user_info:
                    setattr(ds_user, field, user_info[field])

            users_to_update.append(ds_user)

        return users_to_update

    @swagger_auto_schema(
        tags=["open_provider.user"],
        operation_id="provider_batch_delete_user",
        operation_description="批量删除用户",
        request_body=UserBatchDeleteInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        slz = UserBatchDeleteInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.data_source

        data_source_user_ids = list(
            DataSourceUser.objects.filter(
                data_source=data_source,
                code__in=data["ids"],
            ).values_list("id", flat=True)
        )

        if not data_source_user_ids:
            return Response(status=status.HTTP_204_NO_CONTENT)

        with transaction.atomic():
            TenantUser.objects.filter(data_source_user_id__in=data_source_user_ids).delete()
            DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids).delete()
            DataSourceUserLeaderRelation.objects.filter(user_id__in=data_source_user_ids).delete()
            DataSourceUserLeaderRelation.objects.filter(leader_id__in=data_source_user_ids).delete()
            DataSourceUser.objects.filter(id__in=data_source_user_ids).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _bulk_create_tenant_users(self, tenant_id, data_source, data_source_users):
        """批量创建租户用户（含协同策略）"""
        now = timezone.now()
        tenant_user_account_expired_at_map = {
            cfg.tenant_id: now + timedelta(days=cfg.validity_period)
            for cfg in TenantUserValidityPeriodConfig.objects.filter(enabled=True, validity_period__gt=0)
        }

        generator = TenantUserIDGenerator(tenant_id, data_source, prepare_batch=True)
        tenant_users = [
            TenantUser(
                id=generator.gen(user),
                tenant_id=tenant_id,
                data_source=data_source,
                data_source_user=user,
                account_expired_at=tenant_user_account_expired_at_map.get(tenant_id, PERMANENT_TIME),
            )
            for user in data_source_users
        ]
        TenantUser.objects.bulk_create(tenant_users, batch_size=self.BULK_CREATE_BATCH_SIZE)

        collaboration_tenant_users: List[TenantUser] = []
        for strategy in CollaborationStrategy.objects.filter(
            source_tenant_id=tenant_id,
            source_status=CollaborationStrategyStatus.ENABLED,
            target_status=CollaborationStrategyStatus.ENABLED,
        ):
            collab_generator = TenantUserIDGenerator(strategy.target_tenant_id, data_source, prepare_batch=True)
            collaboration_tenant_users += [
                TenantUser(
                    id=collab_generator.gen(user),
                    tenant_id=strategy.target_tenant_id,
                    data_source=data_source,
                    data_source_user=user,
                    account_expired_at=tenant_user_account_expired_at_map.get(
                        strategy.target_tenant_id, PERMANENT_TIME
                    ),
                )
                for user in data_source_users
            ]

        if collaboration_tenant_users:
            TenantUser.objects.bulk_create(collaboration_tenant_users, batch_size=self.BULK_CREATE_BATCH_SIZE)

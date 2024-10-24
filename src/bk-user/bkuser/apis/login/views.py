# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

from collections import defaultdict
from typing import Any, Dict

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.response import Response

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, LocalDataSourceIdentityInfo
from bkuser.apps.idp.constants import IdpStatus
from bkuser.apps.idp.models import Idp
from bkuser.apps.tenant.constants import CollaborationStrategyStatus, TenantStatus
from bkuser.apps.tenant.models import CollaborationStrategy, Tenant, TenantUser
from bkuser.biz.idp import AuthenticationMatcher
from bkuser.common.error_codes import error_codes

from .mixins import LoginApiAccessControlMixin
from .serializers import (
    GlobalSettingOutputSLZ,
    IdpListOutputSLZ,
    IdpRetrieveOutputSLZ,
    LocalUserCredentialAuthenticateInputSLZ,
    LocalUserCredentialAuthenticateOutputSLZ,
    TenantListInputSLZ,
    TenantListOutputSLZ,
    TenantUserMatchInputSLZ,
    TenantUserMatchOutputSLZ,
    TenantUserRetrieveOutputSLZ,
)


class GlobalSettingListApi(LoginApiAccessControlMixin, generics.ListAPIView):
    pagination_class = None

    @staticmethod
    def _get_unique_enabled_tenant_idp() -> Dict | None:
        """
        查询唯一启用的租户认证源，当且仅当存在唯一 IDP 时才返回 IDP 信息，否则返回 None
        用途：辅助判断是否唯一启用租户，且唯一启用的第三方认证源
        """
        # 查询启用的租户列表
        tenant_ids = list(Tenant.objects.filter(status=TenantStatus.ENABLED).values_list("id", flat=True))
        if not tenant_ids:
            return None

        # 启用的认证源
        idps = Idp.objects.filter(status=IdpStatus.ENABLED, owner_tenant_id__in=tenant_ids).values(
            "id", "owner_tenant_id", "plugin_id", "data_source_id"
        )
        if len(idps) != 1:
            return None

        idp = idps[0]
        # 协同情况处理
        # 如果唯一 IDP 关联的数据源是非实名的，则说明该 IDP 只会被用于本租户，不会有其他租户协同的使用
        # 协同限制：非实名数据源不可被协同
        if not DataSource.objects.filter(id=idp["data_source_id"], type=DataSourceTypeEnum.REAL).exists():
            return idp

        target_tenant_ids = list(
            CollaborationStrategy.objects.filter(
                source_status=CollaborationStrategyStatus.ENABLED,
                target_status=CollaborationStrategyStatus.ENABLED,
                source_tenant_id=idp["owner_tenant_id"],
            ).values_list("target_tenant_id", flat=True)
        )
        # 有协同，且协同租户启用了，那就不是唯一认证源了
        if target_tenant_ids and len(set(target_tenant_ids) & set(tenant_ids)) > 0:
            return None

        return idp

    def get(self, request, *args, **kwargs):
        return Response(
            GlobalSettingOutputSLZ(
                {
                    "bk_user_url": settings.BK_USER_URL.rstrip("/"),
                    "unique_enabled_tenant_idp": self._get_unique_enabled_tenant_idp(),
                }
            ).data
        )


class LocalUserCredentialAuthenticateApi(LoginApiAccessControlMixin, generics.CreateAPIView):
    """本地数据源用户的凭据认证"""

    def post(self, request, *args, **kwargs):
        # TODO: 所有报错都添加日志，便于后续排查
        slz = LocalUserCredentialAuthenticateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # TODO: 密码错误次数检测&锁定，如何实现？
        #  不同数据源配置，key=(data_source_id, username)，错误次数如何计算？如何锁定？

        # 由于密码是Hash并加盐, 无法直接查询DB匹配，只能一个个遍历匹配
        users = LocalDataSourceIdentityInfo.objects.filter(
            data_source_id__in=data["data_source_ids"], username=data["username"]
        )
        matched_users = [u for u in users if u.check_password(data["password"])]

        # 无任何匹配
        if not matched_users:
            raise error_codes.USERNAME_OR_PASSWORD_WRONG_ERROR

        # Q: 为什么这里不对用户状态、数据源状态、“是否首次登录检测并强制修改” 等进行检测呢？
        # A: [单一职责] 这里只对用户的凭证进行认证，并不是与登录绑定
        #  多租户下，认证后的数据源用户，
        #  还需要根据匹配规则和租户信息等最终匹配到租户用户(即对外的蓝鲸用户)，这些是在登录流程里的

        # FIXME (nan): 密码过期检测，过期需要返回重置URI

        return Response(LocalUserCredentialAuthenticateOutputSLZ(instance=matched_users, many=True).data)


class TenantListApi(LoginApiAccessControlMixin, generics.ListAPIView):
    pagination_class = None
    serializer_class = TenantListOutputSLZ

    def get_serializer_context(self) -> Dict[str, Any]:
        # 双方都启用了才可用于登录
        strategies = CollaborationStrategy.objects.filter(
            source_status=CollaborationStrategyStatus.ENABLED, target_status=CollaborationStrategyStatus.ENABLED
        ).values("source_tenant_id", "target_tenant_id")

        # 所有启用的租户, 对于协同场景，不过滤不可见的
        tenant_map = {t.id: t for t in Tenant.objects.filter(status=TenantStatus.ENABLED)}

        # 每个租户对应的协同租户列表
        collaboration_tenant_map = defaultdict(list)
        for strategy in strategies:
            if tenant := tenant_map.get(strategy["source_tenant_id"]):
                collaboration_tenant_map[strategy["target_tenant_id"]].append(tenant)

        return {"collaboration_tenant_map": collaboration_tenant_map}

    def get_queryset(self):
        slz = TenantListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 不启用的租户，是不允许登录的
        queryset = Tenant.objects.filter(status=TenantStatus.ENABLED)

        # 根据指定的租户 ID(s) 查询
        if tenant_ids := data["tenant_ids"]:
            queryset = queryset.filter(id__in=tenant_ids)
        else:
            # 无指定需查询的租户，则只查询可见的租户
            queryset = queryset.filter(visible=True)

        return queryset


class IdpListApi(LoginApiAccessControlMixin, generics.ListAPIView):
    pagination_class = None
    serializer_class = IdpListOutputSLZ

    def get_serializer_context(self) -> Dict[str, Any]:
        return {"data_source_type_map": {ds["id"]: ds["type"] for ds in DataSource.objects.values("id", "type")}}

    def get_queryset(self):
        tenant_id = self.kwargs["tenant_id"]
        idp_owner_tenant_id = self.kwargs["idp_owner_tenant_id"]

        # 检查是否存在协同关系
        if (
            tenant_id != idp_owner_tenant_id
            and not CollaborationStrategy.objects.filter(
                source_status=CollaborationStrategyStatus.ENABLED,
                target_status=CollaborationStrategyStatus.ENABLED,
                source_tenant_id=idp_owner_tenant_id,
                target_tenant_id=tenant_id,
            ).exists()
        ):
            return Idp.objects.none()

        queryset = Idp.objects.filter(owner_tenant_id=idp_owner_tenant_id, status=IdpStatus.ENABLED)
        # 协同情况，只有实名用户对应的认证源可以登录
        if tenant_id != idp_owner_tenant_id:
            ds = DataSource.objects.filter(owner_tenant_id=idp_owner_tenant_id, type=DataSourceTypeEnum.REAL).first()
            if ds is None:
                return Idp.objects.none()

            queryset = queryset.filter(data_source_id=ds.id)

        return queryset


class IdpRetrieveApi(LoginApiAccessControlMixin, generics.RetrieveAPIView):
    serializer_class = IdpRetrieveOutputSLZ
    queryset = Idp.objects.all()
    lookup_field = "id"


class TenantUserMatchApi(LoginApiAccessControlMixin, generics.CreateAPIView):
    """通过IDP的用户信息匹配到蓝鲸用户"""

    def post(self, request, *args, **kwargs):
        slz = TenantUserMatchInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 登录的租户
        tenant_id = kwargs["tenant_id"]
        tenant = Tenant.objects.filter(id=tenant_id, status=TenantStatus.ENABLED).first()
        if not tenant:
            raise error_codes.OBJECT_NOT_FOUND.f(_("租户 {} 不存在").format(tenant_id))

        # 认证源
        idp_id = kwargs["idp_id"]
        if not Idp.objects.filter(id=idp_id).exists():
            raise error_codes.OBJECT_NOT_FOUND.f(_("认证源 {} 不存在").format(idp_id))

        # FIXME: 查询是绑定匹配还是直接匹配，
        #  一般社会化登录都得通过绑定匹配方式，比如QQ，用户得先绑定后才能使用QQ登录
        #  直接匹配，一般是企业身份登录方式，
        #  比如企业内部SAML2.0登录，认证后获取到的用户字段，能直接与数据源里的用户数据字段匹配
        data_source_user_ids = AuthenticationMatcher(idp_id).match(data["idp_users"])

        # 查询租户用户
        tenant_users = TenantUser.objects.filter(
            tenant_id=tenant_id, data_source_user_id__in=list(data_source_user_ids)
        ).select_related("data_source_user")

        return Response(TenantUserMatchOutputSLZ(instance=tenant_users, many=True).data)


class TenantUserRetrieveApi(LoginApiAccessControlMixin, generics.RetrieveAPIView):
    serializer_class = TenantUserRetrieveOutputSLZ
    queryset = TenantUser.objects.all()
    lookup_field = "id"

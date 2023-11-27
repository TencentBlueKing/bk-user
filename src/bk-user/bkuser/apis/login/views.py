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
from typing import Any, Dict

from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.response import Response

from bkuser.apps.data_source.models import LocalDataSourceIdentityInfo
from bkuser.apps.idp.constants import IdpStatus
from bkuser.apps.idp.models import Idp
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.biz.idp import AuthenticationMatcher
from bkuser.common.error_codes import error_codes

from .mixins import LoginApiAccessControlMixin
from .serializers import (
    GlobalInfoRetrieveOutputSLZ,
    IdpListOutputSLZ,
    IdpRetrieveOutputSLZ,
    LocalUserCredentialAuthenticateInputSLZ,
    LocalUserCredentialAuthenticateOutputSLZ,
    TenantListInputSLZ,
    TenantListOutputSLZ,
    TenantRetrieveOutputSLZ,
    TenantUserMatchInputSLZ,
    TenantUserMatchOutputSLZ,
    TenantUserRetrieveOutputSLZ,
)


class LocalUserCredentialAuthenticateApi(LoginApiAccessControlMixin, generics.CreateAPIView):
    """本地数据源用户的凭据认证"""

    def post(self, request, *args, **kwargs):
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


class GlobalInfoRetrieveApi(LoginApiAccessControlMixin, generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        # 查询租户启用的认证源
        enabled_idp_map = defaultdict(list)
        for idp in Idp.objects.filter(status=IdpStatus.ENABLED).values("owner_tenant_id", "id", "plugin_id"):
            enabled_idp_map[idp["owner_tenant_id"]].append({"id": idp["id"], "plugin_id": idp["plugin_id"]})

        # 启用认证源的租户数量
        enabled_auth_tenant_number = len(enabled_idp_map)

        # 唯一启用认证的租户信息
        only_enabled_auth_tenant: Dict[str, Any] | None = None
        if enabled_auth_tenant_number == 1:
            owner_tenant_id, enabled_idps = next(iter(enabled_idp_map.items()))
            tenant = Tenant.objects.get(id=owner_tenant_id)
            only_enabled_auth_tenant = {
                "id": tenant.id,
                "name": tenant.name,
                "logo": tenant.logo,
                "enabled_idps": enabled_idps,
            }

        return Response(
            GlobalInfoRetrieveOutputSLZ(
                instance={
                    # FIXME (nan): 待实现全局配置管理功能后调整
                    "tenant_visible": False,
                    "enabled_auth_tenant_number": enabled_auth_tenant_number,
                    "only_enabled_auth_tenant": only_enabled_auth_tenant,
                }
            ).data
        )


class TenantListApi(LoginApiAccessControlMixin, generics.ListAPIView):
    pagination_class = None
    serializer_class = TenantListOutputSLZ

    def get_queryset(self):
        slz = TenantListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = Tenant.objects.all()
        if data["tenant_ids"]:
            queryset = queryset.filter(id__in=data["tenant_ids"])

        return queryset


class TenantRetrieveApi(LoginApiAccessControlMixin, generics.RetrieveAPIView):
    serializer_class = TenantRetrieveOutputSLZ
    queryset = Tenant.objects.all()
    lookup_field = "id"


class IdpListApi(LoginApiAccessControlMixin, generics.ListAPIView):
    pagination_class = None
    serializer_class = IdpListOutputSLZ

    def get_queryset(self):
        return Idp.objects.filter(owner_tenant_id=self.kwargs["tenant_id"]).select_related("plugin")


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
        tenant = Tenant.objects.filter(id=tenant_id).first()
        if not tenant:
            raise error_codes.OBJECT_NOT_FOUND.f(_("租户 {} 不存在").format(tenant_id))

        # 认证源
        idp_id = kwargs["idp_id"]
        if not Idp.objects.filter(owner_tenant_id=tenant_id, id=idp_id).exists():
            raise error_codes.OBJECT_NOT_FOUND.f(_("认证源 {} 不存在").format(idp_id))

        # FIXME: 查询是绑定匹配还是直接匹配，
        #  一般社会化登录都得通过绑定匹配方式，比如QQ，用户得先绑定后才能使用QQ登录
        #  直接匹配，一般是企业身份登录方式，
        #  比如企业内部SAML2.0登录，认证后获取到的用户字段，能直接与数据源里的用户数据字段匹配
        data_source_user_ids = AuthenticationMatcher(tenant_id, idp_id).match(data["idp_users"])

        # 查询租户用户
        tenant_users = TenantUser.objects.filter(
            tenant_id=tenant_id, data_source_user_id__in=list(data_source_user_ids)
        ).select_related("data_source_user")

        return Response(TenantUserMatchOutputSLZ(instance=tenant_users, many=True).data)


class TenantUserRetrieveApi(LoginApiAccessControlMixin, generics.RetrieveAPIView):
    serializer_class = TenantUserRetrieveOutputSLZ
    queryset = TenantUser.objects.all()
    lookup_field = "id"

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
import operator
from functools import reduce

from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.response import Response

from bkuser.apps.data_source.models import DataSourceUser, LocalDataSourceIdentityInfo
from bkuser.apps.idp.data_models import DataSourceMatchRuleList, convert_match_rules_to_queryset_filter
from bkuser.apps.idp.models import Idp
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.common.error_codes import error_codes

from .mixins import LoginApiAccessControlMixin
from .serializers import (
    GlobalSettingRetrieveOutputSLZ,
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


class GlobalSettingRetrieveApi(LoginApiAccessControlMixin, generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        # TODO: 待实现全局配置管理功能后调整
        return Response(GlobalSettingRetrieveOutputSLZ(instance={"tenant_visible": False}).data)


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


class IdpListApi(generics.ListAPIView, LoginApiAccessControlMixin):
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
        idp = Idp.objects.filter(owner_tenant_id=tenant_id, id=idp_id).first()
        if not idp:
            raise error_codes.OBJECT_NOT_FOUND.f(_("认证源 {} 不存在").format(idp_id))

        # FIXME: 查询是绑定匹配还是直接匹配，
        #  一般社会化登录都得通过绑定匹配方式，比如QQ，用户得先绑定后才能使用QQ登录
        #  直接匹配，一般是企业身份登录方式，
        #  比如企业内部SAML2.0登录，认证后获取到的用户字段，能直接与数据源里的用户数据字段匹配
        # 认证源与数据源的匹配规则
        data_source_match_rules = DataSourceMatchRuleList.validate_python(idp.data_source_match_rules)
        # 将规则转换为Django Queryset 过滤条件, 不同用户之间过滤逻辑是OR
        conditions = [
            condition
            for userinfo in data["idp_users"]
            if (condition := convert_match_rules_to_queryset_filter(data_source_match_rules, userinfo))
        ]

        # 查询数据源用户
        data_source_user_ids = (
            DataSourceUser.objects.filter(reduce(operator.or_, conditions)).values_list("id", flat=True)
            if conditions
            else []
        )

        # 查询租户用户
        tenant_users = TenantUser.objects.filter(
            tenant_id=tenant_id, data_source_user_id__in=list(data_source_user_ids)
        ).select_related("data_source_user")

        return Response(TenantUserMatchOutputSLZ(instance=tenant_users, many=True).data)


class TenantUserRetrieveApi(LoginApiAccessControlMixin, generics.RetrieveAPIView):
    serializer_class = TenantUserRetrieveOutputSLZ
    queryset = TenantUser.objects.all()
    lookup_field = "id"

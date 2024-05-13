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
import re
from typing import Any, Dict, List

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DATA_SOURCE_USERNAME_REGEX
from bkuser.apps.idp.constants import IdpStatus
from bkuser.apps.idp.models import Idp
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.serializers import StringArrayField


class LocalUserCredentialAuthenticateInputSLZ(serializers.Serializer):
    data_source_ids = serializers.ListField(help_text="指定查询的数据源ID列表", child=serializers.IntegerField())
    username = serializers.CharField(help_text="用户名")
    password = serializers.CharField(help_text="密码")

    def validate_username(self, value: str) -> str:
        # Q: 为什么不使用 biz.validators.py 封装的 validate_data_source_user_username
        # A: 这里是登录验证用户名密码，虽然用户名规则不符合，
        #    但由于安全原因(避免攻击者知道规则)，只能告知用户名或密码错误
        if not re.fullmatch(DATA_SOURCE_USERNAME_REGEX, value):
            raise ValidationError(_("用户名或密码错误"))

        return value


class LocalUserCredentialAuthenticateOutputSLZ(serializers.Serializer):
    data_source_id = serializers.IntegerField(help_text="数据源ID")
    id = serializers.IntegerField(help_text="用户 ID", source="user_id")
    username = serializers.CharField(help_text="用户名")


class TenantListInputSLZ(serializers.Serializer):
    tenant_ids = StringArrayField(help_text="指定查询的租户, 多个使用英文逗号分隔", required=False, default="")


class CollaborationTenantSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名称")


class TenantListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.CharField(help_text="租户 Logo")
    collaboration_tenants = serializers.SerializerMethodField(help_text="协同租户列表")

    class Meta:
        ref_name = "login.TenantListOutputSLZ"

    def get_collaboration_tenants(self, obj: Tenant) -> List[Dict[str, Any]]:
        collaboration_tenants = self.context["collaboration_tenant_map"].get(obj.id) or []
        return CollaborationTenantSLZ(collaboration_tenants, many=True).data


class EnabledIdpOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源 ID")
    plugin_id = serializers.CharField(help_text="认证源插件 ID")


class OnlyEnabledAuthTenantOutputSLZ(TenantListOutputSLZ):
    enabled_idps = serializers.ListField(child=EnabledIdpOutputSLZ(help_text="认证源插件"))


class GlobalInfoRetrieveOutputSLZ(serializers.Serializer):
    tenant_visible = serializers.BooleanField(help_text="租户可见性")
    enabled_auth_tenant_number = serializers.IntegerField(help_text="启用用户认证的租户数量")
    only_enabled_auth_tenant = OnlyEnabledAuthTenantOutputSLZ(
        help_text="唯一启动用户认证的租户数量，当 enabled_auth_tenant_number 不是一个时，该值为空",
        allow_null=True,
    )


class IdpListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源 ID")
    name = serializers.CharField(help_text="认证源名称")
    plugin_id = serializers.CharField(help_text="认证源 ID", source="plugin.id")
    data_source_type = serializers.SerializerMethodField(help_text="数据源类型")

    class Meta:
        ref_name = "login.IdpListOutputSLZ"

    def get_data_source_type(self, obj: Idp) -> str:
        return self.context["data_source_type_map"].get(obj.data_source_id, "")


class IdpPluginOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源插件 ID")
    name = serializers.CharField(help_text="认证源插件名称")

    class Meta:
        ref_name = "login.IdpPluginOutputSLZ"


class IdpRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源 ID")
    name = serializers.CharField(help_text="认证源名称")
    status = serializers.ChoiceField(help_text="状态", choices=IdpStatus.get_choices())
    owner_tenant_id = serializers.CharField(help_text="归属的租户 ID")
    plugin = IdpPluginOutputSLZ(help_text="认证源插件")
    plugin_config = serializers.SerializerMethodField(help_text="认证源插件配置")

    class Meta:
        ref_name = "login.IdpRetrieveOutputSLZ"

    def get_plugin_config(self, obj: Idp) -> Dict[str, Any]:
        return obj.get_plugin_cfg().model_dump()


class TenantUserMatchInputSLZ(serializers.Serializer):
    idp_users = serializers.ListField(
        help_text="认证源获取到的用户，支持多个",
        child=serializers.JSONField(help_text="用户信息"),
        min_length=1,
    )


class TenantUserMatchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.ReadOnlyField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.ReadOnlyField(help_text="用户姓名", source="data_source_user.full_name")


class TenantUserRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.ReadOnlyField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.ReadOnlyField(help_text="用户姓名", source="data_source_user.full_name")
    display_name = serializers.SerializerMethodField(help_text="用户姓名")
    language = serializers.CharField(help_text="语言")
    time_zone = serializers.CharField(help_text="时区")

    tenant_id = serializers.CharField(help_text="用户所在租户 ID")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)

    class Meta:
        ref_name = "login.TenantUserRetrieveOutputSLZ"

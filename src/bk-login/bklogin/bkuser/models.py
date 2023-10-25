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
from django.db import models

from bklogin.common.models import AuditedModel, TimestampedModel

from .constants import DataSourceStatus, IdpStatus


class Tenant(TimestampedModel):
    id = models.CharField("租户唯一标识", primary_key=True, max_length=128)
    name = models.CharField("租户名称", max_length=128, unique=True)
    logo = models.TextField("Logo", null=True, blank=True, default="")
    is_default = models.BooleanField("是否默认租户", default=False)

    class Meta:
        db_table = "tenant_tenant"
        ordering = ["created_at"]


class DataSourcePlugin(models.Model):
    """
    数据源插件
    DB初始化内置插件：local/mad/ldap
    """

    id = models.CharField("数据源插件唯一标识", primary_key=True, max_length=128)
    name = models.CharField("数据源插件名称", max_length=128, unique=True)
    description = models.TextField("描述", default="", blank=True)
    logo = models.TextField("Logo", null=True, blank=True, default="")

    class Meta:
        db_table = "data_source_datasourceplugin"


class DataSource(AuditedModel):
    name = models.CharField("数据源名称", max_length=128, unique=True)
    owner_tenant_id = models.CharField("归属租户", max_length=64, db_index=True)
    status = models.CharField(
        "数据源状态",
        max_length=32,
        choices=DataSourceStatus.get_choices(),
        default=DataSourceStatus.ENABLED,
    )
    # Note: 数据源插件被删除的前提是，插件没有被任何数据源使用
    plugin = models.ForeignKey(DataSourcePlugin, on_delete=models.PROTECT)
    plugin_config = models.JSONField("插件配置", default=dict)
    # 同步任务启用/禁用配置、周期配置等
    sync_config = models.JSONField("同步任务配置", default=dict)
    # 字段映射，外部数据源提供商，用户数据字段映射到租户用户数据字段
    field_mapping = models.JSONField("用户字段映射", default=list)

    class Meta:
        db_table = "data_source_datasource"
        ordering = ["id"]


class DataSourceUser(TimestampedModel):
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT, db_constraint=False)
    code = models.CharField("用户标识", max_length=128)

    # ----------------------- 内置字段相关 -----------------------
    username = models.CharField("用户名", max_length=128)
    full_name = models.CharField("姓名", max_length=128)
    email = models.EmailField("邮箱", null=True, blank=True, default="")
    phone = models.CharField("手机号", null=True, blank=True, default="", max_length=32)
    phone_country_code = models.CharField("手机国际区号", max_length=16, null=True, blank=True)
    logo = models.TextField("Logo", max_length=256, null=True, blank=True, default="")

    # ----------------------- 其他 -----------------------
    extras = models.JSONField("自定义字段", default=dict)

    # ----------------------- 状态相关 -----------------------
    # TODO: (1) 用户管理里涉及的功能状态 （2）企业本身的员工状态

    class Meta:
        db_table = "data_source_datasourceuser"
        ordering = ["id"]


class IdpPlugin(models.Model):
    """认证源插件"""

    id = models.CharField("认证源插件唯一标识", primary_key=True, max_length=128)
    name = models.CharField("认证源插件名称", max_length=128, unique=True)
    description = models.TextField("描述", default="", blank=True)
    logo = models.TextField("Logo", null=True, blank=True, default="")

    class Meta:
        db_table = "idp_idpplugin"


class Idp(AuditedModel):
    """认证源"""

    # 登录回调场景下，该 ID 是 URL Path 的一部分
    id = models.CharField("认证源标识", primary_key=True, max_length=128)
    name = models.CharField("认证源名称", max_length=128)
    owner_tenant_id = models.CharField("归属租户", max_length=64, db_index=True)
    status = models.CharField("认证源状态", max_length=32, choices=IdpStatus.get_choices(), default=IdpStatus.ENABLED)
    # Note: 认证源插件被删除的前提是，插件没有被任何认证源使用
    plugin = models.ForeignKey(IdpPlugin, on_delete=models.PROTECT)
    plugin_config = models.JSONField("插件配置", default=dict)
    # 认证源与数据源的匹配规则
    data_source_match_rules = models.JSONField("匹配规则", default=list)
    # 允许关联社会化认证源的租户组织架构范围
    allow_bind_scopes = models.JSONField("允许范围", default=list)

    class Meta:
        db_table = "idp_idp"
        ordering = ["created_at"]


class TenantUser(TimestampedModel):
    """
    租户用户即蓝鲸用户
    """

    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, db_constraint=False)
    data_source_user = models.ForeignKey(DataSourceUser, on_delete=models.DO_NOTHING, db_constraint=False)

    # 冗余字段
    data_source = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING, db_constraint=False)

    # Note: 值：对于新用户则为uuid，对于迁移则兼容旧版本 username@domain或username
    # 兼容旧版本：对外 id/username/bk_username 这3个字段，值是一样的
    id = models.CharField("蓝鲸用户对外唯一标识", primary_key=True, max_length=128)

    # 蓝鲸特有
    language = models.CharField("语言", default="zh-cn", max_length=32)
    time_zone = models.CharField("时区", default="Asia/Shanghai", max_length=32)

    # wx_userid/wx_openid 兼容旧版本迁移
    wx_userid = models.CharField("微信ID", null=True, blank=True, default="", max_length=64)
    wx_openid = models.CharField("微信公众号OpenID", null=True, blank=True, default="", max_length=64)

    # 账号有效期相关
    account_expired_at = models.DateTimeField("账号过期时间", null=True, blank=True)

    # 手机&邮箱相关：手机号&邮箱都可以继承数据源或自定义
    is_inherited_phone = models.BooleanField("是否继承数据源手机号", default=True)
    custom_phone = models.CharField("自定义手机号", max_length=32, null=True, blank=True, default="")
    custom_phone_country_code = models.CharField("自定义手机号的国际区号", max_length=16, null=True, blank=True)
    is_inherited_email = models.BooleanField("是否继承数据源邮箱", default=True)
    custom_email = models.EmailField("自定义邮箱", null=True, blank=True, default="")

    class Meta:
        db_table = "tenant_tenantuser"

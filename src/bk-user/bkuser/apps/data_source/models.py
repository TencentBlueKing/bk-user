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

from blue_krill.models.fields import EncryptField
from django.conf import settings
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from bkuser.apps.data_source.constants import DataSourceStatus
from bkuser.common.models import AuditedModel, TimestampedModel
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.utils.uuid import generate_uuid


class DataSourcePlugin(models.Model):
    """
    数据源插件
    DB初始化内置插件：local/mad/ldap
    """

    id = models.CharField("数据源插件唯一标识", primary_key=True, max_length=128)
    name = models.CharField("数据源插件名称", max_length=128, unique=True)
    description = models.TextField("描述", default="", blank=True)
    logo = models.TextField("Logo", null=True, blank=True, default="")


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
        ordering = ["id"]

    @property
    def is_local(self) -> bool:
        """检查类型是否为本地数据源"""
        return self.plugin.id == DataSourcePluginEnum.LOCAL


class DataSourceUser(TimestampedModel):
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT, db_constraint=False)
    code = models.CharField("用户标识", max_length=128, default=generate_uuid)

    # ----------------------- 内置字段相关 -----------------------
    username = models.CharField("用户名", max_length=128)
    full_name = models.CharField("姓名", max_length=128)
    email = models.EmailField("邮箱", null=True, blank=True, default="")
    phone = models.CharField("手机号", null=True, blank=True, default="", max_length=32)
    phone_country_code = models.CharField(
        "手机国际区号", max_length=16, null=True, blank=True, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )
    logo = models.TextField("Logo", max_length=256, null=True, blank=True, default="")

    # ----------------------- 其他 -----------------------
    extras = models.JSONField("自定义字段", default=dict)

    # ----------------------- 状态相关 -----------------------
    # TODO: (1) 用户管理里涉及的功能状态 （2）企业本身的员工状态

    class Meta:
        ordering = ["id"]
        unique_together = [
            ("code", "data_source"),
            ("username", "data_source"),
        ]


class LocalDataSourceIdentityInfo(TimestampedModel):
    """
    本地数据源特有，认证相关信息
    """

    user = models.OneToOneField(DataSourceUser, on_delete=models.CASCADE)
    # FIXME (su) 使用加盐的方式来存储密码
    password = EncryptField(verbose_name="用户密码", null=True, blank=True, default="", max_length=255)
    password_updated_at = models.DateTimeField("密码最后更新时间", null=True, blank=True)
    password_expired_at = models.DateTimeField("密码过期时间", null=True, blank=True)

    # data_source / username 为冗余字段，便于认证时快速匹配
    data_source = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING, db_constraint=False)
    username = models.CharField("用户名", max_length=128)

    class Meta:
        unique_together = [
            ("username", "data_source"),
        ]


class DataSourceDepartment(TimestampedModel):
    """
    数据源部门
    """

    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT, db_constraint=False)

    code = models.CharField("部门标识", max_length=128, default=generate_uuid)
    name = models.CharField("部门名称", max_length=255)
    # 额外信息
    extras = models.JSONField("自定义字段", default=dict)

    class Meta:
        ordering = ["id"]
        unique_together = [("code", "data_source")]


class DataSourceDepartmentRelation(MPTTModel, TimestampedModel):
    """
    数据源部门关系
    """

    department = models.OneToOneField(
        DataSourceDepartment, on_delete=models.DO_NOTHING, db_constraint=False, primary_key=True
    )
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    # 冗余字段
    data_source = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING, db_constraint=False)

    class Meta:
        index_together = [
            ("tree_id", "lft", "rght"),
            ("parent_id", "tree_id", "lft"),
        ]


class DataSourceDepartmentUserRelation(TimestampedModel):
    """
    数据源部门 - 用户关联表
    """

    department = models.ForeignKey(DataSourceDepartment, on_delete=models.DO_NOTHING, db_constraint=False)
    user = models.ForeignKey(DataSourceUser, on_delete=models.DO_NOTHING, db_constraint=False)

    class Meta:
        ordering = ["id"]
        unique_together = [
            ("user", "department"),
        ]


class DataSourceUserLeaderRelation(TimestampedModel):
    """
    数据源用户 - Leader 关联表
    """

    user = models.ForeignKey(DataSourceUser, on_delete=models.DO_NOTHING, db_constraint=False)
    leader = models.ForeignKey(DataSourceUser, related_name="leader", on_delete=models.DO_NOTHING, db_constraint=False)

    class Meta:
        ordering = ["id"]
        unique_together = [
            ("user", "leader"),
        ]


class DepartmentRelationMPTTTree(models.Model):
    """部门关系树记录表，用于自增 tree_id 的分配"""

    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT, db_constraint=False)

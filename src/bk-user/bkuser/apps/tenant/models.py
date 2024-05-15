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
from typing import Tuple

from django.conf import settings
from django.db import models
from django.db.models import Q, QuerySet

from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourceUser
from bkuser.apps.tenant.constants import (
    TIME_ZONE_CHOICES,
    CollaborationStrategyStatus,
    TenantStatus,
    TenantUserStatus,
    UserFieldDataType,
)
from bkuser.common.constants import PERMANENT_TIME, BkLanguageEnum
from bkuser.common.models import AuditedModel, TimestampedModel
from bkuser.common.time import datetime_to_display


class Tenant(AuditedModel):
    id = models.CharField("租户唯一标识", primary_key=True, max_length=128)
    name = models.CharField("租户名称", max_length=128, unique=True)
    logo = models.TextField("Logo", null=True, blank=True, default="")
    is_default = models.BooleanField("是否默认租户", default=False)
    status = models.CharField("状态", max_length=32, choices=TenantStatus.get_choices(), default=TenantStatus.ENABLED)
    # 特性
    visible = models.BooleanField("租户可见性", default=True)
    user_number_visible = models.BooleanField("人员数量是否可见", default=True)

    class Meta:
        ordering = ["created_at"]


class TenantUserManager(models.Manager):
    """TenantUser DB 模型管理器"""

    def filter_by_email(self, tenant_id: str, email: str) -> QuerySet["TenantUser"]:
        return self.filter(tenant_id=tenant_id).filter(
            Q(is_inherited_email=False, custom_email=email) | Q(is_inherited_email=True, data_source_user__email=email)
        )

    def filter_by_phone(self, tenant_id: str, phone: str, phone_country_code: str) -> QuerySet["TenantUser"]:
        return self.filter(tenant_id=tenant_id).filter(
            Q(
                is_inherited_email=False,
                custom_phone=phone,
                custom_phone_country_code=phone_country_code,
            )
            | Q(
                is_inherited_email=True,
                data_source_user__phone=phone,
                data_source_user__phone_country_code=phone_country_code,
            )
        )


class TenantUser(AuditedModel):
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
    status = models.CharField(
        "状态", max_length=32, choices=TenantUserStatus.get_choices(), default=TenantUserStatus.ENABLED
    )

    # 蓝鲸特有
    language = models.CharField(
        "语言", choices=BkLanguageEnum.get_choices(), default=BkLanguageEnum.ZH_CN, max_length=32
    )
    time_zone = models.CharField("时区", choices=TIME_ZONE_CHOICES, default="Asia/Shanghai", max_length=32)

    # wx_userid/wx_openid 兼容旧版本迁移
    wx_userid = models.CharField("微信ID", null=True, blank=True, default="", max_length=64)
    wx_openid = models.CharField("微信公众号 用户OpenID", null=True, blank=True, default="", max_length=64)

    # 账号有效期相关
    account_expired_at = models.DateTimeField("账号过期时间", null=True, blank=True, default=PERMANENT_TIME)

    # 手机&邮箱相关：手机号&邮箱都可以继承数据源或自定义
    is_inherited_phone = models.BooleanField("是否继承数据源手机号", default=True)
    custom_phone = models.CharField("自定义手机号", max_length=32, null=True, blank=True, default="")
    custom_phone_country_code = models.CharField(
        "自定义手机号的国际区号",
        max_length=16,
        null=True,
        blank=True,
        default=settings.DEFAULT_PHONE_COUNTRY_CODE,
    )
    is_inherited_email = models.BooleanField("是否继承数据源邮箱", default=True)
    custom_email = models.EmailField("自定义邮箱", null=True, blank=True, default="")

    objects = TenantUserManager()

    class Meta:
        unique_together = [
            ("data_source_user", "tenant"),
        ]

    @property
    def account_expired_at_display(self) -> str:
        return datetime_to_display(self.account_expired_at)

    @property
    def email(self) -> str:
        return self.data_source_user.email if self.is_inherited_email else self.custom_email

    @property
    def phone_info(self) -> Tuple[str, str]:
        return (
            (self.data_source_user.phone, self.data_source_user.phone_country_code)
            if self.is_inherited_phone
            else (self.custom_phone, self.custom_phone_country_code)
        )


class TenantDepartment(TimestampedModel):
    """
    租户部门即蓝鲸部门
    """

    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, db_constraint=False)
    data_source_department = models.ForeignKey(DataSourceDepartment, on_delete=models.DO_NOTHING, db_constraint=False)

    # 冗余字段
    data_source = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING, db_constraint=False)

    # 目前租户部门暂无其他特别属性，后续可以加入一些统计相关字段(比如，递归人数、当前层级人数等)

    class Meta:
        unique_together = [
            ("data_source_department", "tenant"),
        ]


class TenantManager(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_index=True)
    tenant_user = models.ForeignKey(TenantUser, on_delete=models.CASCADE, db_constraint=False)

    class Meta:
        unique_together = [
            ("tenant_user", "tenant"),
        ]


class UserBuiltinField(TimestampedModel):
    """用户内置字段"""

    name = models.CharField("字段名称", unique=True, max_length=128)
    display_name = models.CharField("展示用名称", unique=True, max_length=128)
    data_type = models.CharField("数据类型", choices=UserFieldDataType.get_choices(), max_length=32)
    required = models.BooleanField("是否必填")
    unique = models.BooleanField("是否唯一")
    default = models.JSONField("默认值", default="")
    options = models.JSONField("配置项", default=list)


class TenantUserCustomField(TimestampedModel):
    """租户用户自定义字段"""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_constraint=False)
    name = models.CharField("英文标识", max_length=128)
    display_name = models.CharField("字段名称", max_length=128)
    data_type = models.CharField("数据类型", choices=UserFieldDataType.get_choices(), max_length=32)
    required = models.BooleanField("是否必填", default=False)
    unique = models.BooleanField("是否唯一", default=False)
    personal_center_visible = models.BooleanField("是否在个人中心可见", default=False)
    personal_center_editable = models.BooleanField("是否在个人中心可编辑", default=False)
    manager_editable = models.BooleanField("租户管理员是否可重复编辑", default=True)
    default = models.JSONField("默认值", default="")
    options = models.JSONField("配置项", default=list)
    # 兼容逻辑，只有老版本迁移过来的枚举类型自定义字段会需要
    use_digit_option_id = models.BooleanField("是否使用数字作为选项ID", default=False)

    class Meta:
        unique_together = [
            ("name", "tenant"),
            ("display_name", "tenant"),
        ]


class TenantUserValidityPeriodConfig(AuditedModel):
    """账号有效期-配置"""

    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, db_index=True, unique=True)

    enabled = models.BooleanField("是否启用账户有效期", default=True)
    validity_period = models.IntegerField("有效期(单位：天)", default=-1)
    remind_before_expire = models.JSONField("临X天过期发送提醒(单位：天)", default=list)
    enabled_notification_methods = models.JSONField("通知方式", default=list)
    notification_templates = models.JSONField("通知模板", default=list)


class CollaborationStrategy(AuditedModel):
    """协同策略"""

    name = models.CharField("策略名称", max_length=128)
    source_tenant = models.ForeignKey(
        Tenant, on_delete=models.DO_NOTHING, db_constraint=False, related_name="source_tenant"
    )
    target_tenant = models.ForeignKey(
        Tenant, on_delete=models.DO_NOTHING, db_constraint=False, related_name="target_tenant"
    )
    source_status = models.CharField(
        "策略状态（分享方）",
        choices=CollaborationStrategyStatus.get_choices(),
        default=CollaborationStrategyStatus.ENABLED,
        max_length=32,
    )
    target_status = models.CharField(
        "策略状态（接受方）",
        choices=CollaborationStrategyStatus.get_choices(),
        default=CollaborationStrategyStatus.UNCONFIRMED,
        max_length=32,
    )
    source_config = models.JSONField("策略配置（分享方）", default=dict)
    target_config = models.JSONField("策略配置（接受方）", default=dict)

    class Meta:
        unique_together = [
            ("name", "source_tenant"),
            ("source_tenant", "target_tenant"),
        ]

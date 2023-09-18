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
from django.conf import settings
from django.db import models

from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourceUser
from bkuser.apps.tenant.constants import TenantFeatureFlag, UserFieldDataType
from bkuser.common.constants import PERMANENT_TIME, BkLanguageEnum
from bkuser.common.models import TimestampedModel

from .constants import TIME_ZONE_CHOICES


class Tenant(TimestampedModel):
    id = models.CharField("租户唯一标识", primary_key=True, max_length=128)
    name = models.CharField("租户名称", max_length=128, unique=True)
    logo = models.TextField("Logo", null=True, blank=True, default="")
    is_default = models.BooleanField("是否默认租户", default=False)
    feature_flags = models.JSONField("租户特性标志集", default=dict)

    class Meta:
        ordering = ["created_at"]

    def has_feature_flag(self, ff: TenantFeatureFlag) -> bool:
        default_flags = TenantFeatureFlag.get_default_flags()
        return self.feature_flags.get(ff, default_flags[ff])


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
    language = models.CharField("语言", choices=BkLanguageEnum.get_choices(), default="zh-cn", max_length=32)
    time_zone = models.CharField("时区", choices=TIME_ZONE_CHOICES, default="Asia/Shanghai", max_length=32)

    # wx_userid/wx_openid 兼容旧版本迁移
    wx_userid = models.CharField("微信ID", null=True, blank=True, default="", max_length=64)
    wx_openid = models.CharField("微信公众号OpenID", null=True, blank=True, default="", max_length=64)

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
    custom_email = models.EmailField("自定义邮箱", max_length=256, null=True, blank=True, default="")

    class Meta:
        unique_together = [
            ("data_source_user", "tenant"),
        ]


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
    options = models.JSONField("配置项", default={})


class TenantUserCustomField(TimestampedModel):
    """租户用户自定义字段"""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_constraint=False)
    name = models.CharField("字段名称", max_length=128)
    display_name = models.CharField("展示用名称", max_length=128)
    data_type = models.CharField("数据类型", choices=UserFieldDataType.get_choices(), max_length=32)
    required = models.BooleanField("是否必填")
    default = models.JSONField("默认值", default="")
    options = models.JSONField("配置项", default={})

    class Meta:
        unique_together = [
            ("name", "tenant"),
            ("display_name", "tenant"),
        ]


# # TODO: 是否直接定义 TenantCommonConfig 表，AccountValidityPeriod是一个JSON字段？
# class AccountValidityPeriodConfig:
#     """账号时效配置"""
#
#     tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_index=True, unique=True)
#
#     enabled = models.BooleanField("是否启用", default=True)
#     # TODO: 定义枚举，设置默认值为永久
#     validity_period_seconds = models.IntegerField("有效期(单位：秒)", default=-1)
#     # TODO: 定义枚举，设置默认值为7天
#     reminder_period_days = models.IntegerField("提醒周期(单位：天)", default=7)
#     # TODO: 定义枚举，同时需要考虑到与企业ESB配置的支持的通知方式有关，是否定义字段？
#     notification_method = models.CharField("通知方式", max_length=32, default="email")
#     # TODO: 需要考虑不同通知方式，可能无法使用相同模板，或者其他设计方式
#     notification_content_template = models.TextField("通知模板", default="")


# class TenantUserSocialAccountRelation(TimestampedModel):
#     """租户用户与社交账号绑定表"""
#
#     tenant_user = models.ForeignKey(TenantUser, on_delete=models.CASCADE, db_constraint=False)
#     idp = models.ForeignKey(Idp, on_delete=models.DO_NOTHING, db_constraint=False)
#     social_client_id = models.CharField("社交认证源对应的ClientID", max_length=128)
#     social_account_id = models.CharField("绑定的社交账号ID", max_length=128)
#
#     class Meta:
#         unique_together = [
#             ("social_account_id", "tenant_user", "idp", "social_client_id"),
#         ]
#         index_together = [
#             ("social_account_id", "idp", "social_client_id"),
#         ]

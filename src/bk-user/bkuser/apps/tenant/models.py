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

from bkuser.common.models import TimestampedModel


class Tenant(TimestampedModel):
    id = models.CharField("租户唯一标识", primary_key=True, max_length=128)
    name = models.CharField("租户名称", max_length=128, unique=True)
    logo = models.TextField("Logo", null=True, blank=True, default="")
    is_default = models.BooleanField("是否默认租户", default=False)
    is_user_number_visible = models.BooleanField("人员数量是否可见", default=True)

    class Meta:
        ordering = ["created_time"]


class TenantManager(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_index=True)
    tenant_user_id = models.CharField("租户用户ID", max_length=128, db_index=True)

    class Meta:
        unique_together = [
            ("tenant", "tenant_user_id"),
        ]


# TODO: 是否直接定义 TenantCommonConfig 表，DynamicFieldInfo是一个JSON字段
# class DynamicFieldInfo(TimestampedModel):
#     """动态的用户字段元信息"""
#
#     tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_index=True)
#
#     id = models.CharField("字段唯一标识", max_length=64)
#     name = models.CharField("字段名称", max_length=64)
#     # TODO: 需要枚举支持的数据类型
#     data_type = models.CharField("数据类型", max_length=32)
#     require = models.BooleanField("是否必填", default=False)
#     unique = models.BooleanField("是否唯一", default=False)
#     editable = models.BooleanField("是否可b", default=False)
#     # TODO：不同类型，可能有额外配置，比如枚举有key和value选项，是否配置为json_schema格式，便于校验呢？？？
#
#     class Meta:
#         unique_together = [
#             ("tenant", "id"),
#             ("tenant", "name"),
#         ]


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

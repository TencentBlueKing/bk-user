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

from bkuser.apps.data_source_organization.models import DataSourceUser
from bkuser.common.constants import PERMANENT_TIME, BkLanguageEnum
from bkuser.common.models import TimestampedModel

from .constants import TIME_ZONE_CHOICES


class TenantUser(TimestampedModel):
    """
    租户用户即蓝鲸用户
    """

    # 对应的数据源用户，这里ForeignKey只是为了使用联表查询方便，db_constraint=False表示不设置DB外键约束
    # 等价于 data_source_user_id = models.IntegerField("外键关联的数据源用户ID")
    data_source_user = models.ForeignKey(DataSourceUser, on_delete=models.DO_NOTHING, db_constraint=False)
    # 冗余字段
    tenant_id = models.CharField("外键关联的租户ID", max_length=128)

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
    custom_phone = models.CharField("自定义手机号", max_length=32)
    custom_phone_country_code = models.CharField(
        "自定义手机号的国际区号",
        max_length=16,
        null=True,
        blank=True,
        default=settings.DEFAULT_PHONE_COUNTRY_CODE,
    )
    is_inherited_email = models.BooleanField("是否继承数据源邮箱", default=True)
    custom_email = models.EmailField("自定义邮箱", null=True, blank=True, default="")


class TenantDepartment(TimestampedModel):
    """
    租户部门即蓝鲸部门
    """

    # 冗余字段
    tenant_id = models.CharField("外键关联的租户ID", max_length=128)

    data_source_department_id = models.IntegerField("外键关联的数据源部门ID")

    # 目前租户部门暂无其他特别属性，后续可以加入一些统计相关字段(比如，递归人数、当前层级人数等)

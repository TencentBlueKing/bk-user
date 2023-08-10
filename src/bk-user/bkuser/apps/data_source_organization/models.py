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
from mptt.models import MPTTModel, TreeForeignKey

from bkuser.common.models import TimestampedModel


class DataSourceUser(TimestampedModel):
    data_source_id = models.IntegerField("数据源 ID")

    # ----------------------- 内置字段相关 -----------------------
    username = models.CharField("用户名", max_length=128)
    full_name = models.CharField("姓名", max_length=128)
    email = models.EmailField("邮箱", null=True, blank=True, default="")
    phone = models.CharField("手机号", max_length=32)
    phone_country_code = models.CharField(
        "手机国际区号", max_length=16, null=True, blank=True, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )
    logo = models.TextField("Logo", max_length=256, null=True, blank=True, default="")
    # ----------------------- 内置字段相关 -----------------------

    # ----------------------- 其他 -----------------------
    extras = models.JSONField("自定义字段", default=dict)
    # ----------------------- 其他 -----------------------

    # ----------------------- 状态相关 -----------------------
    # TODO: (1) 用户管理里涉及的功能状态 （2）企业本身的员工状态
    # ----------------------- 状态相关 -----------------------

    class Meta:
        ordering = ["id"]
        unique_together = [
            ("username", "data_source_id"),
        ]


class LocalDataSourceIdentityInfo(TimestampedModel):
    """
    本地数据源特有，认证相关信息
    """

    user = models.OneToOneField(DataSourceUser, on_delete=models.CASCADE)
    password = models.CharField("用户密码", null=True, blank=True, default="", max_length=255)
    password_updated_at = models.DateTimeField("密码最后更新时间", null=True, blank=True)
    password_expired_at = models.DateTimeField("密码过期时间", null=True, blank=True)

    # data_source_id/username为冗余字段，便于认证时快速匹配
    data_source_id = models.IntegerField("数据源 ID")
    username = models.CharField("用户名", max_length=128)

    class Meta:
        unique_together = [
            ("username", "data_source_id"),
        ]


class DataSourceDepartment(TimestampedModel):
    """
    数据源部门
    """

    data_source_id = models.IntegerField("数据源 ID")

    # 部门标识，不同于自增 id，多数情况存储各个公司组织架构系统的id, 非必须
    code = models.CharField("部门标识", null=True, blank=True, max_length=128)
    name = models.CharField("部门名称", max_length=255)
    # 额外信息
    extras = models.JSONField("自定义字段", default=dict)

    class Meta:
        ordering = ["id"]


class DataSourceDepartmentRelation(MPTTModel, TimestampedModel):
    """
    数据源部门关系
    """

    id = models.IntegerField("部门 ID", primary_key=True)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    # 冗余字段
    data_source_id = models.IntegerField("数据源 ID")

    class Meta:
        index_together = [
            ("tree_id", "lft", "rght"),
            ("parent_id", "tree_id", "lft"),
        ]


class DataSourceDepartmentUserRelation(TimestampedModel):
    """
    数据源部门 - 用户关联表
    """

    department_id = models.IntegerField("数据源部门 ID", db_index=True)
    user_id = models.IntegerField("数据源用户 ID", db_index=True)

    class Meta:
        ordering = ["id"]
        unique_together = [
            ("department_id", "user_id"),
        ]


class DataSourceUserLeaderRelation(TimestampedModel):
    """
    数据源用户 - Leader 关联表
    """

    user_id = models.IntegerField("数据源用户 ID", db_index=True)
    leader_id = models.IntegerField("数据源用户 Leader ID", db_index=True)

    class Meta:
        ordering = ["id"]
        unique_together = [
            ("user_id", "leader_id"),
        ]

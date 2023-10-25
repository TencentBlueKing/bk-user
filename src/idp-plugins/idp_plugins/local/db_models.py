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
from django.db import models


class DataSourceUser(models.Model):
    data_source_id = models.BigIntegerField("数据源")
    code = models.CharField("用户标识", max_length=128)

    # ----------------------- 内置字段相关 -----------------------
    username = models.CharField("用户名", max_length=128)
    full_name = models.CharField("姓名", max_length=128)
    email = models.EmailField("邮箱", null=True, blank=True, default="")
    phone = models.CharField("手机号", null=True, blank=True, default="", max_length=32)
    phone_country_code = models.CharField("手机国际区号", max_length=16, null=True, blank=True)

    class Meta:
        # FIXME: 由于idp_plugins模块会被不同项目引入，model为了被Django App 加载，需要添加app_label,
        #  同时由于不同项目自定义app不一样，所以这里临时使用公共的django.contrib.auth
        app_label = "django.contrib.auth"
        managed = False
        db_table = "data_source_datasourceuser"
        ordering = ["id"]


class LocalDataSourceIdentityInfo(models.Model):
    """
    本地数据源特有，认证相关信息
    """

    user = models.OneToOneField(DataSourceUser, on_delete=models.CASCADE)
    password = EncryptField(verbose_name="用户密码", null=True, blank=True, default="", max_length=255)
    password_updated_at = models.DateTimeField("密码最后更新时间", null=True, blank=True)
    password_expired_at = models.DateTimeField("密码过期时间", null=True, blank=True)

    # data_source_id/username为冗余字段，便于认证时快速匹配
    data_source_id = models.BigIntegerField("数据源")
    username = models.CharField("用户名", max_length=128)

    class Meta:
        # FIXME: 由于idp_plugins模块会被不同项目引入，model为了被Django App 加载，需要添加app_label,
        #  同时由于不同项目自定义app不一样，所以这里临时使用公共的django.contrib.auth
        app_label = "django.contrib.auth"
        managed = False
        db_table = "data_source_localdatasourceidentityinfo"

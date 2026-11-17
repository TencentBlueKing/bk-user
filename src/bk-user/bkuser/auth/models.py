# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from typing import List

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=64, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS: List[str] = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        db_table = "auth_user"

    def get_property(self, key):
        try:
            return self.properties.get(key=key).value
        except UserProperty.DoesNotExist:
            return None

    def set_property(self, key, value):
        key_property, _ = self.properties.get_or_create(key=key)
        if key_property.value != value:
            key_property.value = value
            key_property.save()

    @property
    def tenant_id(self) -> str | None:
        """获取当前登录用户所属租户 ID

        用户扩展信息通过 UserProperty 存储和读取，但 bk_notice_sdk 在多租户模式
        下会直接访问 request.user.tenant_id，因此提供此属性以兼容。
        """
        return self.get_property("tenant_id")


class UserProperty(models.Model):
    """
    Add user extra property
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties")
    key = models.CharField(max_length=64)
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name = "user property"
        verbose_name_plural = "user properties"
        db_table = "auth_user_property"
        unique_together = (("user", "key"),)

    def __str__(self):
        return f"{self.key}: {self.value}"


class UserProxy(User):
    class Meta:
        proxy = True

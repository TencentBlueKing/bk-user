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

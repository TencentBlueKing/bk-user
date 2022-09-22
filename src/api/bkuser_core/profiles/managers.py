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
import datetime
import random
import secrets
import string

from django.conf import settings
from django.db import models
from django.utils.timezone import now

from bkuser_core.common.models import AdvancedModelManager


def gen_password(length):
    chars = string.ascii_letters + string.digits
    return "".join([random.choice(chars) for i in range(length)])


class ProfileAllManager(models.Manager):
    def get_queryset(self):
        return super(ProfileAllManager, self).get_queryset()


class ProfileManager(AdvancedModelManager):
    def add_leader(self, profile_id, profile_obj):
        inst = self.get(id=profile_id)
        if inst not in profile_obj.leader.all():
            profile_obj.leader.add(inst)


class DynamicFieldInfoManager(models.Manager):
    def get_all_field_keys(self):
        """获取当前所有动态字段 key 列表"""
        return self.all().values_list("key", flat=True)

    def get_max_order(self):
        """获取所有启用的字段最大排序值"""
        return max(self.filter(enabled=True).values_list("order", flat=True))

    def get_key_name_map(self):
        """获取字段 name:display_name 映射表"""
        all_fields_info = self.all().values("name", "display_name")
        key_name_map = {}
        for fields_info in all_fields_info:
            key_name_map[fields_info["name"]] = fields_info["display_name"]
        return key_name_map

    def update_order(self, instance, new_order):
        """保证整体 order 连续"""
        if instance.order == new_order:
            return

        if instance.order > new_order:
            # 升序
            influenced_items = self.filter(order__lt=instance.order, order__gte=new_order)
            ascending = True
        else:
            # 降序
            influenced_items = self.filter(order__gt=instance.order, order__lte=new_order)
            ascending = False

        for influenced_item in influenced_items:
            influenced_item.order = models.F("order") + 1 if ascending else models.F("order") - 1
            influenced_item.save(update_fields=["order"])

        # save the target
        instance.order = new_order
        instance.save(update_fields=["order"])

        return

    def get_extras_default_values(self) -> dict:
        """获取用户自定义字段的默认值"""
        return {i.name: None if i.default == "" else i.default for i in self.filter(enabled=True, builtin=False)}


class ProfileTokenManager(models.Manager):
    def create(self, profile, token_expire_seconds: int = settings.DEFAULT_TOKEN_EXPIRE_SECONDS):
        token = secrets.token_urlsafe(32)
        # TODO: use another way generate token, - is not safe for swagger sdk, still not know why
        token = token.replace("-", "0")

        expire_time = now() + datetime.timedelta(seconds=token_expire_seconds)
        return super().create(token=token, profile=profile, expire_time=expire_time)

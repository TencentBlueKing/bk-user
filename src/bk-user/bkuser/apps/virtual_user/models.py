# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
from django.db import models

from bkuser.apps.tenant.models import TenantUser
from bkuser.common.models import TimestampedModel
from bkuser.utils.uuid import generate_uuid


class VirtualUser(TimestampedModel):
    id = models.CharField("虚拟用户标识", primary_key=True, max_length=128, default=generate_uuid)
    username = models.CharField("用户名", max_length=128)
    full_name = models.CharField("姓名", max_length=128)
    desc = models.TextField("描述", default="", blank=True)


class App(TimestampedModel):
    id = models.CharField("应用唯一标识", primary_key=True, max_length=128, default=generate_uuid)
    appcode = models.CharField("应用编码", max_length=128)
    name = models.CharField("应用名称", max_length=128)


class VirtualUserOwnerRelation(TimestampedModel):
    owner = models.ForeignKey(TenantUser, on_delete=models.CASCADE, db_constraint=False)
    virtual_user = models.ForeignKey(VirtualUser, on_delete=models.CASCADE, db_constraint=False)

    class Meta:
        ordering = ["id"]
        unique_together = [
            ("owner", "virtual_user"),
        ]


class VirtualUserAppRelation(TimestampedModel):
    app = models.ForeignKey(App, on_delete=models.CASCADE, db_constraint=False)
    virtual_user = models.ForeignKey(VirtualUser, on_delete=models.CASCADE, db_constraint=False)

    class Meta:
        ordering = ["id"]
        unique_together = [
            ("app", "virtual_user"),
        ]

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

from bkuser.apps.data_source.models import DataSourceUser
from bkuser.common.models import TimestampedModel
from bkuser.utils.uuid import generate_uuid


class NaturalUser(TimestampedModel):
    id = models.CharField("自然人标识", primary_key=True, max_length=128, default=generate_uuid)
    full_name = models.CharField("姓名", max_length=128)


class DataSourceUserNaturalUserRelation(TimestampedModel):
    data_source_user = models.ForeignKey(DataSourceUser, on_delete=models.CASCADE, db_constraint=False)
    natural_user = models.ForeignKey(NaturalUser, on_delete=models.DO_NOTHING, db_constraint=False)

    class Meta:
        ordering = ["id"]
        unique_together = [
            ("data_source_user", "natural_user"),
        ]

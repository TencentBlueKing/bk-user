# coding: utf-8
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

from .helper import bulk_update


class BulkUpdateQuerySet(models.QuerySet):
    def bulk_update(
        self,
        objs,
        update_fields=None,
        exclude_fields=None,
        batch_size=None,
        pk_field="pk",
    ):

        self._for_write = True
        using = self.db

        return bulk_update(
            objs,
            update_fields=update_fields,
            exclude_fields=exclude_fields,
            using=using,
            batch_size=batch_size,
            pk_field=pk_field,
        )

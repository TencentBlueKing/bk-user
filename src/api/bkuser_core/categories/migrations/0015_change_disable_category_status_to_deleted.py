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

from __future__ import unicode_literals

from django.db import migrations

from bkuser_core.categories.constants import CategoryStatus
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.recycle_bin.constants import RecycleBinObjectType
from bkuser_core.recycle_bin.models import RecycleBin


def forwards_func(apps, schema_editor):
    """存量已删除目录，增加回收站映射关系"""
    # apps.get_model的形式的delete是硬删除
    del_categories = ProfileCategory.objects.filter(status=CategoryStatus.INACTIVE.value, enabled=False)
    # 适配新的category.delete(), 并添加相应回收站记录
    recycle_bin_relationships: list = []
    for item in del_categories:
        # 原本的delete是将目录状态变为enabled=0，status=inactived
        # 新的delete 目录状态变为enabled=0，status=deleted
        item.delete()

        recycle_bin_record = RecycleBin(
            object_id=item.id,
            object_type=RecycleBinObjectType.CATEGORY.value,
            operator="admin"
        )
        recycle_bin_relationships.append(recycle_bin_record)
    RecycleBin.objects.bulk_create(recycle_bin_relationships)


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0014_alter_profilecategory_status'),
    ]

    operations = [migrations.RunPython(forwards_func)]

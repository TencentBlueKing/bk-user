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

from collections import defaultdict

from django.db import migrations, models

# 非实名数据源类型的默认名称映射
TYPE_DEFAULT_NAME = {"builtin_management": "内置管理数据源", "virtual": "虚拟用户数据源"}


def forward_func(apps, schema_editor):
    """为已有数据源回填 name 字段，同租户冲突时追加序号"""
    DataSource = apps.get_model("data_source", "DataSource")
    by_tenant = defaultdict(list)
    for ds in DataSource.objects.select_related("plugin").order_by("id"):
        by_tenant[ds.owner_tenant_id].append(ds)

    # 按租户分组所有数据源
    for _, data_sources in by_tenant.items():
        used = set()
        for ds in data_sources:
            base = TYPE_DEFAULT_NAME.get(ds.type) or ds.plugin.name
            name, idx = base, 1
            while name in used:
                idx += 1
                name = f"{base} {idx}"
            used.add(name)
            ds.name = name
            # 数据源的数量不会很多，这里不使用 bulk_update
            ds.save(update_fields=["name"])


class Migration(migrations.Migration):
    dependencies = [("data_source", "0003_datasource_multi_source_support")]

    operations = [
        migrations.AddField(
            model_name="datasource",
            name="name",
            field=models.CharField(default="", max_length=64, verbose_name="数据源名称"),
            preserve_default=False,
        ),
        migrations.RunPython(forward_func, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name="datasource",
            unique_together={("name", "owner_tenant_id")},
        ),
    ]

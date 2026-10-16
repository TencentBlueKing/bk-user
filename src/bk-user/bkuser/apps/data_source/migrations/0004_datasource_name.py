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

from django.db import migrations, models

from bkuser.apps.data_source.name import gen_data_source_name


def forwards_func(apps, schema_editor):
    """为已有数据源回填名称"""
    DataSource = apps.get_model("data_source", "DataSource")
    for data_source in DataSource.objects.select_related("plugin"):
        data_source.name = gen_data_source_name(data_source.type, data_source.plugin.name)
        data_source.save(update_fields=["name"])


class Migration(migrations.Migration):
    dependencies = [("data_source", "0003_datasource_multi_source_support")]

    operations = [
        migrations.AddField(
            model_name="datasource",
            name="name",
            field=models.CharField(default="", max_length=64, verbose_name="数据源名称"),
            preserve_default=False,
        ),
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name="datasource",
            unique_together={("name", "owner_tenant_id")},
        ),
    ]

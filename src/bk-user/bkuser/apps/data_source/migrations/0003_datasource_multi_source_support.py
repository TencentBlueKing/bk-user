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
import django.db.models.deletion


def init_default_username_generate_configs(apps, schema_editor):
    DataSource = apps.get_model("data_source", "DataSource")
    DataSourceUsernameGenerateConfig = apps.get_model("data_source", "DataSourceUsernameGenerateConfig")

    existing_config_data_source_ids = set(
        DataSourceUsernameGenerateConfig.objects.values_list("data_source_id", flat=True)
    )

    to_create = []
    for data_source_id in DataSource.objects.values_list("id", flat=True):
        if data_source_id in existing_config_data_source_ids:
            continue

        to_create.append(
            DataSourceUsernameGenerateConfig(
                data_source_id=data_source_id,
                rule="unchanged",
                prefix="",
                suffix="",
            )
        )

    if to_create:
        DataSourceUsernameGenerateConfig.objects.bulk_create(to_create)


class Migration(migrations.Migration):

    dependencies = [
        ('data_source', '0002_init_builtin_data_source_plugin'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='datasource',
            unique_together=set(),
        ),
        migrations.CreateModel(
            name='DataSourceUsernameGenerateConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rule', models.CharField(choices=[('unchanged', '保持原始值'), ('add_affix', '添加前后缀')], default='unchanged', max_length=32, verbose_name='数据源用户名生成规则')),
                ('prefix', models.CharField(blank=True, default='', max_length=32, verbose_name='用户名前缀')),
                ('suffix', models.CharField(blank=True, default='', max_length=32, verbose_name='用户名后缀')),
                ('data_source', models.OneToOneField(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='username_generate_config', to='data_source.datasource')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(init_default_username_generate_configs),
    ]

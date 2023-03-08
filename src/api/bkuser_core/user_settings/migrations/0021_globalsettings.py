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

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_settings', '0020_add_reset_password_by_phone_confi'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(max_length=64, verbose_name='配置键')),
                ('value', jsonfield.fields.JSONField(default={}, verbose_name='配置内容')),
                ('enabled', models.BooleanField(default=True)),
                ('default', jsonfield.fields.JSONField(default=None, verbose_name='默认值')),
                ('choices', jsonfield.fields.JSONField(default=[], verbose_name='可选值')),
                ('namespace', models.CharField(choices=[('general', '通用')], db_index=True, default='general', max_length=32, verbose_name='命名空间')),
                ('region', models.CharField(default='default', max_length=32, verbose_name='领域')),
            ],
            options={
                'verbose_name': '配置元信息表',
                'verbose_name_plural': '配置元信息表',
                'ordering': ['-create_time'],
                'unique_together': {('key', 'namespace')},
                "db_table": "global_settings",
            },
        ),
    ]

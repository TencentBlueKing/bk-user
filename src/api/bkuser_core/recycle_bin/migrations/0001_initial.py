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


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RecycleBin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('object_type', models.CharField(choices=[('CATEGORY', '用户目录'), ('DEPARTMENT', '部门组织'), ('PROFILE', '人员')], default='', max_length=64, verbose_name='对象类型')),
                ('object_id', models.IntegerField(verbose_name='对象id')),
                ('operator', models.CharField(default='', max_length=255, verbose_name='操作人')),
            ],
            options={
                'verbose_name': '回收站信息',
                'verbose_name_plural': '回收站信息',
                'ordering': ['-create_time'],
                'index_together': {('object_type', 'object_id')},
            },
        ),
    ]

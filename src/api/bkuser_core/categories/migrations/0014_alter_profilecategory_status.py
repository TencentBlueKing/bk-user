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

    dependencies = [
        ('categories', '0013_alter_profilecategory_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilecategory',
            name='status',
            field=models.CharField(choices=[('normal', '正常'), ('inactive', '停用'), ('deleted', '删除')], default='normal', max_length=32, verbose_name='目录状态'),
        ),
    ]

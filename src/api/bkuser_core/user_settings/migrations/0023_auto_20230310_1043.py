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
        ('user_settings', '0022_add_global_recycling_strategy_settings'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='globalsettings',
            options={'ordering': ['-create_time'], 'verbose_name': '全局配置信息表', 'verbose_name_plural': '全局配置信息表'},
        ),
        migrations.AlterField(
            model_name='globalsettings',
            name='namespace',
            field=models.CharField(choices=[('general', '通用'), ('recycling_strategy', '回收策略')], db_index=True, default='general', max_length=32, verbose_name='命名空间'),
        ),
    ]

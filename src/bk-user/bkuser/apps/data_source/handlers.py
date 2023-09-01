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
import logging

from django.dispatch import receiver

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.data_source.signals import post_create_data_source

logger = logging.getLogger(__name__)


@receiver(post_create_data_source)
def after_data_source_created(sender, data_source: DataSource, **kwargs):
    """TODO 数据源创建后，需要执行相关初始化工作"""
    logger.info("receive post_create_data_source signal")

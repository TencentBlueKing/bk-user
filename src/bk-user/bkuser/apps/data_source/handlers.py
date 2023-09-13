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
from django.dispatch import receiver

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.data_source.signals import post_update_data_source


@receiver(post_update_data_source)
def initial_local_data_source_user_identity_info(sender, data_source: DataSource, **kwargs):
    """
    TODO (su) 数据源更新后，需要检查是否是本地数据源，若是本地数据源且启用账密登录，
    则需要对没有账密信息的用户，进行密码的初始化 & 发送通知
    """
    ...

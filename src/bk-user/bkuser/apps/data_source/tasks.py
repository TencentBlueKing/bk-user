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
from typing import Optional

from bkuser.apps.data_source.initializers import LocalDataSourceIdentityInfoInitializer
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.data_source.notifier import LocalDataSourceUserNotifier
from bkuser.celery import app
from bkuser.common.task import BaseTask
from bkuser.plugins.local.constants import NotificationScene

logger = logging.getLogger(__name__)


@app.task(base=BaseTask, ignore_result=True)
def initialize_identity_info_and_send_notification(data_source_id: int, user_id: Optional[int] = None):
    """初始化数据源用户账密数据，支持指定单个用户初始化 & 发送通知，适用于单个创建的情况"""
    logger.info("[celery] receive identity info initialize task, data_source %s user_id %s", data_source_id, user_id)
    data_source = DataSource.objects.get(id=data_source_id)
    # 非本地数据源直接跳过
    if not data_source.is_local:
        logger.debug("not local data source, skip initialize user identity infos")
        return

    initializer = LocalDataSourceIdentityInfoInitializer(data_source)
    if user_id is not None:
        # 若指定用户，则仅为指定的用户初始化 & 发送通知
        users = DataSourceUser.objects.filter(id=user_id)
        users, user_passwd_map = initializer.initialize(users)
    else:
        # 批量为没有账密信息的用户进行初始化
        users, user_passwd_map = initializer.initialize()

    # 逐一发送通知（邮件/短信）
    LocalDataSourceUserNotifier(data_source, NotificationScene.USER_INITIALIZE).send(users, user_passwd_map)

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

from celery.states import FAILURE

logger = logging.getLogger(__name__)


class AlertIfFailedHook:
    """当所有重试都失败时将告警通知"""

    def trigger(self, status: str, params: dict):
        if status == FAILURE:
            logger.error(
                "failed to sync data for category<%s> after %s retries", params["category"], params["retries"]
            )
            # 目前该 hook 更多是一个示例，并未实际实现告警通知功能
            # TODO: 使用 ESB 通知到平台管理员

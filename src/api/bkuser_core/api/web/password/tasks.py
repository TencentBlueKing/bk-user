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

from bkuser_core.celery import app
from bkuser_core.common.notifier import send_sms

logger = logging.getLogger(__name__)


@app.task
def send_reset_password_verification_code_sms(profile_id: str, send_config: dict):
    try:
        logger.info(
            "going to send verification_code of Profile(%s) via telephone(%s)",
            profile_id,
            send_config["receivers"],
        )
        send_sms(**send_config)
    except Exception:
        logger.exception(
            "Failed to send verification_code of Profile(%s) via telephone(%s): %s",
            profile_id,
            send_config["receivers"],
        )

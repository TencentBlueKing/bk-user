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
from bkuser_core.common.notifier import send_mail, send_sms


class ExpirationNotifier:
    def handler(self, notice_config):

        notice_method_map = {
            "send_email": self._notice_by_email,
            "send_sms": self._notice_by_sms,
        }

        for notice_method in notice_config:
            notice_method_map[notice_method](notice_config[notice_method])

    def _notice_by_email(self, email_config):
        send_mail(
            sender=email_config["sender"],
            receivers=email_config["receivers"],
            message=email_config["message"],
            title=email_config["title"],
        )

    def _notice_by_sms(self, sms_config):
        send_sms(sender=sms_config["sender"], receivers=sms_config["receivers"], message=sms_config["message"])

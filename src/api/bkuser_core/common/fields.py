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
from django.conf import settings
from django.db import models

from bkuser_core.common.encrypt import EncryptHandler


class EncryptField(models.TextField):
    """a field which will be encrypted via cryptography/fernet"""

    description = "a field which will be encrypted"

    def __init__(self, secret_key: bytes = settings.FERNET_ENCRYPT_SECRET_KEY, *args, **kwargs):
        super(EncryptField, self).__init__(*args, **kwargs)
        self.handler = EncryptHandler(secret_key=secret_key)

    def get_prep_value(self, value):
        if value is None:
            return value

        return self.handler.encrypt(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.get_prep_value(value)

    def from_db_value(self, value, *args, **kwargs):
        if value is None:
            return value

        return self.handler.decrypt(value)

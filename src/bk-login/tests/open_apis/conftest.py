# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
import os

import pytest
from django.test import Client
from django.test.utils import override_settings


@pytest.fixture
def open_api_client() -> Client:
    client = Client()

    # Set new environment variables
    os.environ["APIGW_MANAGER_DUMMY_GATEWAY_NAME"] = "bk-login"
    os.environ["APIGW_MANAGER_DUMMY_PAYLOAD_APP_CODE"] = "app_code"
    os.environ["APIGW_MANAGER_DUMMY_PAYLOAD_USERNAME"] = "username"

    with override_settings(BK_APIGW_JWT_PROVIDER_CLS="apigw_manager.apigw.providers.DummyEnvPayloadJWTProvider"):
        yield client

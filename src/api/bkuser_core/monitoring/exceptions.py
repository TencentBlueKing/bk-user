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


class StatusMissError(Exception):
    def __init__(self, status_code, desire_code, *args, **kwargs):
        msg = f"response status code<{status_code}> is not equal to desire code<{desire_code}>"
        super().__init__(msg, *args, **kwargs)


class SystemNotHealthyError(Exception):
    def __init__(self, system_name, message, *args, **kwargs):
        msg = f"system<{system_name}> is not health, got message: {message}"
        super().__init__(msg, *args, **kwargs)


class NoDeadlyIssueError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("no exact deadly issue, please offer one", *args, **kwargs)

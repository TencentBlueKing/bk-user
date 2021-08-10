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

from bkuser_shell.version_log.utils import get_version_list


class TestGetVersionLogs:
    def test_version_log_info(self):
        """
        测试版本日志格式
        :return:
        """
        version_set = get_version_list()

        assert version_set.versions, "外层 versions 字段不存在"

        for version in version_set.versions:
            assert version.version, "version 字段不存在"
            assert version.changeLogs, "changeLogs 字段不存在"

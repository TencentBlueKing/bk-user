# coding: utf-8

"""
    蓝鲸用户管理 API

    蓝鲸用户管理后台服务 API  # noqa: E501

    OpenAPI spec version: v2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import unittest

import bkuser_sdk
from api.sync_task_api import SyncTaskApi  # noqa: E501
from bkuser_sdk.rest import ApiException


class TestSyncTaskApi(unittest.TestCase):
    """SyncTaskApi unit test stubs"""

    def setUp(self):
        self.api = api.sync_task_api.SyncTaskApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_v2_sync_task_list(self):
        """Test case for v2_sync_task_list

        """
        pass

    def test_v2_sync_task_show_logs(self):
        """Test case for v2_sync_task_show_logs

        """
        pass


if __name__ == '__main__':
    unittest.main()

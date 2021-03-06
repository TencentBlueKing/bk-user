# coding: utf-8

"""
    蓝鲸用户管理 API

    User management APIs for BlueKing  # noqa: E501

    OpenAPI spec version: v2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import unittest

import bkuser_sdk
from api.healthz_api import HealthzApi  # noqa: E501
from bkuser_sdk.rest import ApiException


class TestHealthzApi(unittest.TestCase):
    """HealthzApi unit test stubs"""

    def setUp(self):
        self.api = api.healthz_api.HealthzApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_healthz(self):
        """Test case for healthz

        """
        pass


if __name__ == '__main__':
    unittest.main()

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

import requests
import json
import logging

from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import exceptions as local_exceptions
from .constants import ACCESS_TOKEN_URL, DEPARTMENT_LIST_URL, USER_LIST_DETAIL


if TYPE_CHECKING:
    from bkuser_core.user_settings.loader import ConfigProvider


logger = logging.getLogger(__name__)


@dataclass
class WeComClient:

    config_provider: "ConfigProvider"

    def __post_init__(self):
        self.corpid = self.config_provider.get("wecom_corpid").get("wecom_corpid")
        self.secret = self.config_provider.get("wecom_secret").get("wecom_secret")
        self.access_token = ""

    @staticmethod
    def __request_get(url: str) -> dict:
        """
        request get 请求
        :param url:
        :return:
        """
        try:
            response = requests.get(url)
        except Exception as e:
            logger.exception("request wecom api failed,url={}, error={}".format(url, e))
            raise local_exceptions.WeComAPIRequestFailed
        if response.status_code != 200:
            logger.error("request wecom api failed,url={},status_code={}".format(url, response.status_code))
            raise local_exceptions.WeComAPIRequestStatusCodeError
        else:
            try:
                result = json.loads(response.content)
            except Exception as e:
                logger.exception("json loads wecom api return fail, error={}".format(e))
                raise local_exceptions.WeComAPIRequestJsonLoadError
        return result

    def __get_access_token(self) -> str:
        """
        获取访问企业微信的access_token
        :return:
        """
        if self.access_token:
            return self.access_token
        url = ACCESS_TOKEN_URL.format(self.corpid, self.secret)
        res = self.__request_get(url)
        if res.get('errcode') == 0:
            access_token = res.get('access_token', '')
        else:
            logger.error("get access_token failed, res={}".format(res))
            raise local_exceptions.WeComAPIGetAccessTokenError
        self.access_token = access_token
        return access_token

    def get_departments(self) -> list:
        """
        获取部门列表
        :return:
        """
        url = DEPARTMENT_LIST_URL.format(self.__get_access_token())
        res = self.__request_get(url)
        if res.get('errcode') == 0:
            departments = res.get('department', [])
        else:
            logger.error("get departments failed, res={}".format(res))
            raise local_exceptions.WeComAPIGetDepartmentError
        return departments

    def get_user_info(self, departments: list) -> list:
        """
        获取用户列表
        :param departments: 部门列表
        :return:
        """
        user_list = []
        for department in departments:
            url = USER_LIST_DETAIL.format(self.__get_access_token(), department['id'], 0)
            res = self.__request_get(url)
            if res.get('errcode') == 0:
                user_list.extend(res.get('userlist', []))
            else:
                logger.error("get user list failed, res={}".format(res))
                raise local_exceptions.WeComAPIGetDepartmentError
        # 去重
        new_user_list = self.__uniq_user_info(user_list)
        return new_user_list

    @staticmethod
    def __uniq_user_info(user_list: list) -> list:
        """
        将从企业微信获取的用户去重
        :param user_list:
        :return:
        """
        user_ids = []
        new_user_list = []
        for user in user_list:
            if user.get("userid") not in user_ids:
                user_ids.append(user.get("userid"))
                new_user_list.append(user)
        return new_user_list

    def check(self, corpid, secret):
        # todo check corpid and secret
        pass

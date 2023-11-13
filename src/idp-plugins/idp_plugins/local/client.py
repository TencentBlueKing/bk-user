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
from typing import Any, Dict, List
from urllib.parse import urljoin

from requests.auth import HTTPBasicAuth

from .settings import BK_USER_API_URL, BK_USER_APP_CODE, BK_USER_APP_SECRET
from ..exceptions import RequestAPIError, ValidationError
from ..http import http_post

logger = logging.getLogger(__name__)


class BkUserAPIClient:
    """请求蓝鲸用户管理接口的Client"""

    def __init__(self):
        # 接口调用认证
        self.auth = HTTPBasicAuth(BK_USER_APP_CODE, BK_USER_APP_SECRET)

    def _call(self, http_func, url_path: str, **kwargs) -> Dict[str, Any]:
        """调用用户管理接口"""
        # FIXME (nan): 对于密码，是敏感信息，不应该出现在日志里
        url = urljoin(BK_USER_API_URL, url_path)
        # API认证
        kwargs.setdefault("auth", self.auth)
        status, resp_data = http_func(url, **kwargs)
        if status.is_invalid:
            logger.error(
                "bk_user api failed, %s %s, kwargs: %s, error: %s", http_func.__name__, url, kwargs, resp_data["error"]
            )
            raise RequestAPIError(
                f"request bk_user api fail! Request=[{http_func.__name__} {url} error={resp_data['error']}"
            )

        # 除20x外，对于 40x 异常，需要根据 error code 进行处理的，所以这里不直接抛异常，直接原始返回
        if status.is_success or status.is_client_error:
            return resp_data

        error = resp_data.get("error")
        logger.error("bk_user api error,  %s %s, data: %s, error: %s", http_func.__name__, url, kwargs, error)
        raise RequestAPIError(
            f"request bk_user api error! " f"Request=[{http_func.__name__} {url} Response[error={error}]"
        )

    def auth_credentials_of_local_user(
        self, data_source_ids: List[int], username: str, password: str
    ) -> List[Dict[str, Any]]:
        """
        认证指定本地数据源的用户凭据
        Note: 由于不同数据源有极小概率出现同名同密，所以可能会查询到多个用户
        :return 认证成功的用户列表，一般只会有一个用户
        """
        resp_data = self._call(
            http_post,
            "/api/v1/login/local-user-credentials/authenticate/",
            json={"data_source_ids": data_source_ids, "username": username, "password": password},
        )

        # FIXME: 后续支持调用点判断，不直接返回ValidationError，比如密码过期，获取error.data里的url进行重置密码
        if error := resp_data.get("error", {}):
            raise ValidationError(error["message"])

        return resp_data["data"]

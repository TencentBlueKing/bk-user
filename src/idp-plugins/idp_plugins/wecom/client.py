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
from typing import Any, Dict, Tuple
from urllib.parse import urljoin

from django.utils.translation import gettext_lazy as _

from .settings import WECOM_API_BASE_URL
from ..exceptions import RequestAPIError, UnexpectedDataError
from ..http import http_get_20x

logger = logging.getLogger(__name__)


class WeComAPIClient:
    """请求企微接口的Client"""

    def __init__(self, corp_id: str, agent_id: str, secret: str):
        self.corp_id = corp_id
        self.agent_id = agent_id
        self.secret = secret

    def _call(self, http_func, url_path: str, **kwargs) -> Dict[str, Any]:
        """调用企业微信接口"""
        url = urljoin(WECOM_API_BASE_URL, url_path)
        ok, resp_data = http_func(url, **kwargs)
        if not ok:
            logger.error(
                "wecom api failed, [corp_id=%s, agent_id=%s]! %s %s, kwargs: %s, error: %s",
                self.corp_id,
                self.agent_id,
                http_func.__name__,
                url,
                kwargs,
                resp_data["error"],
            )
            raise RequestAPIError(
                f"request wecom api fail! Request=[{http_func.__name__} {url} error={resp_data['error']}"
            )

        errcode = resp_data.get("errcode") or 0
        # 出错返回码，为0表示成功，非0表示调用失败
        if not errcode:
            return resp_data

        errmsg = resp_data.get("errmsg", "unknown")
        logger.error(
            "wecom api error, [corp_id=%s, agent_id=%s]! %s %s, data: %s, errcode: %s, errmsg: %s",
            self.corp_id,
            self.agent_id,
            http_func.__name__,
            url,
            kwargs,
            errcode,
            errmsg,
        )
        raise RequestAPIError(
            f"request wecom api error! "
            f"Request=[{http_func.__name__} {url} Response[code={errcode}, message={errmsg}]"
        )

    def _get_access_token(self) -> Tuple[str, int]:
        """
        获取Agent的AccessToken
        docs: https://developer.work.weixin.qq.com/document/path/91039
        """
        params = {"corpid": self.corp_id, "corpsecret": self.secret}

        resp_data = self._call(http_get_20x, "/gettoken", params=params)
        return resp_data["access_token"], resp_data["expires_in"]

    @property
    def access_token(self) -> str:
        # TODO: 先从缓存获取，获取不到再调用接口查询
        # FIXME: 如何引入外部存储共享缓存呢？比如Redis如何支持多种部署方式(单实例、集群、Sentinel)
        access_token, expires_in = self._get_access_token()
        return access_token

    def get_user_id_by_code(self, code: str) -> str:
        """
        通过OAuth授权码获取用户ID
        docs: https://developer.work.weixin.qq.com/document/path/98176
        """
        params = {"access_token": self.access_token, "code": code}
        resp_data = self._call(http_get_20x, "/auth/getuserinfo", params=params)
        userid = resp_data.get("userid")
        if userid:
            return userid

        raise UnexpectedDataError(_("非企业成员，登录认证失败"))

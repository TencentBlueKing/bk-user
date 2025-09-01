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

import logging
from typing import Any, Dict, Tuple
from urllib.parse import urlparse

from django.conf import settings

from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum
from bkuser.common.error_codes import error_codes
from bkuser.common.local import local
from bkuser.component.apigw import _call_apigw_api
from bkuser.component.esb import _call_esb_api
from bkuser.component.http import http_get
from bkuser.utils.url import urljoin

logger = logging.getLogger(__name__)

# 企业微信 API 基础URL
WECOM_API_BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"


class WeComAccessTokenManager:
    """
    企业微信 Access Token 管理器，负责企业微信 access_token 的获取、缓存和管理
    """

    def __init__(self, corp_id: str, corp_secret: str, tenant_id: str):
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.WECOM_API_ACCESS_TOKEN)
        self.tenant_id = tenant_id

    def _call_wecom_api(self, http_func, url_path: str, **kwargs) -> Dict[str, Any]:
        request_id = local.request_id
        url = urljoin(WECOM_API_BASE_URL, url_path)

        # 添加请求头
        kwargs.setdefault("headers", {})
        kwargs["headers"]["X-Request-Id"] = request_id

        ok, resp_data = http_func(url, **kwargs)
        if not ok:
            logger.error(
                "wecom api failed! %s %s, corp_id: %s, corp_secret: %s, request_id: %s, error: %s",
                http_func.__name__,
                url,
                self.corp_id,
                self.corp_secret,
                request_id,
                resp_data["error"],
            )
            raise error_codes.REMOTE_REQUEST_ERROR.format(
                f"request wecom api fail! "
                f"Request=[{http_func.__name__} {urlparse(url).path} request_id={request_id}]"
                f"error={resp_data['error']}"
            )

        # 检查企业微信业务错误码
        errcode = resp_data.get("errcode", 0)
        if errcode != 0:
            errmsg = resp_data.get("errmsg", "unknown")
            logger.error(
                "wecom api error! %s %s, corp_id: %s, corp_secret: %s, request_id: %s, errcode: %s, errmsg: %s",
                http_func.__name__,
                url,
                self.corp_id,
                self.corp_secret,
                request_id,
                errcode,
                errmsg,
            )
            raise error_codes.REMOTE_REQUEST_ERROR.format(
                f"request wecom api error! "
                f"Request=[{http_func.__name__} {urlparse(url).path} request_id={request_id}]"
                f"Response[code={errcode}, message={errmsg}]"
            )

        return resp_data

    def _get_access_token_cache_key(self) -> str:
        """生成 access_token 缓存键"""
        return f"{self.corp_id}:{self.corp_secret}"

    def _fetch_access_token(self) -> Tuple[str, int]:
        """从企业微信 API 获取 access_token"""
        params = {"corpid": self.corp_id, "corpsecret": self.corp_secret}

        resp_data = self._call_wecom_api(http_get, "/gettoken", params=params)
        access_token = resp_data["access_token"]
        expires_in = resp_data["expires_in"]

        logger.info(
            "fetched access_token from wecom api, corp_id: %s, expires_in: %s",
            self.corp_id,
            expires_in,
        )

        return access_token, expires_in

    def get_access_token(self) -> str:
        """获取 access_token，优先从缓存获取，缓存失效则从 API 获取并缓存"""
        cache_key = self._get_access_token_cache_key()

        # 尝试从缓存获取
        access_token = self.cache.get(cache_key)
        if access_token:
            logger.debug("access_token hit cache, corp_id: %s, corp_secret: %s", self.corp_id, self.corp_secret)
            return access_token

        # 获取蓝鲸 CMSI 中的微信配置
        wecom_config = get_wecom_config(self.tenant_id)
        corp_id = wecom_config.get("corp_id", "")
        corp_secret = wecom_config.get("corp_secret", "")

        # 如果传入的 corp_id 和 corp_secret 与蓝鲸 CMSI 配置一致，则使用蓝鲸 CMSI 接口获取 access_token
        if self.corp_id == corp_id and self.corp_secret == corp_secret:
            access_token = get_access_token_from_cmsi(self.tenant_id)
        else:
            # 否则直接使用传入的 corp_id 和 corp_secret 请求 access_token
            access_token, expires_in = self._fetch_access_token()
            self.cache.set(cache_key, access_token, expires_in - 300)
        return access_token


def get_wecom_config(tenant_id: str) -> Dict[str, Any]:
    """获取蓝鲸 CMSI 中的微信配置"""
    if settings.ENABLE_MULTI_TENANT_MODE:
        return _call_apigw_api(http_get, "bk-cmsi", "/v1/channels/weixin/settings/", tenant_id)
    return _call_esb_api(http_get, "/api/c/compapi/esb/get_weixin_config/")


def get_access_token_from_cmsi(tenant_id: str) -> str:
    """从蓝鲸 CMSI 获取 access_token"""
    if settings.ENABLE_MULTI_TENANT_MODE:
        resp_data = _call_apigw_api(http_get, "bk-cmsi", "/v1/channels/weixin/token/", tenant_id)
    else:
        resp_data = _call_esb_api(http_get, "/api/c/compapi/weixin/get_token/")

    return resp_data["access_token"]

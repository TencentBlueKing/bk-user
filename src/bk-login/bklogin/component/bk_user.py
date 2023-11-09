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

from django.conf import settings
from requests.auth import HTTPBasicAuth

from bklogin.common.error_codes import error_codes

from .http import http_get, http_post

logger = logging.getLogger(__name__)


def _call_bk_user_api(http_func, url_path: str, **kwargs):
    """调用用户管理接口"""
    url = urljoin(settings.BK_USER_API_URL, url_path)
    # 内部 API 认证
    kwargs.setdefault("auth", HTTPBasicAuth(settings.BK_USER_APP_CODE, settings.BK_USER_APP_SECRET))

    status, resp_data = http_func(url, **kwargs)
    if status.is_invalid:
        logger.error(
            "bk_user api failed, %s %s, kwargs: %s, error: %s", http_func.__name__, url, kwargs, resp_data["error"]
        )
        raise error_codes.REMOTE_REQUEST_ERROR.f(
            f"request bk_user api fail! Request=[{http_func.__name__} {url} error={resp_data['error']}"
        )

    # 对于预期内的状态码，这里不直接抛异常，直接返回
    if status.is_success:
        return resp_data["data"]

    error = resp_data.get("error")
    logger.error("bk_user api error,  %s %s, data: %s, error: %s", http_func.__name__, url, kwargs, error)
    raise error_codes.REMOTE_REQUEST_ERROR.f(
        f"request bk_user api error! " f"Request=[{http_func.__name__} {url} Response[error={error}]"
    )


def get_global_setting() -> Dict[str, Any]:
    """获取全局配置"""
    return _call_bk_user_api(http_get, "/api/v1/login/global-settings/")


def list_tenant(tenant_ids: List[str] | None = None) -> List[Dict]:
    """查询租户列表，支持过滤"""
    params = {}
    if tenant_ids:
        params["tenant_ids"] = ",".join(tenant_ids)

    return _call_bk_user_api(http_get, "/api/v1/login/tenants/", params=params)


def get_tenant(tenant_id: str) -> Dict:
    """通过租户 ID 获取租户信息"""
    return _call_bk_user_api(http_get, f"/api/v1/login/tenants/{tenant_id}")


def list_idp(tenant_id: str) -> List[Dict]:
    """获取租户关联的认证源"""
    return _call_bk_user_api(http_get, f"/api/v1/login/tenants/{tenant_id}/idps/")


def get_idp(idp_id: str) -> Dict:
    """获取IDP信息"""
    return _call_bk_user_api(http_get, f"/api/v1/login/idps/{idp_id}/")


def list_matched_tencent_user(tenant_id: str, idp_id: str, idp_users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """根据IDP用户查询匹配的租户用户"""
    return _call_bk_user_api(
        http_post,
        f"/api/v1/login/tenants/{tenant_id}/idps/{idp_id}/matched-tenant-users/",
        json={"idp_users": idp_users},
    )

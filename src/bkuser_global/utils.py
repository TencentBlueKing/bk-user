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
import datetime
import os
import requests
import json
from urllib.parse import urljoin
from typing import Union

from django.utils.timezone import get_current_timezone
_UI_CONFIG_CACHE = None

def get_timezone_offset():
    """获取timezone偏移量"""
    dt = datetime.datetime.utcnow()
    offset_seconds = get_current_timezone().utcoffset(dt).seconds
    return datetime.timedelta(seconds=offset_seconds)


def force_str_2_bool(bool_str: Union[str, bool], raise_if_unknown: bool = False) -> bool:
    """convent 'True' or 'False' to bool, using on query_param"""
    if isinstance(bool_str, bool):
        return bool_str

    if bool_str in ["True", "true", "1"]:
        return True
    elif bool_str in ["False", "false", "0"]:
        return False

    if raise_if_unknown:
        raise ValueError("str should be 'True/true' or 'False/false' ")

    # unknown str regard as False
    return False

def get_custom_ui_url(prefix, name):
    global _UI_CONFIG_CACHE
    bk_shared_res_url = os.getenv("BK_SHARED_RES_URL", "")
    if not bk_shared_res_url:
        return ""

    if _UI_CONFIG_CACHE is None:
        try:
            resp = requests.get(urljoin(bk_shared_res_url, f"{prefix}/base.js"), verify=False, timeout=5)
            resp.raise_for_status()
            raw_data = resp.text.replace("__platCfgCallback__(", "").rstrip(")")
            _UI_CONFIG_CACHE = json.loads(raw_data)
        except Exception as e:
            return ""

    return _UI_CONFIG_CACHE.get(name, "")
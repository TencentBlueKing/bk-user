# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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
import unicodedata
from typing import Set
from urllib.parse import urlparse

from django.http.request import split_domain_port, validate_host


# Copied from django.utils.http.url_has_allowed_host_and_scheme()
def url_has_allowed_host_and_scheme(
    url: str | None, allowed_hosts: Set | str | None, require_https: bool = False
) -> bool:
    """
    Return ``True`` if the url uses an allowed host and a safe scheme.

    Always return ``False`` on an empty url.

    If ``require_https`` is ``True``, only 'https' will be considered a valid
    scheme, as opposed to 'http' and 'https' with the default, ``False``.

    Note: "True" doesn't entail that a URL is "safe". It may still be e.g.
    quoted incorrectly. Ensure to also use django.utils.encoding.iri_to_uri()
    on the path component of untrusted URLs.
    """
    if url is not None:
        url = url.strip()

    if not url:
        return False

    if allowed_hosts is None:
        allowed_hosts = set()
    elif isinstance(allowed_hosts, str):
        allowed_hosts = {allowed_hosts}

    # Chrome treats \ completely as / in paths but it could be part of some
    # basic auth credentials so we need to check both URLs.
    return _url_has_allowed_host_and_scheme(
        url, allowed_hosts, require_https=require_https
    ) and _url_has_allowed_host_and_scheme(url.replace("\\", "/"), allowed_hosts, require_https=require_https)


# Copied from django.utils.http._url_has_allowed_host_and_scheme()
# but additional support for wildcard domain matching.
# 支持匹配:
#  (1) * 匹配任意域名
#  (2) 泛域名匹配，比如 .example.com 可匹配 foo.example.com、example.com、foo.example.com:8000、example.com:8080
#  (3) 精确域名匹配，比如 example.com 可匹配 example.com、example.com:8000
#  (4) 精确域名&端口匹配，比如 example.com:9000 只可匹配 example.com:9000
def _url_has_allowed_host_and_scheme(url: str, allowed_hosts: Set, require_https: bool = False):
    # Chrome considers any URL with more than two slashes to be absolute, but
    # urlparse is not so flexible. Treat any url with three slashes as unsafe.
    if url.startswith("///"):
        return False
    try:
        url_info = urlparse(url)
    except ValueError:  # e.g. invalid IPv6 addresses
        return False

    # Forbid URLs like http:///example.com - with a scheme, but without a hostname.
    # In that URL, example.com is not the hostname but, a path component. However,
    # Chrome will still consider example.com to be the hostname, so we must not
    # allow this syntax.
    if not url_info.netloc and url_info.scheme:
        return False

    # Forbid URLs that start with control characters. Some browsers (like
    # Chrome) ignore quite a few control characters at the start of a
    # URL and might consider the URL as scheme relative.
    if unicodedata.category(url[0])[0] == "C":
        return False

    # Check if the scheme is valid.
    scheme = url_info.scheme
    # Consider URLs without a scheme (e.g. //example.com/p) to be http.
    if not url_info.scheme and url_info.netloc:
        scheme = "http"
    valid_schemes = ["https"] if require_https else ["http", "https"]
    if scheme and scheme not in valid_schemes:
        return False

    # Check if netloc is in allowed_hosts
    if not url_info.netloc or url_info.netloc in allowed_hosts:
        return True

    # Check wildcard domain matching
    # Copied from django.http.request.HttpRequest.get_host()
    domain, port = split_domain_port(url_info.netloc)
    return domain and validate_host(domain, allowed_hosts)

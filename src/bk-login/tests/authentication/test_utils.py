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
import pytest
from bklogin.authentication.utils import url_has_allowed_host_and_scheme


class TestURLHasAllowedHostAndScheme:
    @pytest.mark.parametrize(
        "bad_url",
        [
            "http://example.com",
            "http:///example.com",
            "https://example.com",
            "ftp://example.com",
            r"\\example.com",
            r"\\\example.com",
            r"/\\/example.com",
            r"\\//example.com",
            r"/\/example.com",
            r"\/example.com",
            r"/\example.com",
            r"http:/\//example.com",
            r"http:\/example.com",
            r"http:/\example.com",
            'javascript:alert("XSS")',
            "\njavascript:alert(x)",
            "java\nscript:alert(x)",
            "\x08//example.com",
            r"http://otherserver\@example.com",
            r"http:\\testserver\@example.com",
            r"http://testserver\me:pass@example.com",
            r"http://testserver\@example.com",
            r"http:\\testserver\confirm\me@example.com",
            "http:999999999",
            "ftp:9999999999",
            "\n",
            "http://[2001:cdba:0000:0000:0000:0000:3257:9652/",
            "http://2001:cdba:0000:0000:0000:0000:3257:9652]/",
        ],
    )
    def test_bad_urls(self, bad_url):
        assert not url_has_allowed_host_and_scheme(bad_url, allowed_hosts={"testserver", "testserver2"})

    @pytest.mark.parametrize(
        "good_url",
        [
            "/view/?param=http://example.com",
            "/view/?param=https://example.com",
            "/view?param=ftp://example.com",
            "view/?param=//example.com",
            "https://testserver/",
            "HTTPS://testserver/",
            "//testserver/",
            "http://testserver/confirm?email=me@example.com",
            "/url%20with%20spaces/",
            "path/http:2222222222",
        ],
    )
    def test_good_urls(self, good_url):
        assert url_has_allowed_host_and_scheme(good_url, allowed_hosts={"testserver", "otherserver"})

    def test_basic_auth(self):
        assert url_has_allowed_host_and_scheme(r"http://user:pass@testserver/", allowed_hosts={"user:pass@testserver"})

    def test_no_allowed_hosts(self):
        assert url_has_allowed_host_and_scheme("/confirm/me@example.com", allowed_hosts=None)
        assert not url_has_allowed_host_and_scheme(r"http://testserver\@example.com", allowed_hosts=None)

    def test_allowed_hosts_str(self):
        assert url_has_allowed_host_and_scheme("http://good.com/good", allowed_hosts="good.com")
        assert not url_has_allowed_host_and_scheme("http://good.co/evil", allowed_hosts="good.com")

    @pytest.mark.parametrize(
        ("url", "excepted"),
        [
            ("https://example.com/p", True),
            ("HTTPS://example.com/p", True),
            ("/view/?param=http://example.com", True),
            ("http://example.com/p", False),
            ("ftp://example.com/p", False),
            ("//example.com/p", False),
        ],
    )
    def test_scheme_param_urls(self, url, excepted):
        assert url_has_allowed_host_and_scheme(url, allowed_hosts={"example.com"}, require_https=True) == excepted

    @pytest.mark.parametrize(
        ("url", "allowed_hosts", "excepted"),
        [
            # * 匹配任意域名
            ("https://wwww.example.com", "*", True),
            ("https://wwww.example1.com/p1/p2", "*", True),
            ("https://[2001:cdba:0000:0000:0000:0000:3257:9652/", "*", False),
            # 泛域名匹配
            ("https://foo.example.com", ".example.com", True),
            ("https://example.com", ".example.com", True),
            ("https://www.foo.example.com", ".example.com", True),
            ("https://foo.example.com:1111", ".example.com", True),
            ("https://foo.example.com:1111/p1/p2", ".example.com", True),
            ("https://foo.example1.com", ".example.com", False),
            # 精确域名匹配
            ("https://example.com", "example.com", True),
            ("https://example.com:1111", "example.com", True),
            ("https://foo.example.com", "example.com", False),
            # 精确域名&端口匹配
            ("https://example.com:1111", "example.com:1111", True),
            ("https://example.com", "example.com:1111", False),
            ("https://example.com:2222", "example.com:1111", False),
            ("https://foo.example.com", "example.com:1111", False),
        ],
    )
    def test_wildcard_domain(self, url, allowed_hosts, excepted):
        assert url_has_allowed_host_and_scheme(url, allowed_hosts=allowed_hosts, require_https=True) == excepted

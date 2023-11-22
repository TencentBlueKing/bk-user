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


def urljoin(host: str, path: str) -> str:
    """
    拼接host, path生成url，核心是处理host, path有多余/的情况
    Q: 为什么不直接使用 urllib.parse.urljoin
    A: urllib.parse.urljoin 会根据path是否带"/"前缀，对host的带部分path进行移除
       urllib.parse.urljoin("https://example.com/abc", "/efg/index.html") => "https://example.com/efg/index.html"
    """
    return "{}/{}".format(host.rstrip("/"), path.lstrip("/"))

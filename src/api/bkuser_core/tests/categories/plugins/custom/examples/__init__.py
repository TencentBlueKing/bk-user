#!/usr/bin/env python
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
import json
import sys
from wsgiref.simple_server import make_server

from handlers.departments import serve as make_departments
from handlers.profiles import serve as make_profiles

handlers = {
    "/cgi-bin/departments.py": lambda: [json.dumps(make_departments()).encode("utf-8")],
    "/cgi-bin/profiles.py": lambda: [json.dumps(make_profiles()).encode("utf-8")],
}


def wsgi_app(environ, start_response):
    headers = [('Content-type', 'Content-type: application/json')]  # HTTP Headers
    path = environ["PATH_INFO"]
    if path not in handlers:
        status = '404 NOT FOUND'  # HTTP Status
        start_response(status, headers)
        return [json.dumps({"message": "404"}).encode("utf-8")]
    status = "200 OK"
    start_response(status, headers)
    return handlers[path]()


if __name__ == "__main__":
    with make_server('localhost', 8002, wsgi_app) as httpd:
        sa = httpd.socket.getsockname()
        serve_message = "Serving HTTP on {host} port {port} (http://{host}:{port}/) ..."
        print(serve_message.format(host=sa[0], port=sa[1]))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)

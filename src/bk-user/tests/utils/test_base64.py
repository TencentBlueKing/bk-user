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
import base64
import os
import tempfile
from pathlib import Path

import pytest
from bkuser.utils.base64 import load_image_as_base64


def test_load_image_as_base64():
    # 生成临时图片文件
    with tempfile.NamedTemporaryFile(suffix=".png") as img:
        img.write(os.urandom(40))
        img.flush()

        b64content = load_image_as_base64(Path(img.name))
        with open(img.name, "rb") as f:
            expected = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")

        assert b64content == expected


def test_load_image_as_base64_with_not_png():
    # 生成临时图片文件
    with tempfile.NamedTemporaryFile(suffix=".jpg") as img:
        img.write(os.urandom(40))
        img.flush()

        with pytest.raises(ValueError, match="only PNG image supported"):
            load_image_as_base64(Path(img.name))

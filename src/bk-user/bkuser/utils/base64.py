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
from pathlib import Path


def load_image_as_base64(image_path: Path) -> str:
    """加载指定的 PNG 图片文件，并转换成 base64 字符串"""
    if image_path.suffix != ".png":
        raise ValueError("only PNG image supported")

    with open(image_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    return "data:image/png;base64," + content

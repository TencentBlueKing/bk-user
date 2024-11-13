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

import json
from typing import Any, Dict

from django.core.serializers.json import DjangoJSONEncoder
from django.forms import model_to_dict


def get_model_dict(obj) -> Dict[str, Any]:
    # 获取模型的所有字段名称
    fields = [field.name for field in obj._meta.fields]
    # 将模型对象转换为字典
    model_dict = model_to_dict(obj, fields=fields)
    # 使用 DjangoJSONEncoder 将字典转换为 JSON 字符串，然后再解析回字典
    return json.loads(json.dumps(model_dict, cls=DjangoJSONEncoder))

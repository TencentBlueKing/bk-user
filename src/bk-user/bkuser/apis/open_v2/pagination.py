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
from bkuser.common.pagination import CustomPageNumberPagination


class LegacyOpenApiPagination(CustomPageNumberPagination):
    # 兼容 API 单页默认返回条数与老版本保持一致
    page_size = 50
    page_size_query_param = "page_size"
    # 兼容 API 单页返回条数上限与老版本默认值保持一致
    max_page_size = 2000

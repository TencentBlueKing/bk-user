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

from bkuser_core.categories.plugins.custom.models import CustomTypeList
from bkuser_core.common.progress import progress

logger = logging.getLogger(__name__)


def handle_with_progress_info(item_list: CustomTypeList, progress_title: str, continue_if_exception: bool = True):
    """控制进度"""
    total = len(item_list)
    for index, (key, item) in enumerate(item_list.items_map.items()):
        try:
            progress(
                index + 1,
                total,
                f"{progress_title}: {item.display_str}<{key}> ({index + 1}/{total})",
            )
            yield item
        except Exception:
            logger.exception("%s failed", progress_title)
            if continue_if_exception:
                continue

            raise

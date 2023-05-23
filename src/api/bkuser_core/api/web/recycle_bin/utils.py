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

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.recycle_bin.constants import RecycleBinObjectType
from bkuser_core.recycle_bin.models import RecycleBin

logger = logging.getLogger(__name__)


def check_category_in_recycle_bin(category_id):

    try:
        instance = ProfileCategory.objects.get(id=category_id)
        if instance.default:
            logger.warning("Category<%s-%s> is default, can not delete", instance.id, instance.display_name)
            return

        RecycleBin.objects.get(object_type=RecycleBinObjectType.CATEGORY.value, object_id=category_id)

    except ProfileCategory.DoesNotExist:
        raise error_codes.CANNOT_FIND_CATEGORY

    except RecycleBin.DoesNotExist:
        raise error_codes.CANNOT_FIND_CATEGORY_IN_RECYCLE_BIN.f(category_id=category_id)

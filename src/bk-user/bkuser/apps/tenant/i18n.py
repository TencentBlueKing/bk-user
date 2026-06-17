# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from django.utils.translation import gettext_lazy as _

USER_BUILTIN_FIELD_DISPLAY_NAMES = {
    "username": _("用户名"),
    "full_name": _("姓名"),
    "email": _("邮箱"),
    "phone": _("手机号"),
    "phone_country_code": _("手机国际区号"),
}


def get_user_builtin_field_display_name(field) -> str:
    return str(USER_BUILTIN_FIELD_DISPLAY_NAMES.get(field.name, field.display_name))

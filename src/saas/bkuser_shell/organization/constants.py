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
from django.utils.translation import ugettext_lazy as _

from bkuser_shell.common.constants import ChoicesEnum


class ProfileWildSearchFieldEnum(ChoicesEnum):
    EMAIL = "email"
    QQ = "qq"
    USERNAME = "username"
    DISPLAY_NAME = "display_name"
    TELEPHONE = "telephone"
    EXTRAS = "extras"

    _choices_labels = (
        (EMAIL, _("邮箱")),
        (QQ, _("QQ")),
        (DISPLAY_NAME, _("全名")),
        (TELEPHONE, _("手机号")),
        (EXTRAS, _("自定义字段")),
        (USERNAME, _("用户名")),
    )

    @classmethod
    def to_list(cls):
        return [e[0] for e in cls.get_choices()]


# 账户设置类型
ACCOUNT_NAMESPACE = "account"
# 账户有效期选项
ACCOUNT_EXPIRATION_DATE = "expired_after_days"
# 账户有效期为永久
PERMANENT = -1

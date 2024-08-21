# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _


class PersonalCenterFeatureFlag(str, StructuredEnum):
    CAN_CHANGE_PASSWORD = EnumField("can_change_password", label=_("修改密码"))
    UPDATE_PHONE_PERMISSION = EnumField("update_phone_permission", label=_("修改手机号权限"))
    UPDATE_EMAIL_PERMISSION = EnumField("update_email_permission", label=_("修改邮箱权限"))


class PersonalCenterUpdateFieldPermission(str, StructuredEnum):
    IS_EDITABLE = EnumField("is_editable", label=_("可直接修改"))
    NEED_VERIFY = EnumField("need_verify", label=_("验证后修改"))
    NOT_EDITABLE = EnumField("not_editable", label=_("不可修改"))

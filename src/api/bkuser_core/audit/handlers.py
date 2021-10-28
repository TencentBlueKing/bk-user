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
from typing import TYPE_CHECKING

from bkuser_core.audit.constants import OperationType
from bkuser_core.audit.utils import create_general_log, create_profile_log
from bkuser_core.categories.signals import post_category_create
from bkuser_core.departments.signals import post_department_create
from bkuser_core.profiles.signals import post_field_create, post_profile_create, post_profile_update
from bkuser_core.user_settings.signals import post_setting_create
from django.dispatch import receiver

if TYPE_CHECKING:
    from bkuser_core.profiles.models import Profile


@receiver(post_profile_update)
def create_reset_password_log(sender, instance: "Profile", operator: str, extra_values: dict, **kwargs):
    """Create an audit log for profile"""
    # 当密码信息存在时，我们需要增加一条记录，
    if "raw_password" in extra_values:
        create_profile_log(
            instance,
            "ResetPassword",
            {"is_success": True, "password": extra_values["raw_password"]},
            extra_values["request"],
        )


@receiver(post_profile_create)
@receiver(post_department_create)
@receiver(post_category_create)
@receiver(post_field_create)
@receiver(post_setting_create)
def create_audit_log(sender, instance: "Profile", operator: str, extra_values: dict, **kwargs):
    """Create an audit log for instance"""
    create_general_log(
        operator=operator,
        operate_type=OperationType.CREATE.value,
        operator_obj=instance,
        request=extra_values["request"],
    )

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
from bkuser_core.audit.utils import create_general_log, create_profile_log
from bkuser_core.profiles.signals import post_profile_create, post_profile_update
from django.dispatch import receiver


@receiver(post_profile_create)
@receiver(post_profile_update)
def create_audit_log(sender, profile, operator, operation_type, status, extra_values, **kwargs):
    """Create an audit log"""
    request = extra_values["request"]
    create_general_log(
        operator=operator,
        operate_type=operation_type,
        operator_obj=profile,
        request=request,
        status=status,
    )

    # 当密码信息存在时，我们需要增加一条记录，
    if "raw_password" in extra_values:
        create_profile_log(
            profile,
            "ResetPassword",
            {"is_success": True, "password": extra_values["raw_password"]},
            request,
        )

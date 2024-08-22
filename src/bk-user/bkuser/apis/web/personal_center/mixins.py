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

from django.conf import settings

from bkuser.apis.web.personal_center.constants import PhoneOrEmailUpdateRestrictionEnum


class CurrentTenantPhoneOrEmailUpdateRestrictionMixin:
    """获取当前租户更新手机号或邮箱的限制"""

    def get_phone_update_restriction(self, tenant_id):
        if tenant_id in settings.TENANT_PHONE_UPDATE_RESTRICTIONS:
            return settings.TENANT_PHONE_UPDATE_RESTRICTIONS[tenant_id]
        return PhoneOrEmailUpdateRestrictionEnum.NEED_VERIFY

    def get_email_update_restriction(self, tenant_id):
        if tenant_id in settings.TENANT_EMAIL_UPDATE_RESTRICTIONS:
            return settings.TENANT_EMAIL_UPDATE_RESTRICTIONS[tenant_id]
        return PhoneOrEmailUpdateRestrictionEnum.NEED_VERIFY

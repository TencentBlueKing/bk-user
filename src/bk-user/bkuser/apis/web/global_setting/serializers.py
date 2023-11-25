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
from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError as PDValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.global_setting.data_models import validate_global_setting_value_type
from bkuser.utils.pydantic import stringify_pydantic_error


class GlobalSettingRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="配置 ID")
    name = serializers.CharField(help_text="配置名称")
    value = serializers.JSONField(help_text="配置信息，可以是任何数据，比如字典、布尔、整数或字符串")


class GlobalSettingUpdateInputSLZ(serializers.Serializer):
    value = serializers.JSONField(help_text="配置信息，可以是任何数据，比如字典、布尔、整数或字符串")

    def validate_value(self, value):
        global_setting_id = self.context["global_setting_id"]

        try:
            return validate_global_setting_value_type(global_setting_id, value)
        except PDValidationError as e:
            raise ValidationError(_("配置信息值不合法，{}").format(stringify_pydantic_error(e)))
        except ValueError as e:
            raise ValidationError(str(e))

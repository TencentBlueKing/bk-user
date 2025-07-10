# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
import re
from typing import Dict

from django.template import Context
from django.template import Template as DjangoTemplate


def safe_substitute_django_template(template_content: str, context: Dict[str, str]) -> str:
    """安全替换 Django 格式的模板变量

    将 {{ variable }} 格式的变量替换为对应的值
    如果变量不存在，保持原样，避免模板注入风险
    """

    def replace_var(match):
        var_name = match.group(1).strip()
        return context.get(var_name, match.group(0))

    # 使用正则表达式匹配 {{ variable }} 格式
    pattern = r"\{\{\s*(\w+)\s*\}\}"
    return re.sub(pattern, replace_var, template_content)


class SafeTemplateRenderer:
    """安全的模板渲染器

    1. 内部场景（硬编码模板）：使用 Django Template 进行完整渲染
    2. 外部场景（用户输入）：使用安全替换，避免模板注入风险
    """

    @staticmethod
    def render_internal_template(template_content: str, context: Dict[str, str]) -> str:
        """渲染内部模板（硬编码模板）

        使用 Django Template 引擎，支持完整的模板语法
        """
        return DjangoTemplate(template_content).render(Context(context))

    @staticmethod
    def render_external_template(template_content: str, context: Dict[str, str]) -> str:
        """渲染外部模板（用户输入模板）

        使用安全替换，避免模板注入风险
        只支持简单的变量替换，不支持复杂的模板语法
        """
        return safe_substitute_django_template(template_content, context)

    @staticmethod
    def is_external_template(scene: str) -> bool:
        """判断是否为外部模板

        外部模板场景（来自管理员配置）：
        - 用户初始化 (USER_INITIALIZE) - 来自数据源插件配置
        - 重置密码 (RESET_PASSWORD) - 来自数据源插件配置
        - 密码即将过期 (PASSWORD_EXPIRING) - 来自数据源插件配置
        - 密码已过期 (PASSWORD_EXPIRED) - 来自数据源插件配置
        - 租户用户即将过期 (TENANT_USER_EXPIRING) - 来自租户配置
        - 租户用户已过期 (TENANT_USER_EXPIRED) - 来自租户配置

        内部模板场景（硬编码，安全）：
        - 管理员重置密码 (MANAGER_RESET_PASSWORD) - 硬编码模板
        - 发送验证码 (SEND_VERIFICATION_CODE) - 硬编码模板
        """
        external_scenes = [
            "user_initialize",
            "reset_password",
            "password_expiring",
            "password_expired",
            "tenant_user_expiring",
            "tenant_user_expired",
        ]
        return scene in external_scenes

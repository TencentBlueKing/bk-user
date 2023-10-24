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
from typing import Optional

from pydantic import BaseModel

from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.general.constants import AuthMethod, PageSize
from bkuser.plugins.general.models import AuthConfig, GeneralDataSourcePluginConfig, ServerConfig
from bkuser.plugins.local.constants import (
    NotificationMethod,
    NotificationScene,
    PasswordGenerateMethod,
)
from bkuser.plugins.local.models import (
    LocalDataSourcePluginConfig,
    NotificationConfig,
    NotificationTemplate,
    PasswordExpireConfig,
    PasswordInitialConfig,
    PasswordRuleConfig,
)


class DefaultPluginConfigProvider:
    """默认插件配置提供者"""

    def get(self, plugin_id: str) -> Optional[BaseModel]:
        """获取指定插件类型的默认插件配置"""
        # 本地数据源
        if plugin_id == DataSourcePluginEnum.LOCAL:
            return self._get_default_local_plugin_config()

        # 通用 HTTP 数据源
        if plugin_id == DataSourcePluginEnum.GENERAL:
            return self._get_default_general_plugin_config()

        return None

    def _get_default_local_plugin_config(self) -> BaseModel:
        return LocalDataSourcePluginConfig(
            enable_account_password_login=True,
            password_rule=PasswordRuleConfig(
                min_length=12,
                contain_lowercase=True,
                contain_uppercase=True,
                contain_digit=True,
                contain_punctuation=True,
                not_continuous_count=0,
                not_keyboard_order=False,
                not_continuous_letter=False,
                not_continuous_digit=False,
                not_repeated_symbol=False,
                valid_time=90,
                max_retries=3,
                lock_time=60 * 60,
            ),
            password_initial=PasswordInitialConfig(
                force_change_at_first_login=True,
                cannot_use_previous_password=True,
                reserved_previous_password_count=3,
                generate_method=PasswordGenerateMethod.RANDOM,
                fixed_password=None,
                notification=NotificationConfig(
                    enabled_methods=[NotificationMethod.EMAIL],
                    templates=[
                        NotificationTemplate(
                            method=NotificationMethod.EMAIL,
                            scene=NotificationScene.USER_INITIALIZE,
                            title="蓝鲸智云 - 您的账户已经成功创建！",
                            sender="蓝鲸智云",
                            content=(
                                "您好：\n"
                                + "您的蓝鲸智云帐户已经成功创建，以下是您的帐户信息\n"
                                + "登录帐户：{{ username }}，初始登录密码：{{ password }}\n"
                                + "为了保障帐户安全，建议您尽快登录平台修改密码：{{ url }}\n"
                                + "此邮件为系统自动发送，请勿回复。"
                            ),
                            content_html=(
                                "<p>您好：</p>"
                                + "<p>您的蓝鲸智云帐户已经成功创建，以下是您的帐户信息</p>"
                                + "<p>登录帐户：{{ username }}，初始登录密码：{{ password }}</p>"
                                + "<p>为了保障帐户安全，建议您尽快登录平台修改密码：{{ url }}</p>"
                                + "<p>此邮件为系统自动发送，请勿回复。</p>"
                            ),
                        ),
                        NotificationTemplate(
                            method=NotificationMethod.EMAIL,
                            scene=NotificationScene.RESET_PASSWORD,
                            title="蓝鲸智云 - 登录密码重置",
                            sender="蓝鲸智云",
                            content=(
                                "您好：\n"
                                + "我们收到了您重置密码的申请，请点击下方链接进行密码重置：{{ url }}\n"
                                + "该链接有效时间为 3 小时，过期后请重新点击密码重置链接：{{ reset_url }}\n"
                                + "此邮件为系统自动发送，请勿回复。"
                            ),
                            content_html=(
                                "<p>您好：</p>"
                                + "<p>我们收到了您重置密码的申请，请点击下方链接进行密码重置：{{ url }} </p>"
                                + "<p>该链接有效时间为 3 小时，过期后请重新点击密码重置链接：{{ reset_url }}</p>"
                                + "<p>此邮件为系统自动发送，请勿回复。</p>"
                            ),
                        ),
                        NotificationTemplate(
                            method=NotificationMethod.SMS,
                            scene=NotificationScene.USER_INITIALIZE,
                            title=None,
                            sender="蓝鲸智云",
                            content=(
                                "您好：\n"
                                + "您的蓝鲸智云帐户已经成功创建，以下是您的帐户信息\n"
                                + "登录帐户：{{ username }}，初始登录密码：{{ password }}\n"
                                + "为了保障帐户安全，建议您尽快登录平台修改密码：{{ url }}\n"
                                + "该短信为系统自动发送，请勿回复。"
                            ),
                            content_html=(
                                "<p>您好：</p>"
                                + "<p>您的蓝鲸智云帐户已经成功创建，以下是您的帐户信息</p>"
                                + "<p>登录帐户：{{ username }}，初始登录密码：{{ password }}</p>"
                                + "<p>为了保障帐户安全，建议您尽快登录平台修改密码：{{ url }}</p>"
                                + "<p>该短信为系统自动发送，请勿回复。</p>"
                            ),
                        ),
                        NotificationTemplate(
                            method=NotificationMethod.SMS,
                            scene=NotificationScene.RESET_PASSWORD,
                            title=None,
                            sender="蓝鲸智云",
                            content=(
                                "您好：\n"
                                + "我们收到了您重置密码的申请，请点击下方链接进行密码重置：{{ url }}\n"
                                + "该链接有效时间为 3 小时，过期后请重新点击密码重置链接：{{ reset_url }}\n"
                                + "该短信为系统自动发送，请勿回复。"
                            ),
                            content_html=(
                                "<p>您好：</p>"
                                + "<p>我们收到了您重置密码的申请，请点击下方链接进行密码重置：{{ url }} </p>"
                                + "<p>该链接有效时间为 3 小时，过期后请重新点击密码重置链接：{{ reset_url }}</p>"
                                + "<p>该短信为系统自动发送，请勿回复。</p>"
                            ),
                        ),
                    ],
                ),
            ),
            password_expire=PasswordExpireConfig(
                remind_before_expire=[1, 7, 15],
                notification=NotificationConfig(
                    enabled_methods=[NotificationMethod.EMAIL],
                    templates=[
                        NotificationTemplate(
                            method=NotificationMethod.EMAIL,
                            scene=NotificationScene.PASSWORD_EXPIRING,
                            title="蓝鲸智云 - 密码即将到期提醒",
                            sender="蓝鲸智云",
                            content=(
                                "{{ username }}，您好：\n"
                                + "您的蓝鲸智云平台密码将于 {{ expired_at }} 天后过期，为避免影响使用，请尽快登陆平台修改密码。\n"  # noqa: E501
                                + "此邮件为系统自动发送，请勿回复。"
                            ),
                            content_html=(
                                "<p>{{ username }}，您好：</p>"
                                + "<p>您的蓝鲸智云平台密码将于 {{ expired_at }} 天后过期，为避免影响使用，请尽快登陆平台修改密码。</p>"  # noqa: E501
                                + "<p>此邮件为系统自动发送，请勿回复。</p>"
                            ),
                        ),
                        NotificationTemplate(
                            method=NotificationMethod.EMAIL,
                            scene=NotificationScene.PASSWORD_EXPIRED,
                            title="蓝鲸智云 - 密码已过期提醒",
                            sender="蓝鲸智云",
                            content=(
                                "{{ username }}，您好：\n"
                                + "您的蓝鲸智云平台密码已过期，为避免影响正常使用，请尽快登陆平台修改密码。\n"  # noqa: E501
                                + "此邮件为系统自动发送，请勿回复。"
                            ),
                            content_html=(
                                "<p>{{ username }}，您好：</p>"
                                + "<p>您的蓝鲸智云平台密码已过期，为避免影响正常使用，请尽快登陆平台修改密码。</p>"
                                + "<p>此邮件为系统自动发送，请勿回复。</p>"
                            ),
                        ),
                        NotificationTemplate(
                            method=NotificationMethod.SMS,
                            scene=NotificationScene.PASSWORD_EXPIRING,
                            title=None,
                            sender="蓝鲸智云",
                            content=(
                                "{{ username }}，您好：\n"
                                + "您的蓝鲸智云平台密码将于 {{ expired_at }} 天后过期，为避免影响使用，请尽快登陆平台修改密码。\n"  # noqa: E501
                                + "该短信为系统自动发送，请勿回复。"
                            ),
                            content_html=(
                                "<p>{{ username }}，您好：</p>"
                                + "<p>您的蓝鲸智云平台密码将于 {{ expired_at }} 天后过期，为避免影响使用，请尽快登陆平台修改密码。</p>"  # noqa: E501
                                + "<p>该短信为系统自动发送，请勿回复。</p>"
                            ),
                        ),
                        NotificationTemplate(
                            method=NotificationMethod.SMS,
                            scene=NotificationScene.PASSWORD_EXPIRED,
                            title=None,
                            sender="蓝鲸智云",
                            content=(
                                "{{ username }}，您好：\n"
                                + "您的蓝鲸智云平台密码已过期，为避免影响使用，请尽快登陆平台修改密码。\n"  # noqa: E501
                                + "该短信为系统自动发送，请勿回复。"
                            ),
                            content_html=(
                                "<p>{{ username }}，您好：</p>"
                                + "<p>您的蓝鲸智云平台密码已过期，为避免影响使用，请尽快登陆平台修改密码。</p>"  # noqa: E501
                                + "<p>该短信为系统自动发送，请勿回复。</p>"
                            ),
                        ),
                    ],
                ),
            ),
        )

    def _get_default_general_plugin_config(self) -> BaseModel:
        return GeneralDataSourcePluginConfig(
            server_config=ServerConfig(
                server_base_url="https://bk.example.com",
                user_api_path="/api/v1/users",
                department_api_path="/api/v1/departments",
                page_size=PageSize.CNT_100,
                request_timeout=30,
                retries=3,
            ),
            auth_config=AuthConfig(
                method=AuthMethod.BASIC_AUTH,
            ),
        )

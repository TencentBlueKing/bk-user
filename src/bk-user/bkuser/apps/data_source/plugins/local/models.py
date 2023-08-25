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
from typing import List, Optional

from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, Field, ValidationError, model_validator

from bkuser.apps.data_source.plugins.local.constants import MAX_PASSWORD_LENGTH, PasswordGenerateMethod
from bkuser.common.passwd import PasswordRule, PasswordValidator
from bkuser.utils.std_error import stringify_pydantic_error


class PasswordRuleConfig(BaseModel):
    """密码规则配置"""

    # 密码最小长度
    min_length: int = Field(le=MAX_PASSWORD_LENGTH)

    # --- 字符限制类 ---
    # 必须包含小写字母
    contain_lowercase: bool
    # 必须包含大写字母
    contain_uppercase: bool
    # 必须包含数字
    contain_digit: bool
    # 必须包含特殊字符（标点符号）
    contain_punctuation: bool

    # --- 连续性限制类 ---
    # 不允许连续出现位数
    not_continuous_count: int = Field(ge=5, le=10)
    # 不允许键盘序
    not_keyboard_order: bool
    # 不允许连续字母序
    not_continuous_letter: bool
    # 不允许连续数字序
    not_continuous_digit: bool
    # 不允许重复字母，数字，特殊字符
    not_repeated_symbol: bool

    # 密码有效期（单位：秒），-1 表示永久
    valid_time: int = Field(ge=-1, le=10 * 365 * 24 * 60 * 60)
    # 密码试错次数
    max_try_times: int = Field(ge=0, le=10)
    # 锁定时间（单位：秒）
    lock_time: int = Field(ge=0, le=180 * 24 * 60 * 60)

    def to_rule(self) -> PasswordRule:
        """转换成密码工具可用的规则"""
        return PasswordRule(
            # 长度
            min_length=self.min_length,
            max_length=MAX_PASSWORD_LENGTH,
            # 字符集
            contain_lowercase=self.contain_lowercase,
            contain_uppercase=self.contain_uppercase,
            contain_digit=self.contain_digit,
            contain_punctuation=self.contain_punctuation,
            # 连续性
            not_continuous_count=self.not_continuous_count,
            not_keyboard_order=self.not_keyboard_order,
            not_continuous_letter=self.not_continuous_letter,
            not_continuous_digit=self.not_continuous_digit,
            not_repeated_symbol=self.not_repeated_symbol,
        )


class NotifyConfig(BaseModel):
    """通知相关配置"""

    # 以邮件方式通知
    notify_by_email: bool
    # 以短信方式通知
    notify_by_sms: bool
    # 通知模板
    notify_template: str


class PasswordInitialConfig(BaseModel):
    """初始密码设置"""

    # 首次登录后强制修改密码
    must_change_after_first_login: bool
    # 修改密码时候不能使用之前的密码
    cannot_use_previous_password: bool
    # 之前的 N 个密码不能被本次修改使用，仅当 cannot_use_previous_password 为 True 时有效
    reserved_previous_password_count: int = Field(gt=0, le=3)
    # 初始密码生成方式
    generate_method: PasswordGenerateMethod
    # 固定初始密码（仅密码生成方式为'固定值'时有效）
    fixed_password: Optional[str] = None
    # 通知相关配置
    notify: NotifyConfig


class PasswordExpireConfig(BaseModel):
    """密码到期相关配置"""

    # 在密码到期多久前提醒，单位：秒，多个值表示多次提醒
    remind_before_expire: List[int]
    # 通知相关配置
    notify: NotifyConfig


class LocalDataSourcePluginConfig(BaseModel):
    """本地数据源插件配置"""

    # 是否允许使用账密登录
    enable_login_by_password: bool
    # 密码生成规则
    password_rule: PasswordRuleConfig
    # 密码初始化/修改规则
    password_initial: PasswordInitialConfig
    # 密码到期规则
    password_expire: PasswordExpireConfig

    @model_validator(mode="after")
    def validate_attrs(self) -> "LocalDataSourcePluginConfig":
        """插件配置合法性检查"""
        try:
            rule = self.password_rule.to_rule()
        except ValidationError as e:
            raise ValueError(_("密码生成规则不合法: {}").format(stringify_pydantic_error(e)))

        if self.password_initial.generate_method == PasswordGenerateMethod.FIXED:
            # 如果初始密码生成模式为固定密码，则需要为固定密码预设值
            if not self.password_initial.fixed_password:
                raise ValueError(_("固定密码不能为空"))

            # 若配置固定密码，则需要检查是否符合定义的密码强度规则
            ret = PasswordValidator(rule).validate(self.password_initial.fixed_password)
            if not ret.ok:
                raise ValueError("固定密码的值不符合密码规则：{}".format(ret.exception_message))

        return self

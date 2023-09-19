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
import datetime

from django.utils import timezone

from bkuser.apps.data_source.models import DataSource, DataSourceUser, LocalDataSourceIdentityInfo
from bkuser.common.passwd import PasswordGenerator
from bkuser.plugins.local.constants import PasswordGenerateMethod
from bkuser.plugins.local.models import LocalDataSourcePluginConfig


class PasswordProvider:
    """本地数据源用户密码"""

    def __init__(self, plugin_cfg: LocalDataSourcePluginConfig):
        # assert for mypy type linter
        assert plugin_cfg.password_rule is not None
        assert plugin_cfg.password_initial is not None

        self.generate_method = plugin_cfg.password_initial.generate_method
        self.fixed_password = plugin_cfg.password_initial.fixed_password
        self.password_generator = PasswordGenerator(plugin_cfg.password_rule.to_rule())

    def generate(self) -> str:
        if self.generate_method == PasswordGenerateMethod.FIXED and self.fixed_password:
            return self.fixed_password

        return self.password_generator.generate()


class LocalDataSourceIdentityInfoInitializer:
    """本地数据源用户身份数据初始化"""

    BATCH_SIZE = 250

    def __init__(self, data_source: DataSource):
        self.data_source = data_source
        self.plugin_cfg = LocalDataSourcePluginConfig(**data_source.plugin_config)
        self.password_provider = PasswordProvider(self.plugin_cfg)

    def initialize(self) -> None:
        if self._can_skip_initialize():
            return

        self._init_users_identity_info()

    def _can_skip_initialize(self):
        """预先判断能否直接跳过"""

        # 不是本地数据源的，不需要初始化
        if not self.data_source.is_local:
            return True

        # 是本地数据源，但是没开启账密登录的，不需要初始化
        if not self.plugin_cfg.enable_account_password_login:
            return True

        return False

    def _init_users_identity_info(self):
        exists_infos = LocalDataSourceIdentityInfo.objects.filter(data_source=self.data_source)
        exists_info_user_ids = exists_infos.objects.values_list("user_id", flat=True)
        # NOTE：已经存在的账密信息，不会按照最新规则重新生成！
        waiting_init_users = DataSourceUser.objects.filter(
            data_source=self.data_source,
        ).exclude(id__in=exists_info_user_ids)

        time_now = timezone.now()
        expired_at = self._get_password_expired_at(time_now)

        waiting_create_infos = [
            LocalDataSourceIdentityInfo(
                user=user,
                password=self.password_provider.generate(),
                password_updated_at=time_now,
                password_expired_at=expired_at,
                data_source=self.data_source,
                username=user.username,
                created_at=time_now,
                updated_at=time_now,
            )
            for user in waiting_init_users
        ]
        LocalDataSourceIdentityInfo.objects.bulk_create(waiting_create_infos, batch_size=self.BATCH_SIZE)

    def _get_password_expired_at(self, now: datetime.datetime) -> datetime.datetime:
        return now + datetime.timedelta(days=self.plugin_cfg.password_rule.valid_time)  # type: ignore

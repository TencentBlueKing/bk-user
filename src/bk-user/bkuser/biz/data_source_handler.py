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
import hashlib
import logging

from bkuser.apps.data_source.constants import DataSourcePluginType
from bkuser.apps.data_source.models import DataSource, DataSourcePlugin, DataSourceUser
from bkuser.biz.utils import gen_random_str
from django.contrib.auth.hashers import make_password
from django.utils.encoding import force_bytes

logger = logging.getLogger(__name__)


class DataSourceHandler:

    def _make_password_by_config(self, pass_config: dict, return_raw=False) -> str:
        if pass_config["init_password_method"] == "fixed_preset":
            raw_password = pass_config["init_password"]
        else:
            raw_password = gen_random_str(12)
        if return_raw:
            return raw_password

        return make_password(raw_password)

    def _get_code(self, name: str, owner: str) -> str:
        """通过名称+租户ID 生成 唯一code"""
        tmp_str = f"{name}-{owner}"
        sha = hashlib.sha256(force_bytes(tmp_str)).hexdigest()
        logger.debug("use data_source_name and owner to be code: %s -> %s", tmp_str, sha)
        return sha

    def create_data_source(
            self, name: str,
            owner: str,
            data_source_type=DataSourcePluginType.LOCAL.value
    ) -> DataSource:
        local_data_source_plugin = DataSourcePlugin.objects.get(type=data_source_type)
        code = self._get_code(name, owner)
        logger.info(f"create data_source for tenant-<{owner}>. data_source_type:{data_source_type}")
        data_source = DataSource.objects.create(
            name=name,
            code=code,
            owner=owner,
            plugin_id=local_data_source_plugin.id,
            plugin_config=local_data_source_plugin.config_meta,
        )
        return data_source

    def create_data_source_users(self, instance: DataSource, users: list[dict]) -> list[str]:
        data_source_users = []
        password_config = instance.plugin_config["password"]
        for user in users:
            user["password"] = self._make_password_by_config(password_config)
            logger.info(f"create user<{user['username']}> for data_source<{instance.id}-{instance.name}>")
            data_source_users.append(DataSourceUser(data_source_id=instance.id, **user))
        DataSourceUser.objects.bulk_create(data_source_users)
        return [user["username"] for user in users]

    def update_plugin_config(self, instance: DataSource, update_settings: dict, namespace: str) -> DataSource:
        plugin_config = instance.plugin_config
        config = plugin_config.get(namespace, {})

        if not config:
            logger.error(f"plugin config has no this config. namespace:{namespace}")

        for key, value in update_settings.items():
            config[key] = value
        plugin_config[namespace] = config
        instance.save()
        return instance

    def filter_users(self, data_source_id: int, **kwargs) -> DataSourceUser:
        logger.info(f"filter user from data_source<{data_source_id}>. filter condition:{kwargs}")
        return DataSourceUser.objects.filter(data_source_id=data_source_id, **kwargs)


data_source_handler = DataSourceHandler()

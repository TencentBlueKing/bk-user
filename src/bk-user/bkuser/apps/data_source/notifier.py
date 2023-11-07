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
import logging
from typing import Dict, List, Optional

from django.conf import settings
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _

from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.component import cmsi
from bkuser.plugins.local.constants import NotificationMethod, NotificationScene
from bkuser.plugins.local.models import LocalDataSourcePluginConfig, NotificationTemplate

logger = logging.getLogger(__name__)


class NotificationTmplContextGenerator:
    """生成通知模板使用的上下文"""

    def __init__(self, user: DataSourceUser, scene: NotificationScene, **scene_kwargs):
        self.user = user
        self.scene = scene
        self.scene_kwargs = scene_kwargs

    def gen(self) -> Dict[str, str]:
        """生成通知模板使用的上下文

        注：为保证模板渲染准确性，value 值类型需为 str
        """
        if self.scene == NotificationScene.USER_INITIALIZE:
            return self._gen_user_initialize_ctx()
        if self.scene == NotificationScene.RESET_PASSWORD:
            return self._gen_reset_passwd_ctx()
        if self.scene == NotificationScene.PASSWORD_EXPIRING:
            return self._gen_passwd_expiring_ctx()
        if self.scene == NotificationScene.PASSWORD_EXPIRED:
            return self._gen_passwd_expired_ctx()

        return self._gen_base_ctx()

    def _gen_base_ctx(self) -> Dict[str, str]:
        """获取基础信息"""
        return {
            "username": self.user.username,
            "full_name": self.user.full_name,
        }

    def _gen_user_initialize_ctx(self) -> Dict[str, str]:
        """用户初始化"""
        # FIXME (su) 提供修改密码的 URL（settings.BK_USER_URL + xxxx）
        return {
            "password": self.scene_kwargs["passwd"],
            "reset_url": settings.BK_USER_URL + "/reset-password",
            **self._gen_base_ctx(),
        }

    def _gen_reset_passwd_ctx(self) -> Dict[str, str]:
        """重置密码"""
        return self._gen_base_ctx()

    def _gen_passwd_expiring_ctx(self) -> Dict[str, str]:
        """密码即将过期"""
        return self._gen_base_ctx()

    def _gen_passwd_expired_ctx(self) -> Dict[str, str]:
        """密码过期"""
        return self._gen_base_ctx()


class LocalDataSourceUserNotifier:
    """本地数据源用户通知器，支持批量像用户发送某类信息"""

    templates: List[NotificationTemplate] = []

    def __init__(self, data_source: DataSource, scene: NotificationScene):
        self.data_source = data_source
        self.scene = scene

        if not data_source.is_local:
            return

        plugin_cfg = data_source.get_plugin_cfg()
        assert isinstance(plugin_cfg, LocalDataSourcePluginConfig)

        if not plugin_cfg.enable_account_password_login:
            return

        self.templates = self._get_tmpls_with_scene(plugin_cfg, scene)

    def send(self, users: List[DataSourceUser], user_passwd_map: Optional[Dict[int, str]] = None) -> None:
        """根据数据源插件配置，发送对应的通知信息"""
        user_passwd_map = user_passwd_map or {}

        # 预先检查，避免出现发送部分通知后，出现异常中断的情况
        if self.scene == NotificationScene.USER_INITIALIZE:  # noqa: SIM102
            if not_passwd_users := {u.id for u in users} - set(user_passwd_map.keys()):
                raise ValueError(f"users {not_passwd_users} not found in user passwd map")

        try:
            for u in users:
                scene_kwargs = {}
                if self.scene == NotificationScene.USER_INITIALIZE:
                    scene_kwargs["passwd"] = user_passwd_map[u.id]

                self._send_notifications(u, **scene_kwargs)
        # TODO (su) 细化异常处理
        except Exception:
            logger.exception("send notification failed")

    def _get_tmpls_with_scene(
        self, plugin_cfg: LocalDataSourcePluginConfig, scene: NotificationScene
    ) -> List[NotificationTemplate]:
        """根据场景以及插件配置中设置的通知方式，获取需要发送通知的模板"""
        if scene in (
            NotificationScene.USER_INITIALIZE,
            NotificationScene.RESET_PASSWORD,
        ):
            cfg = plugin_cfg.password_initial.notification  # type: ignore
        elif scene in (
            NotificationScene.PASSWORD_EXPIRING,
            NotificationScene.PASSWORD_EXPIRED,
        ):
            cfg = plugin_cfg.password_expire.notification  # type: ignore
        else:
            raise ValueError(_("通知场景 {} 未被支持".format(scene)))

        # 返回场景匹配，且被声明启用的模板列表
        return [tmpl for tmpl in cfg.templates if tmpl.scene == scene and tmpl.method in cfg.enabled_methods]

    def _send_notifications(self, user: DataSourceUser, **scene_kwargs):
        """根据配置的通知模板，逐个用户发送通知"""
        for tmpl in self.templates:
            if tmpl.method == NotificationMethod.EMAIL:
                self._send_email(user, tmpl, **scene_kwargs)
            elif tmpl.method == NotificationMethod.SMS:
                self._send_sms(user, tmpl, **scene_kwargs)

    def _send_email(self, user: DataSourceUser, tmpl: NotificationTemplate, **scene_kwargs):
        logger.info("send email to user %s, scene %s, title: %s", user.username, tmpl.scene, tmpl.title)
        content = self._render_tmpl(user, tmpl.content_html, **scene_kwargs)
        # FIXME (su) 修改为指定用户名
        cmsi.send_mail([user.email], tmpl.sender, tmpl.title, content)  # type: ignore

    def _send_sms(self, user: DataSourceUser, tmpl: NotificationTemplate, **scene_kwargs):
        logger.info("send sms to user %s, scene %s", user.username, tmpl.scene)
        content = self._render_tmpl(user, tmpl.content, **scene_kwargs)
        # FIXME (su) 修改为指定用户名
        cmsi.send_sms([user.phone], content)

    def _render_tmpl(self, user: DataSourceUser, content: str, **scene_kwargs) -> str:
        ctx = NotificationTmplContextGenerator(user=user, scene=self.scene, **scene_kwargs).gen()
        return Template(content).render(Context(ctx))

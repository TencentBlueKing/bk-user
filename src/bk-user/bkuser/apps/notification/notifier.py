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
from typing import Dict, List

from django.template import Context, Template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bkuser import settings
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.notification.constants import NotificationMethod, NotificationScene
from bkuser.apps.notification.data_models import NotificationTemplate
from bkuser.apps.tenant.models import TenantUser, TenantUserValidityPeriodConfig
from bkuser.component import cmsi
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

logger = logging.getLogger(__name__)


class NotificationTmplsGetter:
    """根据指定的不同场景获取通知模板"""

    def get(self, scene: NotificationScene, **kwargs) -> List[NotificationTemplate]:
        """获取指定的通知模板"""
        # 租户管理员重置密码使用的是固定模板
        if scene == NotificationScene.MANAGER_RESET_PASSWORD:
            return self._get_manager_reset_user_password_tmpls()

        # 从租户有效期配置中获取通知模板
        if scene in [
            NotificationScene.TENANT_USER_EXPIRING,
            NotificationScene.TENANT_USER_EXPIRED,
        ]:
            return self._get_from_validity_period_config(scene, **kwargs)

        # 从数据源插件配置中获取通知模板
        if scene in (
            NotificationScene.USER_INITIALIZE,
            NotificationScene.RESET_PASSWORD,
            NotificationScene.PASSWORD_EXPIRING,
            NotificationScene.PASSWORD_EXPIRED,
        ):
            return self._get_from_data_source_plugin_config(scene, **kwargs)

        raise ValueError(_("通知场景 {} 未被支持".format(scene)))

    def _get_manager_reset_user_password_tmpls(self) -> List[NotificationTemplate]:
        """获取租户管理员重置本地数据源用户密码通知模板"""
        return [
            NotificationTemplate(
                method=NotificationMethod.EMAIL,
                title="蓝鲸智云 - 您的密码已被重置",
                sender="蓝鲸智云",
                content=(
                    "<p>您好：</p>"
                    + "<p>您的蓝鲸智云帐户密码已被重置，以下是您的帐户信息\n</p>"
                    + "<p>登录帐户：{{ username }}，登录密码：{{ password }}\n</p>"
                    + "<p>此邮件为系统自动发送，请勿回复。</p>"
                ),
            )
        ]

    def _get_from_validity_period_config(self, scene: NotificationScene, **kwargs) -> List[NotificationTemplate]:
        assert "tenant_id" in kwargs

        cfg = TenantUserValidityPeriodConfig.objects.get(tenant_id=kwargs["tenant_id"])
        # 返回场景匹配，且被声明启用的模板列表
        return [
            NotificationTemplate(
                method=NotificationMethod(tmpl["method"]),
                sender=tmpl["sender"],
                title=tmpl["title"],
                content=tmpl["content"] if tmpl["method"] == NotificationMethod.SMS else tmpl["content_html"],
            )
            for tmpl in cfg.notification_templates
            if tmpl["scene"] == scene and tmpl["method"] in cfg.enabled_notification_methods
        ]

    def _get_from_data_source_plugin_config(self, scene: NotificationScene, **kwargs) -> List[NotificationTemplate]:
        # 从数据源插件配置中获取通知模板
        assert "data_source_id" in kwargs
        data_source = DataSource.objects.get(id=kwargs["data_source_id"])

        plugin_cfg = data_source.get_plugin_cfg()
        assert isinstance(plugin_cfg, LocalDataSourcePluginConfig)

        if scene in (
            NotificationScene.USER_INITIALIZE,
            NotificationScene.RESET_PASSWORD,
        ):
            cfg = plugin_cfg.password_initial.notification  # type: ignore
        else:
            cfg = plugin_cfg.password_expire.notification  # type: ignore

        return [
            NotificationTemplate(
                method=NotificationMethod(tmpl.method),
                sender=tmpl.sender,
                title=tmpl.title,
                content=tmpl.content if tmpl.method == NotificationMethod.SMS else tmpl.content_html,
            )
            for tmpl in cfg.templates
            if tmpl.scene == scene and tmpl.method in cfg.enabled_methods
        ]


class TmplContextGenerator:
    def __init__(self, user: TenantUser, scene: NotificationScene, **scene_kwargs):
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
        if self.scene == NotificationScene.MANAGER_RESET_PASSWORD:
            return self._gen_manager_reset_passwd_ctx()
        if self.scene == NotificationScene.TENANT_USER_EXPIRING:
            return self._gen_tenant_user_expiring_ctx()
        if self.scene == NotificationScene.TENANT_USER_EXPIRED:
            return self._gen_tenant_user_expired_ctx()

        return self._gen_base_ctx()

    def _gen_base_ctx(self) -> Dict[str, str]:
        """获取基础信息"""
        return {
            "username": self.user.data_source_user.username,
            "full_name": self.user.data_source_user.full_name,
        }

    def _gen_user_initialize_ctx(self) -> Dict[str, str]:
        """用户初始化"""
        # FIXME (su) 提供修改密码的 URL（settings.BK_USER_URL + xxxx）
        return {
            "password": self.scene_kwargs["passwd"],
            "url": settings.BK_USER_URL + "/reset-password",
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

    def _gen_manager_reset_passwd_ctx(self) -> Dict[str, str]:
        """管理员重置密码"""
        return {
            "password": self.scene_kwargs["passwd"],
            **self._gen_base_ctx(),
        }

    def _gen_tenant_user_expiring_ctx(self) -> Dict[str, str]:
        """租户用户即将过期"""
        valid_time = self.user.account_expired_at - timezone.now()
        return {
            "valid_days": str(valid_time.days + 1),
            **self._gen_base_ctx(),
        }

    def _gen_tenant_user_expired_ctx(self) -> Dict[str, str]:
        """租户用户已过期"""
        return self._gen_base_ctx()


class TenantUserNotifier:
    """租户用户通知器，用于向一批或某个租户用户发送通知"""

    def __init__(self, scene: NotificationScene, **kwargs):
        """
        :param scene: 通知场景
        :param data_source_id: 数据源 ID，当通知模板来源于数据源插件时必须
        :param tenant_id: 租户 ID，当通知模板来源于租户相关配置时必须
        """
        self.scene = scene
        self.templates = NotificationTmplsGetter().get(scene, **kwargs)

    def batch_send(self, users: List[TenantUser], **kwargs) -> None:
        """
        批量发送通知

        :param users: 租户用户列表
        :param user_passwd_map: {数据源用户ID: 密码} 映射表，密码初始化/重置场景必须
        """
        for u in users:
            try:
                self.send(u, **self._gen_scene_kwargs(u, **kwargs))
            except Exception:  # noqa: PERF203
                logger.exception("send notification to user %s, scene %s failed", u.id, self.scene)

    def send(self, user: TenantUser, **scene_kwargs) -> None:
        for tmpl in self.templates:
            content = self._render_tmpl(user, tmpl.content, **scene_kwargs)
            if tmpl.method == NotificationMethod.EMAIL:
                cmsi.send_mail(user.id, tmpl.sender, tmpl.title, content)  # type: ignore

            elif tmpl.method == NotificationMethod.SMS:
                cmsi.send_sms(user.id, content)

            logger.info("send %s to user %s, scene %s", tmpl.method.value, user.id, self.scene)

    def _gen_scene_kwargs(self, user, **kwargs) -> Dict[str, str]:
        if self.scene in [
            NotificationScene.USER_INITIALIZE,
            NotificationScene.MANAGER_RESET_PASSWORD,
        ]:
            if "user_passwd_map" not in kwargs:
                raise ValueError("user_passwd_map required when call batch_send")

            return {"passwd": kwargs["user_passwd_map"][user.data_source_user.id]}

        return {}

    def _render_tmpl(self, user: TenantUser, tmpl_content: str, **scene_kwargs) -> str:
        ctx = TmplContextGenerator(user=user, scene=self.scene, **scene_kwargs).gen()
        return Template(tmpl_content).render(Context(ctx))

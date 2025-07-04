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
import logging
from typing import Dict, List

from django.conf import settings
from django.template import Context, Template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bkuser.apps.data_source.models import DataSource, LocalDataSourceIdentityInfo
from bkuser.apps.notification.constants import NotificationMethod, NotificationScene
from bkuser.apps.notification.data_models import NotificationTemplate
from bkuser.apps.notification.helpers import gen_reset_password_url
from bkuser.apps.tenant.models import TenantUser, TenantUserValidityPeriodConfig
from bkuser.component.cmsi import get_notification_client
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

logger = logging.getLogger(__name__)


class NotificationTmplsGetter:
    """根据指定的不同场景获取通知模板"""

    def get(self, scene: NotificationScene, **scene_kwargs) -> List[NotificationTemplate]:
        """获取指定的通知模板"""
        # 租户管理员重置密码使用的是固定模板
        if scene == NotificationScene.MANAGER_RESET_PASSWORD:
            return self._get_manager_reset_user_password_tmpls()

        # 用户获取用户管理平台验证码
        if scene == NotificationScene.SEND_VERIFICATION_CODE:
            return self._get_send_verification_code_tmpls(**scene_kwargs)

        # 从租户有效期配置中获取通知模板
        if scene in [
            NotificationScene.TENANT_USER_EXPIRING,
            NotificationScene.TENANT_USER_EXPIRED,
        ]:
            return self._get_from_validity_period_config(scene, **scene_kwargs)

        # 从数据源插件配置中获取通知模板
        if scene in (
            NotificationScene.USER_INITIALIZE,
            NotificationScene.RESET_PASSWORD,
            NotificationScene.PASSWORD_EXPIRING,
            NotificationScene.PASSWORD_EXPIRED,
        ):
            return self._get_from_data_source_plugin_cfg(scene, **scene_kwargs)

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
                    + "<p>您的蓝鲸智云帐户密码已被重置，以下是您的帐户信息</p>"
                    + "<p>登录帐户：{{ username }}，登录密码：{{ password }}</p>"
                    + "<p>此邮件为系统自动发送，请勿回复。</p>"
                ),
            )
        ]

    def _get_send_verification_code_tmpls(self, **scene_kwargs) -> List[NotificationTemplate]:
        """获取用户获取用户管理平台验证码的通知模板"""
        assert "method" in scene_kwargs
        method = NotificationMethod(scene_kwargs["method"])

        if method == NotificationMethod.EMAIL:
            return [
                NotificationTemplate(
                    method=NotificationMethod.EMAIL,
                    title="蓝鲸智云 - 验证码",
                    sender="蓝鲸智云",
                    content=(
                        "<p>您好：</p>"
                        + "<p>您的蓝鲸智云验证码为: {{ verification_code }}</p>"
                        + "<p>该验证码 {{ valid_minutes }} 分钟内有效，为了您的账户安全，请勿向他人泄露该验证码</p>"
                        + "<p>此邮件为系统自动发送，请勿回复。</p>"
                    ),
                )
            ]

        if method == NotificationMethod.SMS:
            return [
                NotificationTemplate(
                    method=NotificationMethod.SMS,
                    title=None,
                    sender="蓝鲸智云",
                    content=(
                        "您好：\n"
                        + "您的蓝鲸智云验证码为: {{ verification_code }}\n"
                        + "该验证码 {{ valid_minutes }} 分钟内有效，为了您的账户安全，请勿向他人泄露该验证码\n"
                        + "此短信为系统自动发送，请勿回复。"
                    ),
                )
            ]

        raise NotImplementedError(f"unsupported method: {method}")

    def _get_from_validity_period_config(self, scene: NotificationScene, **scene_kwargs) -> List[NotificationTemplate]:
        """从租户有效期配置中获取通知模板"""
        assert "tenant_id" in scene_kwargs
        cfg = TenantUserValidityPeriodConfig.objects.get(tenant_id=scene_kwargs["tenant_id"])

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

    def _get_from_data_source_plugin_cfg(self, scene: NotificationScene, **scene_kwargs) -> List[NotificationTemplate]:
        """从数据源插件配置中获取通知模板"""
        assert "data_source_id" in scene_kwargs
        data_source = DataSource.objects.get(id=scene_kwargs["data_source_id"])

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


class ContactTmplContextGenerator:
    """联系方式通知的模板上下文生成器"""

    def __init__(self, scene: NotificationScene, **scene_kwargs):
        self.scene = scene
        self.scene_kwargs = scene_kwargs

    def gen(self) -> Dict[str, str]:
        """生成通知模板使用的上下文"""
        if self.scene == NotificationScene.SEND_VERIFICATION_CODE:
            return self._gen_send_verification_code_ctx()
        if self.scene == NotificationScene.RESET_PASSWORD:
            return self._gen_reset_passwd_ctx()
        raise ValueError(f"Scene {self.scene} not supported for contact notification")

    def _gen_send_verification_code_ctx(self) -> Dict[str, str]:
        """发送验证码"""
        return {
            "verification_code": self.scene_kwargs["verification_code"],
            # 将验证码有效期换算为分钟，更符合一般表示法
            "valid_minutes": str(int(settings.VERIFICATION_CODE_VALID_TIME / 60)),
        }

    def _gen_reset_passwd_ctx(self) -> Dict[str, str]:
        """用户重置密码"""
        return {
            "url": gen_reset_password_url(self.scene_kwargs["token"]),
            # 将验证码有效期换算为分钟，更符合一般表示法
            "valid_minutes": str(int(settings.RESET_PASSWORD_TOKEN_VALID_TIME / 60)),
        }


class UserTmplContextGenerator:
    """依赖用户信息的模板上下文生成器"""

    def __init__(self, user: TenantUser, scene: NotificationScene, **scene_kwargs):
        self.user = user
        self.scene = scene
        self.scene_kwargs = scene_kwargs

    def gen(self) -> Dict[str, str]:
        """生成通知模板使用的上下文"""
        if self.scene == NotificationScene.USER_INITIALIZE:
            return self._gen_user_initialize_ctx()
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
        raise ValueError(f"Scene {self.scene} not supported for user notification")

    def _gen_base_ctx(self) -> Dict[str, str]:
        """获取基础信息"""
        return {
            "username": self.user.data_source_user.username,
            "full_name": self.user.data_source_user.full_name,
        }

    def _gen_user_initialize_ctx(self) -> Dict[str, str]:
        """用户初始化"""
        return {
            "password": self.scene_kwargs["passwd"],
            "url": settings.BK_USER_URL.rstrip("/") + "/personal-center",
            **self._gen_base_ctx(),
        }

    def _gen_passwd_expiring_ctx(self) -> Dict[str, str]:
        """密码即将过期"""
        identify_info = LocalDataSourceIdentityInfo.objects.get(user_id=self.user.data_source_user_id)
        valid_time = identify_info.password_expired_at - timezone.now()
        return {
            "valid_days": str(valid_time.days + 1),
            **self._gen_base_ctx(),
        }

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


class NotificationSender:
    """消息通知发送器"""

    def __init__(self, tenant_id: str):
        """
        初始化发送器
        :param tenant_id: 租户 ID
        """
        self.tenant_id = tenant_id
        self.client = get_notification_client(tenant_id)

    def send(
        self,
        method: str,
        title: str | None,
        content: str,
        sender: str,
        email: str = "",
        phone: str = "",
        phone_country_code: str = "",
        tenant_user_id: str = "",
    ):
        """
        单条消息发送
        支持通过 联系方式 或 租户用户 ID 发送通知，当两者都存在时，优先使用联系方式
        :param method: 发送方式（邮件/短信）
        :param title: 标题（邮件必填参数）
        :param content: 内容
        :param sender: 发送者
        :param email: 邮箱地址
        :param phone: 手机号
        :param phone_country_code: 手机国际区号
        :param tenant_user_id: 租户用户 ID，与联系方式二选一
        """
        if method == NotificationMethod.EMAIL:
            self.client.send_mail(
                sender=sender,
                title=title,  # type: ignore
                content=content,
                email=email,
                receiver=tenant_user_id,
            )
        elif method == NotificationMethod.SMS:
            self.client.send_sms(
                content=content,
                phone=phone,
                phone_country_code=phone_country_code,
                receiver=tenant_user_id,
            )
        else:
            raise ValueError(f"Unsupported notification method: {method}")


class ContactNotifier:
    """联系方式通知器，用于向指定联系方式发送通知（如验证码）"""

    def __init__(self, scene: NotificationScene, tenant_id: str, **scene_kwargs):
        """
        :param scene: 通知场景
        :param tenant_id: 租户 ID
        :param scene_kwargs: 场景相关参数
        """
        self.scene = scene
        self.tenant_id = tenant_id
        self.templates = NotificationTmplsGetter().get(scene, **scene_kwargs)
        self.sender = NotificationSender(tenant_id)

    def send(self, email: str = "", phone: str = "", phone_country_code: str = "", **scene_kwargs) -> None:
        """
        通过联系方式发送通知，适用于不需要用户信息的场景（如发送验证码）
        :param email: 邮箱地址
        :param phone: 手机号
        :param phone_country_code: 手机国际区号
        :param scene_kwargs: 场景相关参数
        """
        context_generator = ContactTmplContextGenerator(self.scene, **scene_kwargs)

        for tmpl in self.templates:
            content = self._render_tmpl(tmpl.content, context_generator)
            self.sender.send(
                method=tmpl.method,
                title=tmpl.title,
                content=content,
                sender=tmpl.sender,
                email=email,
                phone=phone,
                phone_country_code=phone_country_code,
            )
            logger.info("send %s by contact info, scene %s", tmpl.method.value, self.scene)

    def _render_tmpl(self, tmpl_content: str, context_generator: ContactTmplContextGenerator) -> str:
        """渲染模板"""
        ctx = context_generator.gen()
        return Template(tmpl_content).render(Context(ctx))


class TenantUserNotifier:
    """租户用户通知器，用于向租户用户发送通知"""

    def __init__(self, scene: NotificationScene, tenant_id: str, **scene_kwargs):
        """
        :param scene: 通知场景
        :param tenant_id: 租户 ID
        :param scene_kwargs: 场景相关参数
        """
        self.scene = scene
        self.tenant_id = tenant_id

        # 需要传递 tenant_id 作为场景相关参数
        if scene in [NotificationScene.TENANT_USER_EXPIRING, NotificationScene.TENANT_USER_EXPIRED]:
            scene_kwargs["tenant_id"] = tenant_id

        self.templates = NotificationTmplsGetter().get(scene, **scene_kwargs)
        self.sender = NotificationSender(tenant_id)

    def batch_send(self, users: List[TenantUser], **kwargs) -> None:
        """
        批量发送通知到用户
        :param users: 租户用户列表
        :param kwargs: 场景相关参数，如 user_passwd_map: {数据源用户ID: 密码} 映射表
        """
        for user in users:
            try:
                scene_kwargs = self._gen_scene_kwargs(user, **kwargs)
                self.send(user, **scene_kwargs)
            except Exception:  # noqa: PERF203
                logger.exception("send notification to user %s, scene %s failed", user.id, self.scene)

    def send(self, user: TenantUser, **scene_kwargs) -> None:
        """
        发送通知到用户，适用于需要用户信息的场景（如密码过期提醒）
        :param user: 租户用户对象
        :param scene_kwargs: 场景相关参数
        """
        context_generator = UserTmplContextGenerator(user, self.scene, **scene_kwargs)

        for tmpl in self.templates:
            content = self._render_tmpl(tmpl.content, context_generator)
            self.sender.send(
                method=tmpl.method,
                title=tmpl.title,
                content=content,
                sender=tmpl.sender,
                tenant_user_id=user.id,
            )
            logger.info("send %s to user %s, scene %s", tmpl.method.value, user.id, self.scene)

    def _gen_scene_kwargs(self, user: TenantUser, **kwargs) -> Dict[str, str]:
        """生成特定场景所需的参数"""
        if self.scene in [
            NotificationScene.USER_INITIALIZE,
            NotificationScene.MANAGER_RESET_PASSWORD,
        ]:
            if "user_passwd_map" not in kwargs:
                raise ValueError("user_passwd_map required when call batch_send")
            return {"passwd": kwargs["user_passwd_map"][user.data_source_user.id]}
        return {}

    def _render_tmpl(self, tmpl_content: str, context_generator: UserTmplContextGenerator) -> str:
        """渲染模板"""
        ctx = context_generator.gen()
        return Template(tmpl_content).render(Context(ctx))

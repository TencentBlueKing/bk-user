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


class BaseTmplContextGenerator:
    """模板上下文生成器基类"""

    def __init__(self, scene: NotificationScene, **scene_kwargs):
        self.scene = scene
        self.scene_kwargs = scene_kwargs

    def gen(self) -> Dict[str, str]:
        """生成通知模板使用的上下文

        注：为保证模板渲染准确性，value 值类型需为 str
        """
        if self.scene == NotificationScene.SEND_VERIFICATION_CODE:
            return self._gen_send_verification_code_ctx()
        if self.scene == NotificationScene.RESET_PASSWORD:
            return self._gen_reset_passwd_ctx()
        raise ValueError(f"Scene {self.scene} not supported")

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


class UserTmplContextGenerator(BaseTmplContextGenerator):
    """依赖用户信息的模板上下文生成器"""

    def __init__(self, user: TenantUser, scene: NotificationScene, **scene_kwargs):
        super().__init__(scene, **scene_kwargs)
        self.user = user

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
        # 对于不支持的场景，尝试使用基类的处理方法
        return super().gen()

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


class TmplContextGenerator(BaseTmplContextGenerator):
    """模版上下文生成器工厂类，根据是否提供用户对象，返回相应的生成器实例"""

    @classmethod
    def create(cls, scene: NotificationScene, user: TenantUser | None = None, **scene_kwargs):
        if user is not None:
            return UserTmplContextGenerator(user, scene, **scene_kwargs)
        return cls(scene, **scene_kwargs)


class NotificationSender:
    """消息通知发送器"""

    def __init__(self):
        self.client = get_notification_client()

    def send(
        self,
        method: str,
        title: str | None,
        content: str,
        sender: str,
        tenant_id: str,
        contact_info: Dict[str, str | Dict[str, str]] | None = None,
        tenant_user_id: str = "",
    ):
        """
        单条消息发送
        支持通过 联系方式 或 租户用户 ID 发送通知，当两者都存在时，优先使用联系方式
        :param method: 发送方式（邮件/短信）
        :param title: 标题（邮件必填参数）
        :param content: 内容
        :param sender: 发送者
        :param contact_info: 联系方式
        :param tenant_user_id: 租户用户 ID，与 contact_info 二选一
        """
        if method == NotificationMethod.EMAIL:
            self.client.send_mail(
                tenant_id=tenant_id,
                sender=sender,
                title=title,  # type: ignore
                content=content,
                email=contact_info.get("email") if contact_info else None,  # type: ignore
                receiver=tenant_user_id,
            )
        elif method == NotificationMethod.SMS:
            self.client.send_sms(
                tenant_id=tenant_id,
                content=content,
                phone_info=contact_info.get("phone_info") if contact_info else None,  # type: ignore
                receiver=tenant_user_id,
            )
        else:
            raise ValueError(f"Unsupported notification method: {method}")


class TenantUserNotifier:
    """租户用户通知器，用于向一批或某个租户用户发送通知"""

    def __init__(self, scene: NotificationScene, **scene_kwargs):
        """
        :param scene: 通知场景
        :param data_source_id: 数据源 ID，当通知模板来源于数据源插件时必须
        :param tenant_id: 租户 ID，当通知模板来源于租户相关配置时必须
        """
        self.scene = scene
        self.templates = NotificationTmplsGetter().get(scene, **scene_kwargs)
        self.sender = NotificationSender()

    def batch_send(self, users: List[TenantUser], **kwargs) -> None:
        """
        批量发送通知到用户
        :param users: 租户用户列表
        :param user_passwd_map: {数据源用户ID: 密码} 映射表，密码初始化/重置场景必须
        """
        for u in users:
            try:
                self.send(u, **self._gen_scene_kwargs(u, **kwargs))
            except Exception:  # noqa: PERF203
                logger.exception("send notification to user %s, scene %s failed", u.id, self.scene)

    def send(self, user: TenantUser, **scene_kwargs) -> None:
        """发送通知到用户，适用于需要用户信息的场景（如密码过期提醒）"""
        for tmpl in self.templates:
            content = self._render_tmpl(tmpl.content, user=user, **scene_kwargs)
            self.sender.send(
                method=tmpl.method,
                title=tmpl.title,
                content=content,
                sender=tmpl.sender,
                tenant_id=user.tenant_id,
                tenant_user_id=user.id,
            )

            logger.info("send %s to user %s, scene %s", tmpl.method.value, user.id, self.scene)

    def send_by_contact(self, contact_info: Dict[str, str | Dict[str, str]], tenant_id: str, **scene_kwargs) -> None:
        """
        直接通过联系方式发送通知，适用于不需要用户信息的场景（如发送验证码）
        :param contact_info: 联系方式，如 {"email": "xxx"} 或 {"phone_info": {"phone": "xxx", "country_code": "xxx"}}
        :param tenant_id: 收件人所属租户 ID（多租户版本调用网关时必须传入）
        """
        for tmpl in self.templates:
            content = self._render_tmpl(tmpl.content, **scene_kwargs)
            self.sender.send(
                tenant_id=tenant_id,
                method=tmpl.method,
                title=tmpl.title,
                content=content,
                sender=tmpl.sender,
                contact_info=contact_info,
            )
            logger.info("send %s by contact info, scene %s", tmpl.method.value, self.scene)

    def _gen_scene_kwargs(self, user, **kwargs) -> Dict[str, str]:
        if self.scene in [
            NotificationScene.USER_INITIALIZE,
            NotificationScene.MANAGER_RESET_PASSWORD,
        ]:
            if "user_passwd_map" not in kwargs:
                raise ValueError("user_passwd_map required when call batch_send")

            return {"passwd": kwargs["user_passwd_map"][user.data_source_user.id]}

        return {}

    def _render_tmpl(self, tmpl_content: str, user: TenantUser | None = None, **scene_kwargs) -> str:
        ctx = TmplContextGenerator.create(scene=self.scene, user=user, **scene_kwargs).gen()
        return Template(tmpl_content).render(Context(ctx))

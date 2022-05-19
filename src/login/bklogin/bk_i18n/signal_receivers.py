# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import translation
from django.utils.translation.trans_real import (
    check_for_language,
    get_languages,
    get_supported_language_variant,
    language_code_re,
    parse_accept_lang_header,
)

from bklogin.bk_i18n.constants import BK_LANG_TO_DJANGO_LANG, DJANGO_LANG_TO_BK_LANG
from bklogin.common.log import logger
from bklogin.components.usermgr_api import upsert_user


def _get_language_from_request(request, user):
    """从请求中获取需要同步到用户个人信息的语言"""
    supported_lang_codes = get_languages()
    # session 有language，说明在登录页面有进行修改或设置，则需要同步到用户个人信息中
    lang_code = request.session.get(translation.LANGUAGE_SESSION_KEY)
    if lang_code in supported_lang_codes and lang_code is not None and check_for_language(lang_code):
        logger.debug(
            "user %s's request lang_code is %s. supported_lang_codes: %s",
            user.username,
            lang_code,
            supported_lang_codes,
        )
        return lang_code

    # 个人信息中已有language
    if user.language:
        logger.debug("user %s already has language: %s", user.username, user.language)
        return None

    logger.debug("user %s has no language, and can't get from session, do a guess", user.username)
    # session 情况不满足同步到用户个人信息，且目前个人信息中无language设置
    # 查询header头
    accept = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    for accept_lang, unused in parse_accept_lang_header(accept):
        if accept_lang == "*":
            break

        if not language_code_re.search(accept_lang):
            continue

        try:
            return get_supported_language_variant(accept_lang)
        except LookupError:
            continue

    # 使用settings默认设置
    try:
        return get_supported_language_variant(settings.LANGUAGE_CODE)
    except LookupError:
        return settings.LANGUAGE_CODE


@receiver(user_logged_in, dispatch_uid="update_user_i18n_info")
def update_user_i18n_info(sender, request, user, *args, **kwargs):
    """登录后自动刷新用户语言等国际化所需信息"""
    time_zone = user.time_zone
    if not time_zone:
        # 默认使用settings中配置
        time_zone = settings.TIME_ZONE
        # sync time_zone to usermgr
        ok, message, _ = upsert_user(username=user.username, time_zone=time_zone)
        if not ok:
            logger.error(
                "fail to update user %s's timezone to %s. %s",
                user.username,
                time_zone,
                message,
            )

    # 设置language
    lang_code = _get_language_from_request(request, user)
    logger.debug(
        "get language code from user %s's request, language code is %s",
        user.username,
        lang_code,
    )
    bk_lang_code = user.language
    if lang_code:
        # 蓝鲸约定的语言代号与Django的有不同，需要进行转换
        bk_lang_code = DJANGO_LANG_TO_BK_LANG[lang_code]
        # sync language to usermgr
        ok, message, _ = upsert_user(username=user.username, language=bk_lang_code)
        if not ok:
            logger.error(
                "fail to update user %s's language to %s. %s",
                user.username,
                bk_lang_code,
                message,
            )
        request.user.language = bk_lang_code

    lang_code = BK_LANG_TO_DJANGO_LANG[bk_lang_code]
    # set session for render html when logged in not redirect
    logger.debug("session.set language code to %s, timezone to %s", lang_code, time_zone)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    translation.activate(lang_code)
    request.LANGUAGE_CODE = translation.get_language()
    request.session[settings.TIMEZONE_SESSION_KEY] = time_zone

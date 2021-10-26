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
from .django_basic import MEDIA_ROOT
from .platform import BK_PAAS_URL

# paths for exempting of login
LOGIN_EXEMPT_WHITE_LIST = (
    r"/favicon.ico$",
    r"/reset_password$",
    r"/set_password$",
    r"/api/v1/password/reset/$",
    r"/api/v1/password/reset_by_token/$",
    r"api/footer/$",
)

# put on s3 maybe better
DEFAULT_LOGO_URL = "img/logo_default.png"

##########
# Export #
##########
EXPORT_ORG_TEMPLATE = MEDIA_ROOT + "/excel/export_org_tmpl.xlsx"
EXPORT_LOGIN_TEMPLATE = MEDIA_ROOT + "/excel/export_login_tmpl.xlsx"

# according to https://docs.qq.com/sheet/DTktLdUtmRldob21P?tab=uty37p&c=C3A0A0
EXPORT_EXCEL_FILENAME = "bk_user_export"

##############
# VersionLog #
##############
VERSION_FILE = "RELEASE.yaml"


###################
# Footer & Header #
###################
BK_DOC_URL = "https://bk.tencent.com/docs/markdown/用户管理/产品白皮书/产品简介/README.md"

FOOTER_CONFIG = {
    "footer": [
        {
            "text": "QQ咨询(800802001)",
            "text_en": "QQ(800802001)",
            "link": "wxwork://message?uin=8444252571319680;",
            "is_blank": False,
        },
        {
            "text": "蓝鲸论坛",
            "text_en": "BlueKing Forum",
            "link": "https://bk.tencent.com/s-mart/community/",
            "is_blank": True,
        },
        {
            "text": "蓝鲸官网",
            "text_en": "BlueKing Official",
            "link": "https://bk.tencent.com/",
            "is_blank": True,
        },
        {
            "text": "蓝鲸智云桌面",
            "text_en": "BlueKing Desktop",
            "link": BK_PAAS_URL,
            "is_blank": True,
        },
    ],
    "copyright": "Copyright © 2012-2021 Tencent BlueKing. All Rights Reserved.",
}

#############
# DRF-Crown #
#############
DRF_CROWN_RESP_CLS = "bkuser_shell.common.response.Response"
DRF_CROWN_DEFAULT_CONFIG = {"remain_request": True}

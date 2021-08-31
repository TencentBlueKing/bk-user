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
from datetime import timedelta
from enum import auto

from bkuser_core.common.enum import AutoLowerEnum
from django.utils.translation import ugettext_lazy as _

TIMEOUT_THRESHOLD = timedelta(hours=1)


class CategoryStatus(AutoLowerEnum):
    NORMAL = auto()
    INACTIVE = auto()

    _choices_labels = (
        (NORMAL, _("正常")),
        (INACTIVE, _("停用")),
    )


class CategoryType(AutoLowerEnum):
    """目录类型

    TODO: 当目录和数据源解耦完成吼，这里的类型实际上就应该去除
    """

    LOCAL = auto()
    MAD = auto()
    LDAP = auto()
    TOF = auto()
    CUSTOM = auto()
    # 特殊的类型，仅在未解耦前桥接
    PLUGGABLE = auto()

    _choices_labels = (
        (LOCAL, _("本地目录")),
        (MAD, _("Microsoft Active Directory")),
        (LDAP, _("OpenLDAP")),
        (TOF, _("TOF")),
        (CUSTOM, "自定义目录"),
        (PLUGGABLE, "可插拔目录"),
    )

    @classmethod
    def get_description(cls, value: "CategoryType"):
        _map = {
            cls.LOCAL: _("本地支持用户的新增、删除、编辑、查询，以及用户的登录认证。"),
            cls.MAD: _("支持对接 Microsoft Active Directory，将用户信息同步到本地或者直接通过接口完成用户登录验证。"),
            cls.LDAP: _("支持对接 OpenLDAP，将用户信息同步到本地或者直接通过接口完成用户登录验证。"),
            cls.TOF: _("支持 TOF 信息同步"),
            cls.CUSTOM: _("支持对接任意符合自定义数据拉取协议的用户系统。"),
            cls.LOCAL.value: _("本地支持用户的新增、删除、编辑、查询，以及用户的登录认证。"),
            cls.MAD.value: _("支持对接 Microsoft Active Directory，将用户信息同步到本地或者直接通过接口完成用户登录验证。"),
            cls.LDAP.value: _("支持对接 OpenLDAP，将用户信息同步到本地或者直接通过接口完成用户登录验证。"),
            cls.TOF.value: _("支持 TOF 信息同步"),
            cls.CUSTOM.value: _("支持对接任意符合自定义数据拉取协议的用户系统。"),
        }
        return _map[value]


class SyncStep(AutoLowerEnum):
    USERS = auto()
    DEPARTMENTS = auto()
    USERS_RELATIONSHIP = auto()
    DEPT_USER_RELATIONSHIP = auto()

    _choices_labels = (
        (USERS, _("用户数据更新")),
        (DEPARTMENTS, _("组织数据更新")),
        (USERS_RELATIONSHIP, _("用户间关系数据更新")),
        (DEPT_USER_RELATIONSHIP, _("用户和组织关系数据更新")),
    )


class SyncTaskType(AutoLowerEnum):
    MANUAL = auto()
    AUTO = auto()

    _choices_labels = ((MANUAL, _("手动导入")), (AUTO, _("定时同步")))


class SyncTaskStatus(AutoLowerEnum):
    SUCCESSFUL = auto()
    FAILED = auto()
    RUNNING = auto()

    _choices_labels = ((SUCCESSFUL, _("成功")), (FAILED, _("失败")), (RUNNING, _("同步中")))

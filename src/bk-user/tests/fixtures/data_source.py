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
from typing import Any, Dict

import pytest
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourcePlugin,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.constants import NotificationMethod, NotificationScene, PasswordGenerateMethod
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import DEFAULT_TENANT


@pytest.fixture()
def local_ds_plugin_config() -> Dict[str, Any]:
    return {
        "enable_account_password_login": True,
        "password_rule": {
            "min_length": 12,
            "contain_lowercase": True,
            "contain_uppercase": True,
            "contain_digit": True,
            "contain_punctuation": True,
            "not_continuous_count": 5,
            "not_keyboard_order": True,
            "not_continuous_letter": True,
            "not_continuous_digit": True,
            "not_repeated_symbol": True,
            "valid_time": 7,
            "max_retries": 3,
            "lock_time": 3600,
        },
        "password_initial": {
            "force_change_at_first_login": True,
            "cannot_use_previous_password": True,
            "reserved_previous_password_count": 3,
            "generate_method": PasswordGenerateMethod.RANDOM,
            "fixed_password": None,
            "notification": {
                "enabled_methods": [NotificationMethod.EMAIL, NotificationMethod.SMS],
                "templates": [
                    {
                        "method": NotificationMethod.EMAIL,
                        "scene": NotificationScene.USER_INITIALIZE,
                        "title": "您的账户已经成功创建",
                        "sender": "蓝鲸智云",
                        "content": "您的账户已经成功创建，请尽快修改密码",
                        "content_html": "<p>您的账户已经成功创建，请尽快修改密码</p>",
                    },
                    {
                        "method": NotificationMethod.EMAIL,
                        "scene": NotificationScene.RESET_PASSWORD,
                        "title": "登录密码重置",
                        "sender": "蓝鲸智云",
                        "content": "点击以下链接以重置代码",
                        "content_html": "<p>点击以下链接以重置代码</p>",
                    },
                    {
                        "method": NotificationMethod.SMS,
                        "scene": NotificationScene.USER_INITIALIZE,
                        "sender": "蓝鲸智云",
                        "content": "您的账户已经成功创建，请尽快修改密码",
                        "content_html": "<p>您的账户已经成功创建，请尽快修改密码</p>",
                    },
                    {
                        "method": NotificationMethod.SMS,
                        "scene": NotificationScene.RESET_PASSWORD,
                        "sender": "蓝鲸智云",
                        "content": "点击以下链接以重置代码",
                        "content_html": "<p>点击以下链接以重置代码</p>",
                    },
                ],
            },
        },
        "password_expire": {
            "remind_before_expire": [1, 7],
            "notification": {
                "enabled_methods": [NotificationMethod.EMAIL, NotificationMethod.SMS],
                "templates": [
                    {
                        "method": NotificationMethod.EMAIL,
                        "scene": NotificationScene.PASSWORD_EXPIRING,
                        "title": "【蓝鲸智云】密码即将到期提醒！",
                        "sender": "蓝鲸智云",
                        "content": "您的密码即将到期！",
                        "content_html": "<p>您的密码即将到期！</p>",
                    },
                    {
                        "method": NotificationMethod.EMAIL,
                        "scene": NotificationScene.PASSWORD_EXPIRED,
                        "title": "【蓝鲸智云】密码到期提醒！",
                        "sender": "蓝鲸智云",
                        "content": "点击以下链接以重置代码",
                        "content_html": "<p>您的密码已到期！</p>",
                    },
                    {
                        "method": NotificationMethod.SMS,
                        "scene": NotificationScene.PASSWORD_EXPIRING,
                        "sender": "蓝鲸智云",
                        "content": "您的密码即将到期！",
                        "content_html": "<p>您的密码即将到期！</p>",
                    },
                    {
                        "method": NotificationMethod.SMS,
                        "scene": NotificationScene.PASSWORD_EXPIRED,
                        "sender": "蓝鲸智云",
                        "content": "您的密码已到期！",
                        "content_html": "<p>您的密码已到期！</p>",
                    },
                ],
            },
        },
    }


@pytest.fixture()
def local_ds_plugin() -> DataSourcePlugin:
    return DataSourcePlugin.objects.get(id=DataSourcePluginEnum.LOCAL)


@pytest.fixture()
def bare_local_data_source(local_ds_plugin_config, local_ds_plugin) -> DataSource:
    """裸本地数据源（没有用户，部门等数据）"""
    return DataSource.objects.create(
        name=generate_random_string(),
        owner_tenant_id=DEFAULT_TENANT,
        plugin=local_ds_plugin,
        plugin_config=local_ds_plugin_config,
    )


@pytest.fixture()
def full_local_data_source(local_ds_plugin_config, local_ds_plugin) -> DataSource:
    """携带用户，部门信息的本地数据源"""

    # 数据源
    ds = DataSource.objects.create(
        name=generate_random_string(),
        owner_tenant_id=DEFAULT_TENANT,
        plugin=local_ds_plugin,
        plugin_config=local_ds_plugin_config,
    )

    # 数据源用户
    zhangsan = DataSourceUser.objects.create(
        code="Employee-3",
        username="zhangsan",
        full_name="张三",
        email="zhangsan@m.com",
        phone="13512345671",
        data_source=ds,
    )
    lisi = DataSourceUser.objects.create(
        code="Employee-4",
        username="lisi",
        full_name="李四",
        email="lisi@m.com",
        phone="13512345672",
        data_source=ds,
    )
    wangwu = DataSourceUser.objects.create(
        code="Employee-5",
        username="wangwu",
        full_name="王五",
        email="wangwu@m.com",
        phone="13512345673",
        data_source=ds,
    )
    zhaoliu = DataSourceUser.objects.create(
        code="Employee-6",
        username="zhaoliu",
        full_name="赵六",
        email="zhaoliu@m.com",
        phone="13512345674",
        data_source=ds,
    )
    liuqi = DataSourceUser.objects.create(
        code="Employee-7",
        username="liuqi",
        full_name="柳七",
        email="liuqi@m.com",
        phone="13512345675",
        data_source=ds,
    )
    maiba = DataSourceUser.objects.create(
        code="Employee-8",
        username="maiba",
        full_name="麦八",
        email="maiba@m.com",
        phone="13512345676",
        data_source=ds,
    )
    yangjiu = DataSourceUser.objects.create(
        code="Employee-9",
        username="yangjiu",
        full_name="杨九",
        email="yangjiu@m.com",
        phone="13512345677",
        data_source=ds,
    )
    lushi = DataSourceUser.objects.create(
        code="Employee-10",
        username="lushi",
        full_name="鲁十",
        email="lushi@m.com",
        phone="13512345678",
        data_source=ds,
    )
    linshiyi = DataSourceUser.objects.create(
        code="Employee-11",
        username="linshiyi",
        full_name="林十一",
        email="linshiyi@m.com",
        phone="13512345679",
        data_source=ds,
    )
    baishier = DataSourceUser.objects.create(
        code="Employee-12",
        username="baishier",
        full_name="白十二",
        email="baishier@m.com",
        phone="13512345670",
        data_source=ds,
    )
    # 不属于任何组织，没有上下级的自由人
    DataSourceUser.objects.create(
        code="Employee-666",
        username="freedom",
        full_name="自由人",
        email="freedom@m.com",
        phone="1351234567X",
        data_source=ds,
    )

    # 数据源部门
    company = DataSourceDepartment.objects.create(data_source=ds, code="company", name="公司")
    dept_a = DataSourceDepartment.objects.create(data_source=ds, code="dept_a", name="部门A")
    dept_b = DataSourceDepartment.objects.create(data_source=ds, code="dept_b", name="部门B")
    center_aa = DataSourceDepartment.objects.create(data_source=ds, code="center_aa", name="中心AA")
    center_ab = DataSourceDepartment.objects.create(data_source=ds, code="center_ab", name="中心AB")
    center_ba = DataSourceDepartment.objects.create(data_source=ds, code="center_ba", name="中心BA")
    group_aaa = DataSourceDepartment.objects.create(data_source=ds, code="group_aaa", name="小组AAA")
    group_aba = DataSourceDepartment.objects.create(data_source=ds, code="group_aba", name="小组ABA")
    group_baa = DataSourceDepartment.objects.create(data_source=ds, code="group_baa", name="小组BAA")

    # 数据源部门关系
    company_node = DataSourceDepartmentRelation.objects.create(department=company, parent=None, data_source=ds)
    dept_a_node = DataSourceDepartmentRelation.objects.create(department=dept_a, parent=company_node, data_source=ds)
    dept_b_node = DataSourceDepartmentRelation.objects.create(department=dept_b, parent=company_node, data_source=ds)
    center_aa_node = DataSourceDepartmentRelation.objects.create(
        department=center_aa, parent=dept_a_node, data_source=ds
    )
    center_ab_node = DataSourceDepartmentRelation.objects.create(
        department=center_ab, parent=dept_a_node, data_source=ds
    )
    center_ba_node = DataSourceDepartmentRelation.objects.create(
        department=center_ba, parent=dept_b_node, data_source=ds
    )
    DataSourceDepartmentRelation.objects.create(department=group_aaa, parent=center_aa_node, data_source=ds)
    DataSourceDepartmentRelation.objects.create(department=group_aba, parent=center_ab_node, data_source=ds)
    DataSourceDepartmentRelation.objects.create(department=group_baa, parent=center_ba_node, data_source=ds)

    # 数据源部门用户关联
    dept_user_relations = [
        DataSourceDepartmentUserRelation(department=company, user=zhangsan),
        DataSourceDepartmentUserRelation(department=dept_a, user=lisi),
        DataSourceDepartmentUserRelation(department=dept_a, user=wangwu),
        DataSourceDepartmentUserRelation(department=center_aa, user=lisi),
        DataSourceDepartmentUserRelation(department=center_aa, user=zhaoliu),
        DataSourceDepartmentUserRelation(department=group_aaa, user=liuqi),
        DataSourceDepartmentUserRelation(department=center_ab, user=maiba),
        DataSourceDepartmentUserRelation(department=center_ab, user=yangjiu),
        DataSourceDepartmentUserRelation(department=group_aba, user=lushi),
        DataSourceDepartmentUserRelation(department=group_aba, user=linshiyi),
        DataSourceDepartmentUserRelation(department=dept_b, user=wangwu),
        DataSourceDepartmentUserRelation(department=center_ba, user=lushi),
        DataSourceDepartmentUserRelation(department=group_baa, user=baishier),
    ]
    DataSourceDepartmentUserRelation.objects.bulk_create(dept_user_relations)

    # 数据源用户 Leader 关联
    user_leader_relations = [
        DataSourceUserLeaderRelation(user=lisi, leader=zhangsan),
        DataSourceUserLeaderRelation(user=wangwu, leader=zhangsan),
        DataSourceUserLeaderRelation(user=zhaoliu, leader=lisi),
        DataSourceUserLeaderRelation(user=liuqi, leader=zhaoliu),
        DataSourceUserLeaderRelation(user=maiba, leader=wangwu),
        DataSourceUserLeaderRelation(user=maiba, leader=lisi),
        DataSourceUserLeaderRelation(user=yangjiu, leader=wangwu),
        DataSourceUserLeaderRelation(user=lushi, leader=maiba),
        DataSourceUserLeaderRelation(user=linshiyi, leader=lushi),
        DataSourceUserLeaderRelation(user=lushi, leader=wangwu),
        DataSourceUserLeaderRelation(user=baishier, leader=lushi),
    ]
    DataSourceUserLeaderRelation.objects.bulk_create(user_leader_relations)

    return ds

# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
    LocalDataSourceIdentityInfo,
)
from bkuser.common.passwd import PasswordGenerator


def init_data_source_users_depts_and_relations(ds: DataSource) -> None:
    """
    为数据源初始化用户，部门，用户部门关系，用户 leader 关系，部门关系等

    部门 & 部门用户关系(* 表示该用户属于多个部门)
    公司                         zhangsan
     ├── 部门 A                  lisi*, wangwu*
     │     ├── 中心 AA           lisi*, zhaoliu
     │     │     └── 小组 AAA    liuqi
     │     └── 中心 AB           maiba, yangjiu
     │           └── 小组 ABA    lushi*, linshiyi
     └── 部门 B                  wangwu*
           └── 中心 BA           lushi*
                 └── 小组 BAA    baishier

    用户 Leader 关系(* 表示该用户有多个 leader)
    zhangsan
     ├── lisi
     │    ├── zhaoliu
     │    │    └── liuqi
     │    └── maiba*
     └── wangwu
          ├── maiba*
          │    └── lushi*
          │         ├── linshiyi
          │         └── baishier
          ├── yangjiu
          └── lushi*

    不属于任何部门，也没有 leader 的用户：freedom
    """

    # 数据源用户
    zhangsan = DataSourceUser.objects.create(
        code="zhangsan",
        username="zhangsan",
        full_name="张三",
        email="zhangsan@m.com",
        phone="13512345671",
        data_source=ds,
    )
    lisi = DataSourceUser.objects.create(
        code="lisi",
        username="lisi",
        full_name="李四",
        email="lisi@m.com",
        phone="13512345672",
        data_source=ds,
    )
    wangwu = DataSourceUser.objects.create(
        code="wangwu",
        username="wangwu",
        full_name="王五",
        email="wangwu@m.com",
        phone="13512345673",
        data_source=ds,
    )
    zhaoliu = DataSourceUser.objects.create(
        code="zhaoliu",
        username="zhaoliu",
        full_name="赵六",
        email="zhaoliu@m.com",
        phone="13512345674",
        data_source=ds,
    )
    liuqi = DataSourceUser.objects.create(
        code="liuqi",
        username="liuqi",
        full_name="柳七",
        email="liuqi@m.com",
        phone="13512345675",
        data_source=ds,
    )
    maiba = DataSourceUser.objects.create(
        code="maiba",
        username="maiba",
        full_name="麦八",
        email="maiba@m.com",
        phone="13512345676",
        data_source=ds,
    )
    yangjiu = DataSourceUser.objects.create(
        code="yangjiu",
        username="yangjiu",
        full_name="杨九",
        email="yangjiu@m.com",
        phone="13512345677",
        data_source=ds,
    )
    lushi = DataSourceUser.objects.create(
        code="lushi",
        username="lushi",
        full_name="鲁十",
        email="lushi@m.com",
        phone="13512345678",
        data_source=ds,
    )
    linshiyi = DataSourceUser.objects.create(
        code="linshiyi",
        username="linshiyi",
        full_name="林十一",
        email="linshiyi@m.com",
        phone="13512345679",
        data_source=ds,
    )
    baishier = DataSourceUser.objects.create(
        code="baishier",
        username="baishier",
        full_name="白十二",
        email="baishier@m.com",
        phone="13512345670",
        data_source=ds,
    )
    # 不属于任何组织，没有上下级的自由人
    DataSourceUser.objects.create(
        code="freedom",
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
        DataSourceDepartmentUserRelation(department=company, user=zhangsan, data_source=ds),
        DataSourceDepartmentUserRelation(department=dept_a, user=lisi, data_source=ds),
        DataSourceDepartmentUserRelation(department=dept_a, user=wangwu, data_source=ds),
        DataSourceDepartmentUserRelation(department=center_aa, user=lisi, data_source=ds),
        DataSourceDepartmentUserRelation(department=center_aa, user=zhaoliu, data_source=ds),
        DataSourceDepartmentUserRelation(department=group_aaa, user=liuqi, data_source=ds),
        DataSourceDepartmentUserRelation(department=center_ab, user=maiba, data_source=ds),
        DataSourceDepartmentUserRelation(department=center_ab, user=yangjiu, data_source=ds),
        DataSourceDepartmentUserRelation(department=group_aba, user=lushi, data_source=ds),
        DataSourceDepartmentUserRelation(department=group_aba, user=linshiyi, data_source=ds),
        DataSourceDepartmentUserRelation(department=dept_b, user=wangwu, data_source=ds),
        DataSourceDepartmentUserRelation(department=center_ba, user=lushi, data_source=ds),
        DataSourceDepartmentUserRelation(department=group_baa, user=baishier, data_source=ds),
    ]
    DataSourceDepartmentUserRelation.objects.bulk_create(dept_user_relations)

    # 数据源用户 Leader 关联
    user_leader_relations = [
        DataSourceUserLeaderRelation(user=lisi, leader=zhangsan, data_source=ds),
        DataSourceUserLeaderRelation(user=wangwu, leader=zhangsan, data_source=ds),
        DataSourceUserLeaderRelation(user=zhaoliu, leader=lisi, data_source=ds),
        DataSourceUserLeaderRelation(user=liuqi, leader=zhaoliu, data_source=ds),
        DataSourceUserLeaderRelation(user=maiba, leader=wangwu, data_source=ds),
        DataSourceUserLeaderRelation(user=maiba, leader=lisi, data_source=ds),
        DataSourceUserLeaderRelation(user=yangjiu, leader=wangwu, data_source=ds),
        DataSourceUserLeaderRelation(user=lushi, leader=maiba, data_source=ds),
        DataSourceUserLeaderRelation(user=linshiyi, leader=lushi, data_source=ds),
        DataSourceUserLeaderRelation(user=lushi, leader=wangwu, data_source=ds),
        DataSourceUserLeaderRelation(user=baishier, leader=lushi, data_source=ds),
    ]
    DataSourceUserLeaderRelation.objects.bulk_create(user_leader_relations)


def init_local_data_source_identity_infos(ds: DataSource) -> None:
    """初始化本地数据源身份信息"""
    if not ds.is_local:
        return

    plugin_cfg = ds.get_plugin_cfg()
    passwd_generator = PasswordGenerator(plugin_cfg.password_rule.to_rule())  # type: ignore

    for user in DataSourceUser.objects.filter(data_source=ds):
        LocalDataSourceIdentityInfo.objects.get_or_create(
            user=user,
            defaults={
                "data_source": ds,
                "username": user.username,
                "password": passwd_generator.generate(),
            },
        )

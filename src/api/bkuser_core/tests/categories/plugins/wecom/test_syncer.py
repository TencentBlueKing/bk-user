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
import pytest
from unittest import mock

from bkuser_core.categories.plugins.metas import ProfileMeta
from bkuser_core.departments.models import Department
from bkuser_core.tests.utils import make_simple_profile

pytestmark = pytest.mark.django_db


class TestWecomSyncer:
    @pytest.mark.parametrize(
        "pre_created, departments, users, expected_adding, expected_updating",
        [
            (
                    [],
                    [
                        {'id': 1, 'name': '测试企业', 'parentid': 0, 'order': 100000000},
                        {'id': 2, 'name': '部门1', 'parentid': 1, 'order': 100000000},
                        {'id': 4, 'name': '部门2', 'parentid': 1, 'order': 99998000},
                        {'id': 5, 'name': '部门3', 'parentid': 1, 'order': 99997000},
                        {'id': 6, 'name': '部门4', 'parentid': 1, 'order': 99996000},
                        {'id': 7, 'name': '部门5', 'parentid': 1, 'order': 99995000},
                        {'id': 8, 'name': '部门2-1', 'parentid': 4, 'order': 100000000},
                        {'id': 9, 'name': '部门2-2', 'parentid': 4, 'order': 99999000},
                        {'id': 10, 'name': '部门2-3', 'parentid': 4, 'order': 99998000},
                        {'id': 11, 'name': '部门2-4', 'parentid': 4, 'order': 99998500},
                        {'id': 12, 'name': '部门2-5', 'parentid': 4, 'order': 99997500},
                        {'id': 13, 'name': '部门1-1', 'parentid': 2, 'order': 100000000},
                        {'id': 14, 'name': '部门1-2', 'parentid': 2, 'order': 99999000},
                        {'id': 15, 'name': '部门1-3', 'parentid': 2, 'order': 99998000},
                        {'id': 16, 'name': '部门3-1', 'parentid': 5, 'order': 100000000},
                        {'id': 17, 'name': '部门3-2', 'parentid': 5, 'order': 99999000},
                        {'id': 18, 'name': '部门3-3', 'parentid': 5, 'order': 99998000},
                        {'id': 19, 'name': '部门3-4', 'parentid': 5, 'order': 99997000},
                        {'id': 20, 'name': '部门3-5', 'parentid': 5, 'order': 99996000},
                        {'id': 21, 'name': '部门3-6', 'parentid': 5, 'order': 99995000},
                        {'id': 22, 'name': '部门3-7', 'parentid': 5, 'order': 99994000},
                        {'id': 23, 'name': '部门3-8', 'parentid': 5, 'order': 99993000},
                        {'id': 24, 'name': '部门3-9', 'parentid': 5, 'order': 99992000}],
                    [
                        {
                            "userid": "zhangsan",
                            "name": "zhangsan",
                            "department": [
                                1
                            ],
                            "position": "",
                            "mobile": "13123456789",
                            "gender": "1",
                            "email": "13123456789@qq1.com",
                            "avatar": "http://wework.qpic.cn/bizmail/zhangsan/0",
                            "status": 1,
                            "enable": 1,
                            "isleader": 0,
                            "extattr": {
                                "attrs": []
                            },
                            "hide_mobile": 0,
                            "telephone": "",
                            "order": [
                                0
                            ],
                            "external_profile": {
                                "external_attr": [],
                                "external_corp_name": ""
                            },
                            "main_department": 1,
                            "qr_code": "https://open.work.weixin.qq.com/wwopen/userQRCode",
                            "alias": "",
                            "is_leader_in_dept": [
                                0
                            ],
                            "address": "",
                            "thumb_avatar": "http://wework.qpic.cn/bizmail/zhangsan/100"
                        },
                        {
                            "userid": "lisi",
                            "name": "lisi",
                            "department": [
                                1,
                                14,
                                9,
                                21,
                                7
                            ],
                            "position": "",
                            "mobile": "13123456789",
                            "gender": "1",
                            "email": "lisi@qq1.com",
                            "avatar": "http://wework.qpic.cn/bizmail/lisi/0",
                            "status": 1,
                            "enable": 1,
                            "isleader": 0,
                            "extattr": {
                                "attrs": []
                            },
                            "hide_mobile": 0,
                            "telephone": "",
                            "order": [
                                0,
                                0,
                                0,
                                0,
                                0
                            ],
                            "external_profile": {
                                "external_attr": [],
                                "external_corp_name": ""
                            },
                            "main_department": 1,
                            "qr_code": "https://open.work.weixin.qq.com/wwopen/userQRCode",
                            "alias": "lisi",
                            "is_leader_in_dept": [
                                0,
                                0,
                                0,
                                0,
                                0
                            ],
                            "address": "",
                            "thumb_avatar": "http://wework.qpic.cn/bizmail/lisi/100"
                        },
                        {
                            "userid": "wangwu",
                            "name": "wangwu",
                            "department": [
                                1,
                                2,
                                4,
                                7
                            ],
                            "position": "",
                            "mobile": "13123456789",
                            "gender": "1",
                            "email": "wangwu@qq1.com",
                            "avatar": "http://wework.qpic.cn/bizmail/wangwu/0",
                            "status": 1,
                            "enable": 1,
                            "isleader": 1,
                            "extattr": {
                                "attrs": []
                            },
                            "hide_mobile": 0,
                            "telephone": "",
                            "order": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "external_profile": {
                                "external_attr": [],
                                "external_corp_name": ""
                            },
                            "main_department": 1,
                            "qr_code": "https://open.work.weixin.qq.com/wwopen/userQRCode",
                            "alias": "",
                            "is_leader_in_dept": [
                                1,
                                0,
                                0,
                                1
                            ],
                            "address": "",
                            "thumb_avatar": "http://wework.qpic.cn/bizmail/wangwu/100"
                        }
                    ],
                    ['zhangsan', 'lisi', 'wangwu'],
                    []
            ),
            (
                    ["zhangsan"],
                    [
                        {'id': 1, 'name': '测试企业', 'parentid': 0, 'order': 100000000},
                        {'id': 2, 'name': '部门1', 'parentid': 1, 'order': 100000000},
                        {'id': 4, 'name': '部门2', 'parentid': 1, 'order': 99998000},
                        {'id': 5, 'name': '部门3', 'parentid': 1, 'order': 99997000},
                        {'id': 6, 'name': '部门4', 'parentid': 1, 'order': 99996000},
                        {'id': 7, 'name': '部门5', 'parentid': 1, 'order': 99995000},
                        {'id': 8, 'name': '部门2-1', 'parentid': 4, 'order': 100000000},
                        {'id': 9, 'name': '部门2-2', 'parentid': 4, 'order': 99999000},
                        {'id': 10, 'name': '部门2-3', 'parentid': 4, 'order': 99998000},
                        {'id': 11, 'name': '部门2-4', 'parentid': 4, 'order': 99998500},
                        {'id': 12, 'name': '部门2-5', 'parentid': 4, 'order': 99997500},
                        {'id': 13, 'name': '部门1-1', 'parentid': 2, 'order': 100000000},
                        {'id': 14, 'name': '部门1-2', 'parentid': 2, 'order': 99999000},
                        {'id': 15, 'name': '部门1-3', 'parentid': 2, 'order': 99998000},
                        {'id': 16, 'name': '部门3-1', 'parentid': 5, 'order': 100000000},
                        {'id': 17, 'name': '部门3-2', 'parentid': 5, 'order': 99999000},
                        {'id': 18, 'name': '部门3-3', 'parentid': 5, 'order': 99998000},
                        {'id': 19, 'name': '部门3-4', 'parentid': 5, 'order': 99997000},
                        {'id': 20, 'name': '部门3-5', 'parentid': 5, 'order': 99996000},
                        {'id': 21, 'name': '部门3-6', 'parentid': 5, 'order': 99995000},
                        {'id': 22, 'name': '部门3-7', 'parentid': 5, 'order': 99994000},
                        {'id': 23, 'name': '部门3-8', 'parentid': 5, 'order': 99993000},
                        {'id': 24, 'name': '部门3-9', 'parentid': 5, 'order': 99992000}],
                    [
                        {
                            "userid": "zhangsan",
                            "name": "zhangsan",
                            "department": [
                                1
                            ],
                            "position": "",
                            "mobile": "12345678911",
                            "gender": "1",
                            "email": "13123456789@qqx.com",
                            "avatar": "http://wework.qpic.cn/bizmail/zhangsan/0",
                            "status": 1,
                            "enable": 1,
                            "isleader": 0,
                            "extattr": {
                                "attrs": []
                            },
                            "hide_mobile": 0,
                            "telephone": "",
                            "order": [
                                0
                            ],
                            "external_profile": {
                                "external_attr": [],
                                "external_corp_name": ""
                            },
                            "main_department": 1,
                            "qr_code": "https://open.work.weixin.qq.com/wwopen/userQRCode",
                            "alias": "",
                            "is_leader_in_dept": [
                                0
                            ],
                            "address": "",
                            "thumb_avatar": "http://wework.qpic.cn/bizmail/zhangsan/100"
                        },
                        {
                            "userid": "lisi",
                            "name": "lisi",
                            "department": [
                                1,
                                14,
                                9,
                                21,
                                7
                            ],
                            "position": "",
                            "mobile": "12345678912",
                            "gender": "1",
                            "email": "lisi@qq1.com",
                            "avatar": "http://wework.qpic.cn/bizmail/lisi/0",
                            "status": 1,
                            "enable": 1,
                            "isleader": 0,
                            "extattr": {
                                "attrs": []
                            },
                            "hide_mobile": 0,
                            "telephone": "",
                            "order": [
                                0,
                                0,
                                0,
                                0,
                                0
                            ],
                            "external_profile": {
                                "external_attr": [],
                                "external_corp_name": ""
                            },
                            "main_department": 1,
                            "qr_code": "https://open.work.weixin.qq.com/wwopen/userQRCode",
                            "alias": "lisi",
                            "is_leader_in_dept": [
                                0,
                                0,
                                0,
                                0,
                                0
                            ],
                            "address": "",
                            "thumb_avatar": "http://wework.qpic.cn/bizmail/lisi/100"
                        },
                        {
                            "userid": "wangwu",
                            "name": "wangwu",
                            "department": [
                                1,
                                2,
                                4,
                                7
                            ],
                            "position": "",
                            "mobile": "13123456789",
                            "gender": "1",
                            "email": "wangwu@qq1.com",
                            "avatar": "http://wework.qpic.cn/bizmail/wangwu/0",
                            "status": 1,
                            "enable": 1,
                            "isleader": 1,
                            "extattr": {
                                "attrs": []
                            },
                            "hide_mobile": 0,
                            "telephone": "",
                            "order": [
                                0,
                                0,
                                0,
                                0
                            ],
                            "external_profile": {
                                "external_attr": [],
                                "external_corp_name": ""
                            },
                            "main_department": 1,
                            "qr_code": "https://open.work.weixin.qq.com/wwopen/userQRCode",
                            "alias": "",
                            "is_leader_in_dept": [
                                1,
                                0,
                                0,
                                1
                            ],
                            "address": "",
                            "thumb_avatar": "http://wework.qpic.cn/bizmail/wangwu/100"
                        }
                    ],
                    ['lisi', 'wangwu'],
                    ['zhangsan']
            )

        ]
    )
    def test_sync_users(self, pre_created, test_wecom_syncer, departments, users, expected_adding, expected_updating):
        """测试同步用户"""
        for p in pre_created:
            make_simple_profile(p, force_create_params={"category_id": test_wecom_syncer.category_id})

        with mock.patch.object(test_wecom_syncer.fetcher, "fetch") as fetch:
            fetch.return_value = [], [], users
            test_wecom_syncer._sync_users(users, departments)
            test_wecom_syncer.db_sync_manager.sync_all()
        for k in expected_adding:
            assert (
                    test_wecom_syncer.db_sync_manager.magic_get(k, ProfileMeta)
                    in test_wecom_syncer.db_sync_manager._sets[ProfileMeta.target_model].adding_items
            )

        for k in expected_updating:
            assert (
                    test_wecom_syncer.db_sync_manager.magic_get(k, ProfileMeta)
                    in test_wecom_syncer.db_sync_manager._sets[ProfileMeta.target_model].updating_items
            )

    @pytest.mark.parametrize(
        "departments, expected, expected_count", [
            (
                    [
                        {'id': 1, 'name': '测试企业', 'parentid': 0, 'order': 100000000},
                        {'id': 2, 'name': '部门1', 'parentid': 1, 'order': 100000000},
                        {'id': 4, 'name': '部门2', 'parentid': 1, 'order': 99998000},
                        {'id': 5, 'name': '部门3', 'parentid': 1, 'order': 99997000},
                        {'id': 6, 'name': '部门4', 'parentid': 1, 'order': 99996000},
                        {'id': 7, 'name': '部门5', 'parentid': 1, 'order': 99995000},
                        {'id': 8, 'name': '部门2-1', 'parentid': 4, 'order': 100000000},
                        {'id': 9, 'name': '部门2-2', 'parentid': 4, 'order': 99999000},
                        {'id': 10, 'name': '部门2-3', 'parentid': 4, 'order': 99998000},
                        {'id': 11, 'name': '部门2-4', 'parentid': 4, 'order': 99998500},
                        {'id': 12, 'name': '部门2-5', 'parentid': 4, 'order': 99997500},
                        {'id': 13, 'name': '部门1-1', 'parentid': 2, 'order': 100000000},
                        {'id': 14, 'name': '部门1-2', 'parentid': 2, 'order': 99999000},
                        {'id': 15, 'name': '部门1-3', 'parentid': 2, 'order': 99998000},
                        {'id': 16, 'name': '部门3-1', 'parentid': 5, 'order': 100000000},
                        {'id': 17, 'name': '部门3-2', 'parentid': 5, 'order': 99999000},
                        {'id': 18, 'name': '部门3-3', 'parentid': 5, 'order': 99998000},
                        {'id': 19, 'name': '部门3-4', 'parentid': 5, 'order': 99997000},
                        {'id': 20, 'name': '部门3-5', 'parentid': 5, 'order': 99996000},
                        {'id': 21, 'name': '部门3-6', 'parentid': 5, 'order': 99995000},
                        {'id': 22, 'name': '部门3-7', 'parentid': 5, 'order': 99994000},
                        {'id': 23, 'name': '部门3-8', 'parentid': 5, 'order': 99993000},
                        {'id': 24, 'name': '部门3-9', 'parentid': 5, 'order': 99992000}],
                    [['测试企业']], 23)
        ]
    )
    def test_sync_departments(self, test_wecom_category, test_wecom_syncer, departments, expected, expected_count):
        """测试同步部门"""
        with mock.patch.object(test_wecom_syncer.fetcher, "fetch") as fetch:
            fetch.return_value = [], departments, []
            test_wecom_syncer._sync_departments(departments)

        for route in expected:
            parent = None
            for d in route:
                parent = Department.objects.get(name=d, parent=parent, category_id=test_wecom_syncer.category_id)

        assert Department.objects.filter(category_id=test_wecom_category.id).count() == expected_count

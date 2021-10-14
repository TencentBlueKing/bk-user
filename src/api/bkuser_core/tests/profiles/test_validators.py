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
from bkuser_core.profiles.constants import DynamicFieldTypeEnum
from bkuser_core.profiles.models import DynamicFieldInfo
from bkuser_core.profiles.validators import validate_domain, validate_extras_value_unique, validate_username
from bkuser_core.tests.utils import make_simple_category, make_simple_profile
from rest_framework.exceptions import ValidationError

pytestmark = pytest.mark.django_db


class TestValidator:
    @pytest.mark.parametrize(
        "username",
        [
            "asdf",
            "123",
            "asdf---...___123",
            "12345678912345678912345678912345",
            "asdf123",
            "asdf123--..",
            "1",
            "a",
            "Asds",
            "0Asd-",
        ],
    )
    def test_right_validate_username(self, username):
        """检测各种用户名校验"""
        validate_username(username)

    @pytest.mark.parametrize(
        "username",
        [
            "-asdf",
            ".asdf",
            "asdf@asdf",
            "asdf@123",
            "12345678912345678912345678912345a",
            "/asdf",
            "",
        ],
    )
    def test_wrong_validate_username(self, username):
        with pytest.raises(ValidationError):
            validate_username(username)

    @pytest.mark.parametrize(
        "domain",
        [
            "asdf",
            "123",
            "asdf---...123",
            "1234567891234567",
            "asdf123",
            "asdf123--..",
            "1",
            "a",
            "Asds",
            "0Asd-",
        ],
    )
    def test_right_validate_domain(self, domain):
        """检测 domain 字段"""
        validate_domain(domain)

    @pytest.mark.parametrize(
        "domain",
        [
            "-asdf",
            ".asdf",
            "asdf_",
            "asdf@asdf",
            "asdf@123",
            "1234567891234567a",
            "/asdf",
            "",
        ],
    )
    def test_wrong_validate_domain(self, domain):
        with pytest.raises(ValidationError):
            validate_domain(domain)

    @pytest.mark.parametrize(
        "username",
        [
            "asdf",
            "123",
            "asdf---...___123",
            "12345678912345678912345678912345",
            "asdf123",
            "asdf123--..",
            "1",
            "a",
            "Asds",
            "0Asd-",
        ],
    )
    def test_db_save_username(self, username):
        make_simple_profile(username=username)

    @pytest.mark.parametrize(
        "domain",
        [
            "-asdf",
            ".asdf",
            "asdf@asdf",
            "asdf@123",
            "12345678912345678912345678912345a",
            "/asdf",
            "",
        ],
    )
    def test_db_save_domain(self, domain):
        with pytest.raises(ValidationError):
            make_simple_profile(username=domain)


class TestExtrasValidator:
    def test_duplicate_in_same_category(self):
        _ = DynamicFieldInfo.objects.create(
            name="xxxx",
            unique=True,
            order=100,
            type=DynamicFieldTypeEnum.STRING.value,
            display_name="xxxx",
        )
        _ = DynamicFieldInfo.objects.create(
            name="yyyy",
            unique=True,
            order=100,
            options=[["111", "xxx"]],
            type=DynamicFieldTypeEnum.MULTI_ENUM.value,
            display_name="yyyy",
        )
        a = make_simple_profile(
            username="fakeA",
            force_create_params={"extras": {"xxxx": "aaaa", "111": "xxx"}},
        )
        # multi_enum & one_enum 类型都不会检查唯一性
        validate_extras_value_unique(value={"111": "xxx"}, category_id=a.category_id)

        with pytest.raises(ValidationError):
            validate_extras_value_unique(value={"xxxx": "aaaa"}, category_id=a.category_id)

    def test_duplicate_in_other_category(self):
        _ = DynamicFieldInfo.objects.create(
            name="xxxx", unique=True, order=100, type=DynamicFieldTypeEnum.STRING.value
        )
        c = make_simple_category(domain="testB", display_name="Test B")
        _ = make_simple_profile(username="fakeA", force_create_params={"extras": {"xxxx": "aaaa"}})

        validate_extras_value_unique(value={"xxxx": "aaaa"}, category_id=c.pk)

    def test_normal(self):
        _ = DynamicFieldInfo.objects.create(
            name="xxxx", unique=True, order=100, type=DynamicFieldTypeEnum.STRING.value
        )
        a = make_simple_profile(username="fakeA", force_create_params={"extras": {"xxxx": "aaaa"}})

        validate_extras_value_unique(value={"xxxx": "aaa"}, category_id=a.category_id)

    def test_no_field(self):
        _ = DynamicFieldInfo.objects.create(
            name="xxxx", unique=True, order=100, type=DynamicFieldTypeEnum.STRING.value
        )
        a = make_simple_profile(username="fakeA", force_create_params={"extras": {"yyyy": "aaaa"}})

        validate_extras_value_unique(value={"yyyy": "aaa"}, category_id=a.category_id)

    def test_db_save(self):
        _ = DynamicFieldInfo.objects.create(
            name="yyyy", unique=True, order=100, type=DynamicFieldTypeEnum.STRING.value
        )
        make_simple_profile(username="fakeA", force_create_params={"extras": {"yyyy": "aaaa"}})

        with pytest.raises(ValidationError):
            make_simple_profile(username="fakeB", force_create_params={"extras": {"yyyy": "aaaa"}})

    def test_multiple_field(self):
        _ = DynamicFieldInfo.objects.create(
            name="yyyy", unique=True, order=100, type=DynamicFieldTypeEnum.STRING.value
        )
        make_simple_profile(
            username="fakeA",
            force_create_params={"extras": {"yyyy": "aaab", "bbbb": "aaaa"}},
        )

        with pytest.raises(ValidationError):
            make_simple_profile(username="fakeB", force_create_params={"extras": {"yyyy": "aaab"}})

        make_simple_profile(username="fakeB", force_create_params={"extras": {"yyyy": "aaaa"}})

    @pytest.mark.parametrize(
        "field_name,updating_values",
        [
            ("yyyy", ["aaab", "xxxxx", "wer", 666]),
        ],
    )
    def test_profile_update(self, field_name, updating_values):
        _ = DynamicFieldInfo.objects.create(
            name=field_name,
            unique=True,
            order=100,
            type=DynamicFieldTypeEnum.STRING.value,
        )
        a = make_simple_profile(username="fakeA", force_create_params={"extras": {field_name: "test"}})

        for i in updating_values:
            a.extras = {"yyyy": i}
            a.save()

    @pytest.mark.parametrize(
        "black_names,target",
        [
            (["extras"], "extras"),
        ],
    )
    def test_black_extra_name(self, black_names, target):
        from bkuser_core.profiles import validators

        validators.BLACK_FIELD_NAMES = black_names
        with pytest.raises(ValidationError):
            DynamicFieldInfo.objects.create(
                name=target,
                unique=True,
                order=100,
                type=DynamicFieldTypeEnum.STRING.value,
            )

    @pytest.mark.parametrize(
        "field_names,force_extras",
        [
            (["xxxx", "yyyy"], [{"yyyy": "abcd"}, {"xxxx": "abcd"}]),
        ],
    )
    def test_duplicate_other_missing_key(self, field_names, force_extras):
        for field_name in field_names:
            DynamicFieldInfo.objects.create(
                name=field_name,
                display_name=f"Dis_{field_name}",
                unique=True,
                order=100,
                type=DynamicFieldTypeEnum.STRING.value,
            )

        for i, e in enumerate(force_extras):
            make_simple_profile(username=f"fake{i}", force_create_params={"extras": e})

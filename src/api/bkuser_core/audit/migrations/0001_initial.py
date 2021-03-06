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
# Generated by Django 1.11.23 on 2019-11-04 15:35
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
import jsonfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApiRequest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("create_time", models.DateTimeField(auto_now_add=True)),
                ("update_time", models.DateTimeField(auto_now=True)),
                (
                    "operator",
                    models.CharField(blank=True, max_length=32, null=True, verbose_name="操作者"),
                ),
                ("extra_value", jsonfield.fields.JSONField(null=True)),
                ("uri", models.CharField(max_length=64, verbose_name="请求 URI")),
                ("time_cost", models.FloatField(verbose_name="请求耗时")),
                ("method", models.CharField(max_length=32, verbose_name="请求方法")),
                ("status", models.IntegerField(verbose_name="Http状态码")),
            ],
            options={
                "ordering": ["create_time"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="GeneralLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("create_time", models.DateTimeField(auto_now_add=True)),
                ("update_time", models.DateTimeField(auto_now=True)),
                (
                    "operator",
                    models.CharField(blank=True, max_length=32, null=True, verbose_name="操作者"),
                ),
                ("extra_value", jsonfield.fields.JSONField(null=True)),
            ],
            options={
                "ordering": ["create_time"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="LogIn",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("create_time", models.DateTimeField(auto_now_add=True)),
                ("update_time", models.DateTimeField(auto_now=True)),
                (
                    "operator",
                    models.CharField(blank=True, max_length=32, null=True, verbose_name="操作者"),
                ),
                ("extra_value", jsonfield.fields.JSONField(null=True)),
                (
                    "is_success",
                    models.BooleanField(default=True, verbose_name="是否成功登陆"),
                ),
                (
                    "reason",
                    models.CharField(
                        blank=True,
                        choices=[("bad_password", "密码错误")],
                        max_length=32,
                        null=True,
                        verbose_name="登陆失败原因",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="profiles.Profile",
                        verbose_name="登陆用户",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ResetPassword",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("create_time", models.DateTimeField(auto_now_add=True)),
                ("update_time", models.DateTimeField(auto_now=True)),
                (
                    "operator",
                    models.CharField(blank=True, max_length=32, null=True, verbose_name="操作者"),
                ),
                ("extra_value", jsonfield.fields.JSONField(null=True)),
                (
                    "token",
                    models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
                ),
                (
                    "is_success",
                    models.BooleanField(default=False, verbose_name="是否重置成功"),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="profiles.Profile",
                        verbose_name="登陆用户",
                    ),
                ),
            ],
            options={
                "ordering": ["-create_time"],
            },
        ),
    ]

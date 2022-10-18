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
# from django.core.validators import RegexValidator

# FIXME: 目前创建只有前端进行了校验?

# class CategoryDisplayNameValidator:
#     """目录展示名格式校验"""
#     def __init__(self, resource_type):
#         self.resource_type = resource_type
#         self.message = "%s 由1-16位字母、数字、汉字、点(.)、减号(-)字符组成"
#         self.validator = RegexValidator(r"[\w.-]+", message=self.message)
#     def __call__(self, value):
#         self.validator(value)


# class CategoryDomainValidator:
#     """目录登陆域格式校验"""
#     def __init__(self, resource_type):
#         self.resource_type = resource_type
#         self.message = "%s 由1-16位字母、数字、点(.)、减号(-)字符组成，以字母或数字开头" % self.resource_type
#         self.validator = RegexValidator("^(?![0-9]+.*$)(?!-)[a-zA-Z0-9-]{,63}(?<!-)$", message=self.message)
#     def __call__(self, value):
#         self.validator(value)

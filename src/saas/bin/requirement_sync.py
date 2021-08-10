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
import logging
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def sync_requirements():
    """
    同步依赖 同步app.yml, 与requirements.txt一致
    :return:
    """
    """
    1. 获取requirements
    """
    requirements_dict = dict()
    with open(requirements_file, "r") as r_f:
        pattern = re.compile(r"[\w\-]*==")
        line = r_f.readline()
        # 寻找包起始行
        while not pattern.match(line):
            line = r_f.readline()
            if not line:
                break
        if not line:
            logger.warning("未找到依赖")
            return
        first_letter = line[0]
        requirements_dict[first_letter] = [(line.split("==")[0], line.split("==")[1].strip("\n"))]

        lines = r_f.readlines()

        for line in lines:
            first_letter = line[0]
            if first_letter in requirements_dict:
                requirements_dict[first_letter].append((line.split("==")[0], line.split("==")[1].strip("\n")))
            else:
                requirements_dict[first_letter] = [(line.split("==")[0], line.split("==")[1].strip("\n"))]

    """
    2. 同步
    """
    with open(app_yml_file, "r") as a_f:
        pattern = re.compile(r"[\w]*:\n")
        lines = a_f.readlines()
        start_index = -1
        end_index = -1
        for index, line in enumerate(lines):
            if line == "libraries:\n":
                start_index = index
                continue
            if pattern.match(line) and start_index != -1:
                end_index = index
        front_part = lines[0:start_index]
        end_part = [] if end_index == -1 else lines[end_index:]

        mid_part = ["libraries:\n"]
        for items in requirements_dict.items():
            item = items[1]
            for pkg in item:
                mid_part.append("- name: {}\n  version: {}\n".format(pkg[0], pkg[1]))

    with open(app_yml_file, "w") as a_f:
        a_f.writelines(front_part + mid_part + end_part)

    logger.info("同步完成")


if __name__ == "__main__":
    requirements_file = "./requirements.txt"
    app_yml_file = "./app.yml"
    sync_requirements()

# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from datetime import datetime

from zxcvbn import feedback, matching, scoring, time_estimates


def zxcvbn_ext(password, user_inputs=None, max_length=72):
    """对 zxcvbn.zxcvbn 方法扩展，在原来返回结果的基础上增加了所有匹配项的返回值。
    Note: 去除了 python2 对 str/unicode 的兼容处理，统一使用 str 类型。
    """
    # Throw error if password exceeds max length
    if len(password) > max_length:
        raise ValueError(f"Password exceeds max length of {max_length} characters.")

    # Python 3 string types
    basestring = (str, bytes)

    if user_inputs is None:
        user_inputs = []

    start = datetime.now()

    sanitized_inputs = []
    for arg in user_inputs:
        argx = str(arg) if not isinstance(arg, basestring) else arg
        sanitized_inputs.append(argx.lower())

    ranked_dictionaries = matching.RANKED_DICTIONARIES
    ranked_dictionaries["user_inputs"] = matching.build_ranked_dict(sanitized_inputs)

    matches = matching.omnimatch(password, ranked_dictionaries)
    result = scoring.most_guessable_match_sequence(password, matches)
    result["calc_time"] = datetime.now() - start

    attack_times = time_estimates.estimate_attack_times(result["guesses"])
    for prop, val in attack_times.items():
        result[prop] = val

    result["feedback"] = feedback.get_feedback(result["score"], result["sequence"])

    return result, matches

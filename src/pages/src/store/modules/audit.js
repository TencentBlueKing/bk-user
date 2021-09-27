/**
* by making 蓝鲸智云-用户管理(Bk-User) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License");
* you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and limitations under the License.
*/
/* eslint-disable no-unused-vars */
import http from '@/api';

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    // 登录审计分页查询
    getLoginList(_context, {
      startTime = '',
      endTime = '',
      page = '',
      pageSize = '',
    } = {}, _config = {}) {
      return http.get(`api/v2/audit/login_log/?start_time=${startTime}&end_time=${endTime}&page=${page}&page_size=${pageSize}`);
    },
    // 审计分页查询
    getList(_context, {
      startTime = '',
      endTime = '',
      keyword = '',
      page = '',
      pageSize = '',
    } = {}, _config = {}) {
      // return http.get(`api/v2/audit/operation_logs/?start_time=${startTime}&end_time=${endTime}&keyword=${keyword}`)
      return http.get(`api/v2/audit/operation_logs/?start_time=${startTime}&end_time=${endTime}&page=${page}&page_size=${pageSize}${keyword && (`&keyword=${keyword}`)}`);
      // &keyword=${keyword}&page=${page}&page_size=${page_size}
    },
    // 审计导出
    getAuditderive(context, params, config = {}) {
      const { url, startTime, endTime } = params;
      return http.get(`${url}/api/v2/audit/login_log/export/?start_time=${startTime}&end_time=${endTime}`);
    },
  },
};

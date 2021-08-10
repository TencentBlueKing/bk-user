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
    getAuthInfo(context, params, config = {}) {
      return http.get('api/v2/fields/manageable/');
    },
    postFields(context, params, config = {}) {
      return http.post('api/v2/fields/', params.data);
    },
    deleteFields(context, params, config = {}) {
      return http.delete(`api/v2/fields/${params.id}/`);
    },
    patchFields(context, params, config = {}) {
      return http.patch(`api/v2/fields/${params.id}/`, params.data);
    },
    // 获取字段，表头、设置列表字段也会用到
    getFields(context, params, config = {}) {
      return http.get('api/v2/fields/');
    },
    // 字段设置列表拖拽重新排序
    dragFields(context, params, config = {}) {
      const { id, index } = params;
      return http.patch(`api/v2/fields/${id}/order/${index}/`);
    },
    // 设置哪些字段可在首页表格展示
    updateFieldsVisible(context, params, config = {}) {
      return http.patch('api/v2/fields/visible/', {
        updating_ids: params.idList,
      });
    },
  },
};

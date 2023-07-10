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
      return http.get('api/v1/web/fields/manageable/');
    },
    postFields(context, params, config = {}) {
      return http.post('api/v1/web/fields/', params.data);
    },
    deleteFields(context, params, config = {}) {
      return http.delete(`api/v1/web/fields/${params.id}/`);
    },
    patchFields(context, params, config = {}) {
      return http.patch(`api/v1/web/fields/${params.id}/`, params.data);
    },
    // 获取字段，表头、设置列表字段也会用到
    getFields(context, params, config = {}) {
      return http.get('api/v1/web/fields/');
    },
    // 字段设置列表拖拽重新排序
    dragFields(context, params, config = {}) {
      const { id, index } = params;
      return http.patch(`api/v1/web/fields/${id}/order/${index}/`);
    },
    // 设置哪些字段可在首页表格展示
    updateFieldsVisible(context, params, config = {}) {
      return http.patch('api/v1/web/fields/visible/', {
        updating_ids: params.idList,
      });
    },
    // 回收策略配置
    getGlobalSettings(context, params, config = {}) {
      return http.get('api/v1/web/global_settings/namespaces/recycling_strategy/');
    },
    // 回收策略配置修改
    putGlobalSettings(context, params, config = {}) {
      const url = 'api/v1/web/global_settings/namespaces/recycling_strategy/';
      return http.put(url, params, config);
    },
    // 回收站目录列表
    getCategoryList(context, params, config = {}) {
      const { pageSize, page, keyword } = params;
      return keyword
        ? http.get(`api/v1/web/recycle_bin/categories/?page_size=${pageSize}&page=${page}&keyword=${params.keyword}`)
        : http.get(`api/v1/web/recycle_bin/categories/?page_size=${pageSize}&page=${page}`);
    },
    // 回收站组织列表
    getDepartmentList(context, params, config = {}) {
      const { pageSize, page, keyword } = params;
      return keyword
        ? http.get(`api/v1/web/recycle_bin/departments/?page_size=${pageSize}&page=${page}&keyword=${params.keyword}`)
        : http.get(`api/v1/web/recycle_bin/departments/?page_size=${pageSize}&page=${page}`);
    },
    // 回收站人员列表
    getProfileList(context, params, config = {}) {
      const { pageSize, page, keyword } = params;
      return keyword
        ? http.get(`api/v1/web/recycle_bin/profiles/?page_size=${pageSize}&page=${page}&keyword=${params.keyword}`)
        : http.get(`api/v1/web/recycle_bin/profiles/?page_size=${pageSize}&page=${page}`);
    },
    // 目录还原预检查接口
    categoriesCheck(context, params, config = {}) {
      return http.get(`api/v1/web/recycle_bin/categories/${params.category_id}/conflicts`);
    },
    // 目录还原接口
    categoriesRevert(context, params, config = {}) {
      return http.put(`api/v1/web/recycle_bin/categories/${params.category_id}/`);
    },
    // 目录硬删除接口
    categoriesHardDelete(context, params, config = {}) {
      return http.delete(`api/v1/web/recycle_bin/categories/${params.category_id}`);
    },
  },
};

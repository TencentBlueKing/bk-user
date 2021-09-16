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
  state: {
    currentPasswordInfo: {
      // 当前 passwordInfo 对应的 Id
      id: '',
      // 重置密码、新增成员密码有效期默认值依赖的数据
      data: null,
    },
  },
  mutations: {
    updatePasswordInfo(state, payload) {
      state.currentPasswordInfo = payload;
    },
  },
  actions: {
    // 获取目录 + 组织树
    getOrganizationTree(context, { onlyEnabled = true } = {}, config = {}) {
      return http.get(`api/v2/departments/?only_enabled=${onlyEnabled}`);
    },
    // 根据ID获取组织列表（展开对应的子级）
    getDataById(context, params, config = {}) {
      // return (params.searchType && params.searchId)
      //     ? http.get(`api/v1/departments/${params.id}/?type=${params.searchType}&id=${params.searchId}`)
      //     : http.get(`api/v1/departments/${params.id}/`)
      return http.get(`api/v2/departments/${params.id}/`);
    },
    // 根据组织 id 搜索组织列表
    searchDataByCategory(context, params, config = {}) {
      const { id, keyword, withAncestors, searchLength } = params;
      if (withAncestors) {
        return http.get(`api/v2/categories/${id}/departments/search/?keyword=${keyword}&max_items=${searchLength}&with_ancestors=true`);
      }
      return http.get(`api/v2/categories/${id}/departments/search/?keyword=${keyword}&max_items=${searchLength}`);
    },
    // 新增组织
    addDepartment(context, params, config = {}) {
      return http.post('api/v2/departments/', params);
    },
    // 删除组织
    deleteDepartment(context, params, config = {}) {
      return http.delete(`api/v2/departments/${params.id}/`);
    },
    // 编辑组织名称
    modifyDepartmentName(context, params, config = {}) {
      const { id, name } = params;
      return http.patch(`api/v2/departments/${id}/`, { name });
    },
    // 目录或组织上移、下移
    switchNodeOrder(context, params, config = {}) {
      return http.patch(`api/v2/${params.nodeType}/${params.id}/switch_order/${params.upId}/`);
    },
    // 批量新增用户到部门
    postUserToDepartments(context, params, config = {}) {
      const { id, idList } = params;
      return http.post(`api/v2/departments/${id}/profiles/`, { profile_id_list: idList });
    },

    // 组织树搜索
    getSearchResult(context, params, config = {}) {
      return http.get(`api/v2/search/detail/?keyword=${params.searchKey}&max_items=${params.searchLength}&only_enabled=true`);
    },

    // 用户列表，分页查询接口
    getProfiles(context, params, config = {}) {
      const { id, pageSize, page, keyword, recursive } = params;
      return keyword
        ? http.get(`api/v2/departments/${id}/profiles/?page_size=${pageSize}&page=${page}&recursive=${recursive}&keyword=${keyword}`)
        : http.get(`api/v2/departments/${id}/profiles/?page_size=${pageSize}&page=${page}&recursive=${recursive}`);
    },
    // 新增用户
    postProfile(context, params, config = {}) {
      return http.post('api/v2/profiles/', params);
    },
    // 批量删除 彻底删除
    deleteProfiles(context, params, config = {}) {
      config.data = params;
      return http.delete('api/v2/batch/profiles/', config);
    },
    // 修改用户状态
    patchProfile(context, params, config = {}) {
      const { id, data } = params;
      return http.patch(`api/v2/profiles/${id}/`, data);
    },
    // 设置所在组织
    batchAddDepart(context, params, config = {}) {
      return http.patch('api/v2/batch/profiles/', params);
    },
    // 从其他组织拉取，这里的 id 是目录 id
    getAllUser(context, params, config = {}) {
      return http.get(`api/v2/categories/${params.id}/profiles/?no_page=true`);
    },
    // 直接上级数据
    getSupOrganization(context, params, config = {}) {
      const { id, pageSize, page, keyword } = params;
      return http.get(`api/v2/categories/${id}/profiles/?keyword=${keyword}&page=${page}&page_size=${pageSize}`);
    },
    // 根据id查看用户
    getProfileById(context, params, config = {}) {
      return http.get(`api/v2/profiles/${params.id}/`);
    },
  },
};

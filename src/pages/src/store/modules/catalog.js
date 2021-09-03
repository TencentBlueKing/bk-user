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
import http from '@/api';

export default {
  namespaced: true,
  state: {
    // 默认值
    defaults: {
      password: null,
      connection: null,
      fieldsMad: null,
      fieldsLdap: null,
    },
    // 下拉列表可选值
    choices: {
      // connection
      ssl_encryption: [],
      // fields
      basic_pull_node: [],
      group_pull_node: [],
      bk_fields: [],
      mad_fields: [],
    },
  },
  mutations: {
    updateDefaults(state, defaults) {
      state.defaults = defaults;
    },
    updateChoices(state, choices) {
      state.choices = choices;
    },
  },
  actions: {
    // ['post', 'put', 'patch'] return http.post(url, data, config)
    // ['delete', 'get', 'head', 'options'] return http.get(url, config)

    // 获取数据更新记录
    ajaxGetUpdateRecord(_context, params, config = {}) {
      const url = `/api/v2/sync_task/?page=${params.page}&page_size=${params.page_size}`;
      return http.get(url, config);
    },

    // 获取数据更新日记详细记录
    ajaxGetUpdateDetailRecord(_context, params, config = {}) {
      const url = `/api/v2/sync_task/${params.id}/logs`;
      return http.get(url, config);
    },

    // 获取新增目录类型数据
    ajaxGetCatalogMetas(_context, _params, config = {}) {
      const url = 'api/v2/categories_metas/';
      return http.get(url, config);
    },

    // 获取用户目录列表
    ajaxGetCatalogList(_context, _params, config = {}) {
      const url = 'api/v2/categories/';
      return http.get(url, config);
      // return http.get(`?mock-file=catalog&invoke=ajaxGetCatalogList`, config)
    },

    // eslint-disable-next-line no-unused-vars
    ajaxSyncCatalog(_context, params, _config = {}) {
      return http.post(`api/v2/categories/${params.id}/sync/`);
      // const mockUrl = `?mock-file=catalog`
      // return http.get(mockUrl, config)
    },
    // eslint-disable-next-line no-unused-vars
    ajaxImportUser(_context, params, _config = {}) {
      return http.post(`api/v2/categories/${params.id}/sync/`, params.data);
      // const mockUrl = `?mock-file=catalog`
      // return http.get(mockUrl, config)
    },

    // 用户目录（基本设置）
    ajaxPostCatalog(_context, params, config = {}) {
      const url = 'api/v2/categories/';
      return http.post(url, {
        type: params.type,
        ...params.data,
      }, config);
      // return http.get(`?mock-file=catalog&invoke=ajaxPostCatalog`, config)
    },
    ajaxDeleteCatalog(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/`;
      return http.delete(url, config);
      // return http.get(`?mock-file=catalog`, config)
    },
    ajaxPutCatalog(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/`;
      // todo put 还没有 put
      return http.patch(url, params.data, config);
      // return http.get(`?mock-file=catalog`, config)
    },
    ajaxPatchCatalog(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/`;
      return http.patch(url, params.data, config);
      // return http.get(`?mock-file=catalog`, config)
    },
    ajaxGetCatalog(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/`;
      return http.get(url, config);
      // return http.get(`?mock-file=catalog&invoke=ajaxGetCatalog`, config)
    },

    // 密码设置
    ajaxPostPassport(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/settings/namespaces/password/`;
      // 这里后端又自动生成了配置，所以改成 put
      return http.put(url, params.data, config);
      // return http.get(`?mock-file=catalog`, config)
    },
    ajaxPutPassport(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/settings/namespaces/password/`;
      return http.put(url, params.data, config);
      // return http.get(`?mock-file=catalog`, config)
    },
    ajaxGetPassport(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/settings/namespaces/password/`;
      return http.get(url, config);
      // return http.get(`?mock-file=catalog&invoke=ajaxGetPassport`, config)
    },
    ajaxGetDefaultPassport(_context, _params, config = {}) {
      const url = 'api/v2/settings/metas/?category_type=local&namespace=password';
      return http.get(url, config);
      // return http.get(`?mock-file=catalog&invoke=ajaxGetDefaultPassport`, config)
    },

    // 连接设置
    ajaxPostConnection(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/settings/namespaces/connection/`;
      return http.post(url, params.data, config);
      // return http.get(`?mock-file=catalog`, config)
    },
    ajaxPutConnection(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/settings/namespaces/connection/`;
      return http.put(url, params.data, config);
      // return http.get(`?mock-file=catalog`, config)
    },
    ajaxGetConnection(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/settings/namespaces/connection/`;
      return http.get(url, config);
      // return http.get(`?mock-file=catalog&invoke=ajaxGetConnection`, config)
    },
    ajaxGetDefaultConnection(_context, _params, config = {}) {
      const url = 'api/v2/settings/metas/?category_type=mad&namespace=connection';
      return http.get(url, config);
      // return http.get(`?mock-file=catalog&invoke=ajaxGetDefaultConnection`, config)
    },
    ajaxTestConnection(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/test_connection/`;
      const obj = {};
      const arr = Object.values(params.data);
      arr.forEach((item) => {
        Object.assign(obj, item);
      });
      return http.post(url, obj, config);
      // return http.get(`?mock-file=catalog&invoke=ajaxTestConnection`, config)
    },

    // 字段设置
    ajaxPostFields(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/settings/namespaces/fields/`;
      return http.post(url, params.data, config);
      // return http.get(`?mock-file=catalog`, config)
    },
    ajaxPutFields(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/settings/namespaces/fields/`;
      return http.put(url, params.data, config);
      // return http.get(`?mock-file=catalog`, config)
    },
    ajaxGetFields(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/settings/namespaces/fields/`;
      return http.get(url, config);
      // return http.get(`?mock-file=catalog&invoke=ajaxGetFields`, config)
    },
    ajaxGetDefaultFields(_context, params, config = {}) {
      const url = `api/v2/settings/metas/?category_type=${params.type}&namespace=fields`;
      return http.get(url, config);
      // return http.get(`?mock-file=catalog&invoke=ajaxGetDefaultFields`, config)
    },
    ajaxTestField(_context, params, config = {}) {
      const url = `api/v2/categories/${params.id}/test_fetch_data/`;
      const obj = {};
      const arr = Object.values(params.data);
      arr.forEach((item) => {
        Object.assign(obj, item);
      });
      return http.post(url, obj, config);
      // return http.get(`?mock-file=catalog&invoke=ajaxTestConnection`, config)
    },
  },
};

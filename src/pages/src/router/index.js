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
import Vue from 'vue';
import VueRouter from 'vue-router';

import store from '@/store';
import http from '@/api';
import { rootPath, connectToMain } from '@blueking/sub-saas/dist/main.js';

Vue.use(VueRouter);

const Organization = () => import(/* webpackChunkName: 'Organization' */'../views/organization');
const Catalog = () => import(/* webpackChunkName: 'Catalog' */'../views/catalog');
const Audit = () => import(/* webpackChunkName: 'Audit' */'../views/audit');
const Setting = () => import(/* webpackChunkName: 'Setting' */'../views/setting');
const SetPassword = () => import(/* webpackChunkName: 'SetPassword' */'../views/password/Set');
const ResetPassword = () => import(/* webpackChunkName: 'ResetPassword' */'../views/password/Reset');
const ModifyPassword = () => import(/* webpackChunkName: 'ModifyPassword' */'../views/password/Modify');
const Recycle = () => import(/* webpackChunkName: 'Recycle' */'../views/recycle');
const NotFound = () => import(/* webpackChunkName: 'NotFound' */'../views/404');


const routes = [
  {
    path: rootPath,
    redirect: '/organization',
  },
  {
    path: `${rootPath}organization`,
    name: 'organization',
    component: Organization,
  },
  {
    path: `${rootPath}catalog`,
    name: 'catalog',
    component: Catalog,
  },
  {
    path: `${rootPath}setting`,
    name: 'setting',
    component: Setting,
  },
  {
    path: `${rootPath}audit`,
    name: 'audit',
    component: Audit,
  },
  {
    path: `${rootPath}resetPassword`,
    name: 'resetPassword',
    component: ResetPassword,
  },
  {
    path: `${rootPath}change_password`,
    name: 'modifyPassword',
    component: ModifyPassword,
  },
  {
    path: `${rootPath}set_password`,
    name: 'setPassword',
    component: SetPassword,
  },
  {
    path: `${rootPath}recycle`,
    name: 'recycle',
    component: Recycle,
  },
  {
    path: '*',
    name: 'NotFound',
    component: NotFound,
  },
];

const router = new VueRouter({
  mode: 'history',
  base: window.SITE_URL,
  routes,
});

connectToMain(router);

const cancelRequest = async () => {
  const allRequest = http.queue.get();
  const requestQueue = allRequest.filter(request => request.cancelWhenRouteChange);
  await http.cancel(requestQueue.map(request => request.requestId));
};

router.beforeEach(async (to, from, next) => {
  if (['organization', 'catalog', 'audit', 'setting', 'recycle'].includes(to.name)) {
    store.commit('updateInitLoading', true);
  }
  store.commit('updateNoAuthData', null);
  await cancelRequest();
  next();
});

export default router;

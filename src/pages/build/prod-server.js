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
const express = require('express');
const path = require('path');
const artTemplate = require('express-art-template');
const history = require('connect-history-api-fallback');
const cookieParser = require('cookie-parser');
// eslint-disable-next-line new-cap
const app = new express();
const axios = require('axios');

const http = axios.create({
  withCredentials: true,
});

http.interceptors.response.use(response => response, error => Promise.reject(error));

// APA 重定向回首页，由首页Route响应处理
// https://github.com/bripkens/connect-history-api-fallback#index
app.use(history({
  index: '/',
  rewrites: [
    {
      // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
      // 兼容 /cs/28aa9eda67644a6eb254d694d944307e/cluster/BCS-MESOS-10001/node/127.0.0.1 这样以 IP 结尾的 url
      // from: /\d+\.\d+\.\d+\.\d+$/,
      from: /\/(\d+\.)*\d+$/,
      to: '/',
    },
    {
      // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
      // 兼容
      // bcs/projectId/app/214/taskgroups/0.application-1-13.test123.10013.1510806131114508229/containers/containerId
      from: /\/\/+.*\..*\//,
      to: '/',
    },
  ],
}));

app.use(cookieParser());

// 首页
app.get('/', (req, res) => {
  const index = path.join(__dirname, '../dist/index.html');
  res.render(index);
});

// 配置静态资源
app.use('/', express.static(path.join(__dirname, '../dist')));

// 配置视图
app.set('views', path.join(__dirname, '../dist'));

// 配置模板引擎
// http://aui.github.io/art-template/zh-cn/docs/
app.engine('html', artTemplate);
app.set('view engine', 'html');

// 配置端口
app.listen(5000, () => {
  console.log('App is running in port 5000');
});

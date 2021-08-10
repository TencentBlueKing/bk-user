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
import path from 'path';
import prodEnv from './prod.env';
import devEnv from './dev.env';

export default {
  build: {
    // env 会通过 webpack.DefinePlugin 注入到前端代码里
    env: prodEnv,
    // 打包的根路径
    assetsRoot: path.resolve(__dirname, '../dist'),
    // util.assetsPath 可通过此变量将静态资源打包到一个子路径
    assetsSubDirectory: '',
    // webpack output publicPath，最好用变量 BK_STATIC_URL
    assetsPublicPath: '{{ BK_STATIC_URL }}',
    productionSourceMap: true,
    productionGzip: false,
    productionGzipExtensions: ['js', 'css'],
    bundleAnalyzerReport: process.env.npm_config_report,
  },
  dev: {
    // env 会通过 webpack.DefinePlugin 注入到前端代码里
    env: devEnv,
    port: 8089,
    localDevUrl: 'http://dev.bktencent-example.com',
    localDevPort: 8089,
    assetsSubDirectory: 'static',
    assetsPublicPath: '/',
    proxyTable: {},
    cssSourceMap: false,
    autoOpenBrowser: false,
  },
};

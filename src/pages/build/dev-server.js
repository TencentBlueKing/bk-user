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
import express from 'express';
import open from 'open';
import webpack from 'webpack';
import webpackDevMiddleware from 'webpack-dev-middleware';
import webpackHotMiddleware from 'webpack-hot-middleware';
import proxyMiddleware from 'http-proxy-middleware';
import bodyParser from 'body-parser';
import history from 'connect-history-api-fallback';
import cors from 'cors';

import devConf from './webpack.dev.conf';
import ajaxMiddleware from './ajax-middleware';
import config from './config';
import checkVer from './check-versions';

checkVer();

const port = process.env.PORT || config.dev.localDevPort;

const autoOpenBrowser = !!config.dev.autoOpenBrowser;

const proxyTable = config.dev.proxyTable;

const app = express();
const compiler = webpack(devConf);

const devMiddleware = webpackDevMiddleware(compiler, {
  publicPath: devConf.output.publicPath,
  quiet: true,
});

const hotMiddleware = webpackHotMiddleware(compiler, {
  log: false,
  heartbeat: 2000,
});

Object.keys(proxyTable).forEach((context) => {
  let options = proxyTable[context];
  if (typeof options === 'string') {
    options = {
      target: options,
    };
  }
  app.use(proxyMiddleware(context, options));
});

app.use(history({
  verbose: false,
  rewrites: [
    {
      // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
      // 兼容 /router/127.0.0.1 这样以 IP 结尾的 url
      from: /(\d+\.)*\d+$/,
      to: '/',
    },
    {
      // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
      // 兼容 /router/0.aaa.bbb.ccc.1234567890/ddd/eee
      from: /\/+.*\..*\//,
      to: '/',
    },
  ],
}));

const allowedOrigins = [`http://localhost:${port}`, `${config.dev.localDevUrl}:${port}`];

app.use(cors({
  origin: (origin, callback) => {
    if (!origin) {
      return callback(null, true);
    }
    if (allowedOrigins.indexOf(origin) === -1) {
      const msg = 'The CORS policy for this site does not allow access from the specified Origin.';
      return callback(new Error(msg), false);
    }
    return callback(null, true);
  },
  methods: ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH'],
  credentials: true,
}));

app.use(devMiddleware);

app.use(hotMiddleware);

app.use(bodyParser.json());

app.use(bodyParser.urlencoded({
  extended: true,
}));

app.use(ajaxMiddleware);

const staticPath = path.posix.join(config.dev.assetsPublicPath, config.dev.assetsSubDirectory);
app.use(staticPath, express.static('./static'));

const url = `${config.dev.localDevUrl}:${port}`;

let _resolve;
const readyPromise = new Promise((resolve) => {
  _resolve = resolve;
});

console.log('> Starting dev server...');
devMiddleware.waitUntilValid(() => {
  console.log(`> Listening at ${url}\n`);
  if (autoOpenBrowser) {
    open(url);
  }
  _resolve();
});

const server = app.listen(port);

export default {
  ready: readyPromise,
  close: () => {
    server.close();
  },
};

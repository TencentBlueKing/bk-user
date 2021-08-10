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
import fs from 'fs';
import url from 'url';
import queryString from 'querystring';
import chalk from 'chalk';

const mockReqHandler = (req, mockParamValue) => {
  // mockFile replace 去掉 最后的 /，例如 /a/b/c/ => /a/b/c
  const mockFilePath = `${path.join(__dirname, '../mock/ajax', mockParamValue.replace(/\/+$/, ''))}.js`;
  if (!fs.existsSync(mockFilePath)) {
    return false;
  }

  console.log(chalk.magenta('Mock File Query: ', mockParamValue));
  console.log(chalk.magenta('Mock File Path: ', mockFilePath));

  delete require.cache[require.resolve(mockFilePath)];
  return require(mockFilePath);
};

export default async function ajaxMiddleWare(req, res, next) {
  // eslint-disable-next-line node/no-deprecated-api
  let query = url.parse(req.url).query;

  if (!query) {
    return next();
  }

  query = queryString.parse(query);

  const mockParamValue = query['mock-file'];
  // 不是 mock 请求
  if (!mockParamValue) {
    return next();
  }
  const postData = req.body || '';
  const mockDataHandler = mockReqHandler(req, mockParamValue);

  if (!mockDataHandler) {
    res.status(404).end();
    return;
  }

  let data = await mockDataHandler.response(query, postData, req);

  if (data.statusCode) {
    res.status(data.statusCode).end(JSON.stringify(data));
    return;
  }

  let contentType = req.headers['Content-Type'];

  // 返回值未指定内容类型，默认按 JSON 格式处理返回
  if (!contentType) {
    contentType = 'application/json;charset=UTF-8';
    req.headers['Content-Type'] = contentType;
    res.setHeader('Content-Type', contentType);
    data = JSON.stringify(data || {});
  }

  res.end(data);

  return next();
}

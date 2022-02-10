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
import webpack from 'webpack';
import merge from 'webpack-merge';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import FriendlyErrorsPlugin from 'friendly-errors-webpack-plugin';

import config from './config';
import baseConf from './webpack.base.conf';
import manifest from '../static/lib-manifest.json';

const webpackConfig = merge(baseConf, {
  mode: 'development',
  entry: {
    main: './src/main.js',
  },

  module: {
    rules: [
      {
        test: /\.(css|postcss|scss)$/,
        use: [
          'vue-style-loader',
          {
            loader: 'css-loader',
            options: {
              importLoaders: 1,
            },
          },
          {
            loader: 'postcss-loader',
            options: {
              config: {
                path: path.resolve(__dirname, '..', 'postcss.config.js'),
              },
            },
          },
          {
            loader: "sass-loader",
            options: {
              implementation: require("sass") //使用dart-sass代替node-sass
            }
          },
          // 'sass-loader',
        ],
      },
    ],
  },

  plugins: [
    new webpack.DefinePlugin(config.dev.env),

    new webpack.DllReferencePlugin({
      context: __dirname,
      manifest,
    }),

    new webpack.HotModuleReplacementPlugin(),

    new webpack.NoEmitOnErrorsPlugin(),

    new HtmlWebpackPlugin({
      filename: 'index.html',
      template: 'index-dev.html',
      inject: true,
    }),

    new FriendlyErrorsPlugin(),
  ],
});

Object.keys(webpackConfig.entry).forEach((name) => {
  webpackConfig.entry[name] = ['./build/dev-client'].concat(webpackConfig.entry[name]);
});

export default webpackConfig;

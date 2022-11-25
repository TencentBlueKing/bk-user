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
import './public-path';
import Vue from 'vue';
import VueCropper from 'vue-cropperjs';
import vClickOutside from 'v-click-outside';
import VueClipboard from 'vue-clipboard2';

import App from '@/App';
import router from '@/router';
import store from '@/store';
import { injectCSRFTokenToHeaders } from '@/api';
import '@/common/bkmagic';
import i18n from '@/language/i18n';
import methods from '@/plugins/methods';
import bus from '@/common/bus';
import cursor from '@/directives/cursor';
import { Base64 } from 'js-base64';
import xss from 'xss';
import Rsa from '@/common/rsa';

Vue.component(VueCropper);
Vue.use(vClickOutside);
Vue.use(VueClipboard);
Vue.use(methods);
Vue.directive('cursor', cursor);
Vue.config.devtools = true;
Vue.prototype.$bus = new Vue();
Vue.use(Base64);
Vue.prototype.Rsa = Rsa;
Vue.prototype.$xss = (html) => {
  const attrs = ['class', 'title', 'target', 'style', 'src', 'onerror'];
  return xss(html || '', {
    onTagAttr: (tag, name, value) => {
      if (attrs.includes(name)) {
        return `${name}=${value}`;
      }
    },
  });
};

injectCSRFTokenToHeaders();
window.bus = bus;
window.mainComponent = new Vue({
  el: '#app',
  router,
  store,
  i18n,
  components: { App },
  template: '<App />',
});

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router';
import App from './app.vue';
import './css/index.css';
import i18n from './language/index';

// 全量引入 bkui-vue
import bkui from 'bkui-vue';
// 全量引入 bkui-vue 样式
import 'bkui-vue/dist/style.css';

createApp(App)
  .use(router)
  .use(createPinia())
  .use(bkui)
  .use(i18n)
  .mount('.app');

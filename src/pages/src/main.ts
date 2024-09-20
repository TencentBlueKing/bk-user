// 全量引入 bkui-vue
import bkui, { bkTooltips, InfoBox } from 'bkui-vue';
import { createPinia } from 'pinia';
import { createApp } from 'vue';
import VueDOMPurifyHTML from 'vue-dompurify-html';

import App from './app.vue';
import i18n from './language/index';
import router from './router';

import './css/index.css';
import '../static/bk_icon_font/style.css';
import '../static/blueking-icon/style.css';
// 全量引入 bkui-vue 样式
import 'bkui-vue/dist/style.css';

const leaveBoxInstance = InfoBox({
  isShow: false,
});
const leaveBox = (opt = {}) => new Promise((resolve) => {
  const opts = Object.assign({
    title: i18n.global.t('确定离开当前页？'),
    subTitle: i18n.global.t('离开将会导致未保存的信息丢失'),
    class: 'leave-box',
    quickClose: false,
    onConfirm: async () => {
      window.changeInput = false;
      resolve(true);
    },
    confirmText: i18n.global.t('确定'),
    onClose: () => {
      resolve(false);
    },
  }, opt);
  leaveBoxInstance.update(opts);
  leaveBoxInstance.show(opts);
});

const leaveBefore = async () => {
  if (window.changeInput) {
    const isLeave = await leaveBox();
    if (isLeave) {
      window.changeInput = false;
    }
    return isLeave;
  }
  return true;
};

window.leaveBefore = leaveBefore;

createApp(App)
  .use(router)
  .use(createPinia())
  .use(bkui)
  .use(i18n)
  .use(VueDOMPurifyHTML)
  .provide('editLeaveBefore', leaveBox)
  .directive('bkTooltips', bkTooltips)
  .mount('.app');

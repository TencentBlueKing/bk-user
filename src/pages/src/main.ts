import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router';
import App from './app.vue';
import './css/index.css';
import '../static/bk_icon_font/style.css';
import '../static/blueking-icon/style.css';

// 全量引入 bkui-vue
import bkui, { InfoBox } from 'bkui-vue';
// 全量引入 bkui-vue 样式
import 'bkui-vue/dist/style.css';

const leaveBoxInstance = InfoBox({
  isShow: false,
});
const leaveBox = (opt = {}) => new Promise((resolve) => {
  const opts = Object.assign({
    title: '确定离开当前页？',
    subTitle: '离开将会导致未保存的信息丢失',
    quickClose: false,
    onConfirm: async () => {
      window.changeInput = false;
      resolve(true);
    },
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
  .provide('editLeaveBefore', leaveBox)
  .mount('.app');

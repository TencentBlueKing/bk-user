<template>
  <div class="main-content">
    <div class="bg-img right-top">
      <img src="../static/images/right-top.png" alt="">
    </div>
    <div class="bg-img right-bottom">
      <img src="../static/images/right-bottom.png" alt="">
    </div>
    <div class="bg-img left-bottom">
      <img src="../static/images/left-bottom.png" alt="">
    </div>
    <div class="login-model">
      <router-view></router-view>
      <div class="tenant-footer">
        <div class="cursor-pointer tenant-protocol" @click="protocolVisible = true">{{ $t('用户协议') }} ></div>
        <div class="language-switcher">
          <div class="language-select">
            <p class="language-item" :class="{ active: activeTab === 'zh-cn' }" @click="handleSwitchLocale('zh-cn')">
              <span class="text-active">中文</span>
            </p>
            <p class="language-item" :class="{ active: activeTab === 'en' }" @click="handleSwitchLocale('en')">
              <span class="text-active">English</span>
            </p>
          </div>
        </div>
      </div>
      <Protocol v-if="protocolVisible && activeTab === 'zh-cn'" @close="protocolVisible = false" />
      <ProtocolEn v-if="protocolVisible && activeTab === 'en'" @close="protocolVisible = false" />
    </div>
    <div id="particles-js"></div>
    <footer class="footer">
      <p>
        <span v-dompurify-html="contact"></span>
        <bk-popover theme="light" placement="bottom">
          <a href="" target="_blank" class="link follow-us">
            | {{ $t('关注我们') }}
          </a>
          <template #content>
            <span class="qr-box"><img class="qr" src="../static/images/qr.png" alt=""></span>
          </template>
        </bk-popover>
      </p>
      <p>{{ copyright }}</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue';
import { getPlatformConfig, setShortcutIcon, setDocumentTitle } from '@blueking/platform-config';
import { platformConfig } from '@/store/platformConfig';
import Protocol from './views/components/protocol.vue';
import ProtocolEn from './views/components/protocol-en.vue';
import I18n from '@/language/index';
import Cookies from 'js-cookie';

const activeTab = ref(I18n.global.locale.value);
/**
 * 用户协议是否显示
 */
const protocolVisible = ref(false);

onMounted(() => {
  particlesJS(
    'particles-js',
    {
      particles: {
        number: {
          value: 10,
          density: {
            enable: true,
            value_area: 800,
          },
        },
        color: {
          value: '#D0D9E2',
        },
        shape: {
          type: 'circle',
          stroke: {
            width: 0,
            color: '#000000',
          },
          polygon: {
            nb_sides: 5,
          },
          image: {
            src: 'img/github.svg',
            width: 100,
            height: 100,
          },
        },
        opacity: {
          value: 0.5,
          random: false,
          anim: {
            enable: false,
            speed: 1,
            opacity_min: 0.1,
            sync: false,
          },
        },
        size: {
          value: 7,
          random: false,
          anim: {
            enable: false,
            speed: 1,
            size_min: 0.1,
            sync: false,
          },
        },
        line_linked: {
          enable: true,
          distance: 150,
          color: '#D0D9E2',
          opacity: 0.4,
          width: 2,
        },
        move: {
          enable: true,
          speed: 1,
          direction: 'none',
          random: true,
          straight: false,
          out_mode: 'out',
          attract: {
            enable: false,
            rotateX: 600,
            rotateY: 1200,
          },
        },
      },
      interactivity: {
        detect_on: 'canvas',
        events: {
          onhover: {
            enable: true,
            mode: 'repulse',
          },
          onclick: {
            enable: true,
            mode: 'push',
          },
          resize: true,
        },
        modes: {
          grab: {
            distance: 400,
            line_linked: {
              opacity: 1,
            },
          },
          bubble: {
            distance: 400,
            size: 40,
            duration: 2,
            opacity: 8,
            speed: 1,
          },
          repulse: {
            distance: 50,
          },
          push: {
            particles_nb: 4,
          },
          remove: {
            particles_nb: 2,
          },
        },
      },
      retina_detect: true,
      config_demo: {
        hide_card: false,
        background_color: '#b61924',
        background_image: '',
        background_position: '50% 50%',
        background_repeat: 'no-repeat',
        background_size: 'cover',
      },
    },
  );
});

const platformConfigData = platformConfig();
const url = `${window.BK_SHARED_RES_URL}/bk_login/base.js`;  // url 远程配置文件地址
const defaults = {
  name: '登录',
  nameEn: 'Login',
  brandName: '蓝鲸智云',
  brandNameEn: 'BlueKing',
  version: '3.0',
};

const getConfigData = async () => {
  const config =  await getPlatformConfig(url, defaults);

  setShortcutIcon(config.favicon);
  setDocumentTitle(config.i18n);
  platformConfigData.update(config);
};
getConfigData();
const contact = computed(() => platformConfigData.i18n.footerInfoHTML);
const copyright = computed(() => platformConfigData.footerCopyrightContent);


/**
 * 切换语言
 * @param locale 语言代码
 */
const handleSwitchLocale = (locale: 'zh-cn' | 'en') => {
  activeTab.value = locale;
  // 因为未登录，所以改为后端直接调用接口
  // const api = `${window.BK_COMPONENT_API_URL}/api/c/compapi/v2/usermanage/fe_update_user_language/`;
  // const scriptId = 'jsonp-script';
  // const prevJsonpScript = document.getElementById(scriptId);
  // if (prevJsonpScript) {
  //   document.body.removeChild(prevJsonpScript);
  // }
  // const script = document.createElement('script');
  // script.type = 'text/javascript';
  // script.src = `${api}?language=${locale}`;
  // script.id = scriptId;
  // document.body.appendChild(script);

  Cookies.set('blueking_language', locale, {
    expires: 3600,
    path: '/',
    domain: window.BK_DOMAIN,
  });
  I18n.global.locale.value = locale;
  document.querySelector('html')?.setAttribute('lang', locale);
  window.location.reload();
};
</script>

<style lang="postcss" scoped>
.login-model {
  z-index: 2;
  width: 480px;
  background: #FFFFFF;
  box-shadow: 0 4px 12px 0 #00000033;
  border-radius: 10px;
  position: absolute;
  left: 50%;
  top: 35%;
  transform: translate(-50%, -35%);
  padding: 52px 40px 32px;
}

.tenant-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  font-size: 14px;
}

.tenant-protocol {
  display: flex;
}

.language-select {
  display: flex;
}

.language-item {
  width: 70px;
  text-align: center;
  background: #f5f7fa;
  transform: skew(-15deg, 0deg);
  display: inline-block;
  height: 24px;
  cursor: pointer;

  .text-active {
    display: block;
    width: 70px;
    height: 24px;
    line-height: 24px;
    font-size: 12px;
    transform: skew(15deg, 0deg);
  }
}

.language-switcher {
  display: flex;
  border-radius: 2px;
  height: 24px;
  line-height: 24px;
  justify-content: end;
  text-align: right;
}

.active {
  background: #e1ecff;
  .text-active {
    color: #3a84ff;
  }
}

.main-content {
  height: 100%;
  background-color: #ebf2fa;
}

#particles-js {
  height: 100%;
}

.bg-img img {
  width: 100%;
}

.right-top {
  width: 52%;
  height: 0;
  position: absolute;
  right: 0;
  top: 0;
  padding-bottom: 10%;
  background-color: #ebf2fa;
}

.right-bottom {
  width: 31%;
  height: 0;
  position: absolute;
  right: 1%;
  bottom: 0;
  padding-bottom: 15%;
}

.left-bottom {
  width: 35%;
  height: 0;
  position: absolute;
  left: 0;
  bottom: 0;
  padding-bottom: 12%;
}

.footer {
  width: 100%;
  line-height: 20px;
  padding: 2% 0;
  position: absolute;
  bottom: 0;
  color: #bfcbd7;
  font-size: 12px;
  text-align: center;
  background: url(./images/footer.png) no-repeat center;
  background-size: 100% 100%;
}

.footer a {
  color: #bfcbd7;

  &:hover {
    color: #fff;
  }
}
:deep(.link-item ){
  color: #bfcbd7;
}
:deep(.link-item:hover) {
  color: #fff;
}
</style>

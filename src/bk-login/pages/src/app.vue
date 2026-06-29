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
          <bk-select
            v-model="activeTab"
            :clearable="false"
            :searchable="false"
            size="small"
            class="language-select"
            @change="handleSwitchLocale">
            <template #prefix>
              <div class="language-icon">
                <LanguageIcon :size="16" />
              </div>
            </template>
            <template #suffix>
              <DownShape :width="12" :height="12" />
            </template>
            <bk-option
              v-for="item in languageOptions"
              :key="item.value"
              :value="item.value"
              :label="item.label" />
          </bk-select>
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
import { onMounted, computed, ref, onBeforeMount } from 'vue';
import { getPlatformConfig, setShortcutIcon, setDocumentTitle } from '@blueking/platform-config';
import { platformConfig } from '@/store/platformConfig';
import Protocol from './views/components/protocol.vue';
import ProtocolEn from './views/components/protocol-en.vue';
import LanguageIcon from './views/components/language-icon.vue';
import I18n, { DEFAULT_LANGUAGE_OPTIONS, loadMessages } from '@/language/index';
import Cookies from 'js-cookie';
import { getGlobalSettings } from '@/http/api';
import { DownShape } from 'bkui-vue/lib/icon/index';

const platformConfigData = platformConfig();
const url = `${window.BK_SHARED_RES_URL}/bk_login/base.js`;  // url 远程配置文件地址
const defaults = {
  name: '登录',
  nameEn: 'Login',
  brandName: '蓝鲸智云',
  brandNameEn: 'BlueKing',
  version: '3.0',
};
const activeTab = ref(I18n.global.locale.value as string);
/** 语言选项（响应式） */
const languageOptions = ref([...DEFAULT_LANGUAGE_OPTIONS]);
/**
 * 用户协议是否显示
 */
const protocolVisible = ref(false);
const contact = computed(() => platformConfigData.i18n.footerInfoHTML);
const copyright = computed(() => platformConfigData.footerCopyrightContent);

const getConfigData = async () => {
  const config =  await getPlatformConfig(url, defaults);

  setShortcutIcon(config.favicon);
  setDocumentTitle(config.i18n);
  platformConfigData.update(config);
};

/** 初始化语言列表并预加载语言包 */
const initLanguages = async () => {
  try {
    const settings = await getGlobalSettings();
    if (settings?.supported_languages?.length > 0) {
      // 先加载非默认语言包，记录成功的语言
      const defaultCodes = new Set(DEFAULT_LANGUAGE_OPTIONS.map(opt => opt.value));
      const nonDefault = settings.supported_languages.filter(lang => !defaultCodes.has(lang.code));
      const loadResults = await Promise.all(nonDefault.map(lang => loadMessages(lang.code)));

      // 可用的语言 code 集合：默认语言 + 加载成功的非默认语言
      const availableCodes = new Set(DEFAULT_LANGUAGE_OPTIONS.map(opt => opt.value));
      nonDefault.forEach((lang, i) => {
        if (loadResults[i]) availableCodes.add(lang.code);
      });

      // 仅追加可用语言选项（去重）
      const existingCodes = new Set(languageOptions.value.map(opt => opt.value));
      settings.supported_languages.forEach(lang => {
        if (availableCodes.has(lang.code) && !existingCodes.has(lang.code)) {
          languageOptions.value.push({ value: lang.code, label: lang.name });
        }
      });
    }

    // 加载完语言包后，设置当前 locale 为 cookie 中的语言
    const cookieLang = Cookies.get('blueking_language') || 'zh-cn';
    if (cookieLang !== I18n.global.locale.value) {
      (I18n.global.locale as any).value = cookieLang;
      activeTab.value = cookieLang;
    }
  } catch (err) {
    console.warn('[i18n] Failed to fetch global settings', err);
  }
};

/**
 * 切换语言
 * @param lang 语言代码
 */
const handleSwitchLocale = (lang: string) => {
  activeTab.value = lang;
  // 因为未登录，所以改为后端直接调用接口
  // const api = `${window.BK_COMPONENT_API_URL}/api/c/compapi/v2/usermanage/fe_update_user_language/`;
  // const scriptId = 'jsonp-script';
  // const prevJsonpScript = document.getElementById(scriptId);
  // if (prevJsonpScript) {
  //   document.body.removeChild(prevJsonpScript);
  // }
  // const script = document.createElement('script');
  // script.type = 'text/javascript';
  // script.src = `${api}?language=${lang}`;
  // script.id = scriptId;
  // document.body.appendChild(script);

  Cookies.set('blueking_language', lang, {
    expires: 3600,
    path: '/',
    domain: window.BK_DOMAIN,
  });
  (I18n.global.locale as any).value = lang;
  document.querySelector('html')?.setAttribute('lang', lang);
  window.location.reload();
};

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

onBeforeMount(() => {
  getConfigData();
  initLanguages();
});
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
  align-items: center;
  width: 110px;
  
  .language-icon {
    display: flex;
    align-items: center;
    padding-left: 8px;
    color: #4D4F56;
    background-color: #F0F1F5;
  }

  :deep(.bk-input) {
    border: none;
    box-shadow: none !important;
    &.is-focused {
      box-shadow: none !important;
    }
    .bk-input--text { 
      background-color: #F0F1F5;
      color: #4D4F56;
    }
  }
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

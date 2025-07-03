<template>
  <div class="reset-wrapper">
    <div class="reset-box-content">
      <template v-if="!showEmailSend">
        <div class="reset-password-header">
          <p class="title">{{ $t('忘记密码') }}</p>
          <p class="subtitle">{{ tipsText }}</p>
        </div>
        <div class="reset-password-tab">
          <div
            class="tab-item"
            v-for="item in resetPasswordMethod"
            :key="item.value"
            @click="handleChangeMethod(item.value)">
            <span :class="activeMethod === item.value ? 'active' : ''">
              {{ item.label }}
            </span>
          </div>
          <Phone v-if="activeMethod === 'phone'" :tenant-id="tenantId" />
          <Email v-if="activeMethod === 'email'" :tenant-id="tenantId" @email-send="emailSend" />
        </div>
      </template>
      <template v-else>
        <EmailSent :current-email="currentEmail" @email-send="emailSend" />
      </template>
    </div>
    <div class="bg-img right-top">
      <img src="../../images/right-top.png" alt="">
    </div>
    <div class="bg-img right-bottom">
      <img src="../../images/right-bottom.png" alt="">
    </div>
    <div class="bg-img left-bottom">
      <img src="../../images/left-bottom.png" alt="">
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
            <span class="qr-box"><img class="qr" src="../../images/qr.png" alt=""></span>
          </template>
        </bk-popover>
      </p>
      <p>{{ copyright }}</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import { getPlatformConfig, setDocumentTitle, setShortcutIcon } from '@blueking/platform-config';

import Email from './emailForm.vue';
import EmailSent from './emailSent.vue';
import Phone from './phoneForm.vue';

import { t } from '@/language/index';
import { platformConfig } from '@/store/platformConfig';

const route = useRoute();

const tenantId = ref('');
const activeMethod = ref('phone');

watch(() => route.query.tenantId, (id: string) => {
  if (id) {
    tenantId.value = id;
  }
}, {
  immediate: true,
});

const tipsText = computed(() => (activeMethod.value === 'phone'
  ? t('请输入手机号以接收短信验证码')
  : t('请输入邮箱以接收邮件重置密码链接')));
const resetPasswordMethod = ref([
  {
    label: t('手机号'),
    value: 'phone',
  },
  {
    label: t('邮箱'),
    value: 'email',
  },
]);

const handleChangeMethod = (method: string) => {
  activeMethod.value = method;
};

const showEmailSend = ref(false);
const currentEmail = ref('');
const emailSend = (status: boolean, email: string) => {
  showEmailSend.value = status;
  currentEmail.value = email;
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
</script>

<style lang="less" scoped>
.reset-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 999;
  width: 100%;
  height: 100%;
  background: #fafbfd;
}

.reset-box-content {
  position: absolute;
  inset: 0;
  width: 480px;
  height: 474px;
  background: #FFF;
  border-radius: 10px;
  box-shadow: 0 4px 12px 0 #0003;
  position: absolute;
  left: 50%;
  top: 35%;
  transform: translate(-50%, -35%);
  padding: 52px 40px 32px;

  .reset-password-header {
    color: #313238;

    .title {
      height: 42px;
      margin-bottom: 32px;
      font-size: 32px;
      font-weight: 700;
    }

    .subtitle {
      margin-bottom: 24px;
      font-size: 20px;
      line-height: 28px;
      color: #313238;
    }
  }

  .reset-password-tab {
    width: 400px;
    margin-bottom: 24px;
    font-size: 14px;
    line-height: 22px;
    color: #63656E;
    white-space: nowrap;

    .tab-item {
      display: inline-block;
      width: 200px;
      margin-bottom: 34px;
      text-align: center;
      cursor: pointer;

      span {
        padding-bottom: 10px;

        &.active {
          font-size: 16px;
          font-weight: 700;
          color: #3A84FF;
          border-bottom: 2px solid #3A84FF;
        }
      }
    }
  }
}

#particles-js {
  background: #ebf2fa;
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
  background: url(../../images/footer.png) no-repeat center;
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


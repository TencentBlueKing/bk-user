<template>
  <div class="main-content">
    <canvas
      ref="dynamicBgRef"
      class="dynamic-bg"
      aria-hidden="true">
    </canvas>
    <div class="login-model">
      <router-view></router-view>
      <div class="tenant-footer">
        <div
          :style="{ visibility: activeTab === 'zh-cn' || activeTab === 'en' ? 'visible' : 'hidden' }"
          class="cursor-pointer tenant-protocol"
          @click="protocolVisible = true"
        >
          {{ $t('用户协议') }} >
        </div>
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
import { computed, onBeforeMount, onBeforeUnmount, onMounted, ref } from 'vue';
import { getPlatformConfig, setShortcutIcon, setDocumentTitle } from '@blueking/platform-config';
import { platformConfig } from '@/store/platformConfig';
import Protocol from './views/components/protocol.vue';
import ProtocolEn from './views/components/protocol-en.vue';
import LanguageIcon from './views/components/language-icon.vue';
import I18n, { DEFAULT_LANGUAGE_OPTIONS, loadMessages } from '@/language/index';
import Cookies from 'js-cookie';
import { getGlobalSettings } from '@/http/api';
import { DownShape } from 'bkui-vue/lib/icon/index';

interface DynamicPoint {
  baseX: number
  baseY: number
  driftX: number
  driftY: number
  phase: number
  radius: number
  speed: number
}

const dynamicBgRef = ref<HTMLCanvasElement | null>(null);
let cleanupDynamicBg: (() => void) | null = null;

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
    if (settings?.languages?.length > 0) {
      // 先加载非默认语言包，记录成功的语言
      const defaultCodes = new Set(DEFAULT_LANGUAGE_OPTIONS.map(opt => opt.value));
      const nonDefault = settings.languages.filter(lang => !defaultCodes.has(lang.code));
      const loadResults = await Promise.all(nonDefault.map(lang => loadMessages(lang.code)));

      // 可用的语言 code 集合：默认语言 + 加载成功的非默认语言
      const availableCodes = new Set(DEFAULT_LANGUAGE_OPTIONS.map(opt => opt.value));
      nonDefault.forEach((lang, i) => {
        if (loadResults[i]) availableCodes.add(lang.code);
      });

      // 仅追加可用语言选项（去重）
      const existingCodes = new Set(languageOptions.value.map(opt => opt.value));
      settings.languages.forEach(lang => {
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

/**
 * 初始化登录页动态背景
 * @param canvas 背景画布
 */
const initDynamicBackground = (canvas: HTMLCanvasElement) => {
  const targetCanvas = canvas;
  const ctx = targetCanvas.getContext('2d');
  if (!ctx) {
    return () => {};
  }

  let width = 0;
  let height = 0;
  let dpr = 1;
  let animationFrameId = 0;
  let startTime = 0;
  let points: DynamicPoint[] = [];
  // 统一控制背景动画速度，避免分散调整节点运动参数。
  const motionSpeedRatio = 6;

  const getPointCount = () => Math.max(36, Math.min(72, Math.round((width * height) / 26000)));

  /**
   * 创建分散在画布上的动态节点
   */
  const createPoints = () => Array.from({ length: getPointCount() }, () => ({
    baseX: Math.random() * width,
    baseY: Math.random() * height,
    driftX: 18 + Math.random() * 34,
    driftY: 14 + Math.random() * 28,
    phase: Math.random() * Math.PI * 2,
    radius: 1 + Math.random() * 1.4,
    speed: 0.11 + Math.random() * 0.2,
  }));

  const getPointPosition = (point: DynamicPoint, time: number) => ({
    x: point.baseX + Math.sin(time * point.speed + point.phase) * point.driftX,
    y: point.baseY + Math.cos(time * point.speed * 0.83 + point.phase) * point.driftY,
    radius: point.radius + Math.sin(time * point.speed * 1.7 + point.phase) * 0.25,
  });

  const drawBackground = () => {
    const baseGradient = ctx.createLinearGradient(0, 0, width, height);
    baseGradient.addColorStop(0, '#e4efff');
    baseGradient.addColorStop(0.36, '#f1f6ff');
    baseGradient.addColorStop(1, '#e8f0ff');
    ctx.fillStyle = baseGradient;
    ctx.fillRect(0, 0, width, height);

    const softGlow = ctx.createRadialGradient(width * 0.28, height * 0.16, 0, width * 0.28, height * 0.16, width * 0.72);
    softGlow.addColorStop(0, 'rgba(168, 200, 255, 0.42)');
    softGlow.addColorStop(1, 'rgba(232, 240, 255, 0)');
    ctx.fillStyle = softGlow;
    ctx.fillRect(0, 0, width, height);
  };

  const render = (timestamp: number) => {
    if (!startTime) {
      startTime = timestamp;
    }

    const elapsed = ((timestamp - startTime) / 1000) * motionSpeedRatio;
    const positions = points.map(point => getPointPosition(point, elapsed));
    const lineLimit = Math.max(128, Math.min(224, Math.min(width, height) * 0.24));

    ctx.clearRect(0, 0, width, height);
    drawBackground();

    // 节点之间按距离动态连线，形成类似 AI Studio 的轻量网格动效。
    ctx.lineWidth = 1;
    for (let index = 0; index < positions.length; index++) {
      for (let nextIndex = index + 1; nextIndex < positions.length; nextIndex++) {
        const current = positions[index];
        const next = positions[nextIndex];
        const distance = Math.hypot(current.x - next.x, current.y - next.y);

        if (distance < lineLimit) {
          const opacity = (1 - distance / lineLimit) * 0.18;
          ctx.strokeStyle = `rgba(91, 123, 214, ${opacity})`;
          ctx.beginPath();
          ctx.moveTo(current.x, current.y);
          ctx.lineTo(next.x, next.y);
          ctx.stroke();
        }
      }
    }

    positions.forEach((point, index) => {
      const opacity = 0.16 + (index % 5) * 0.018;
      ctx.fillStyle = `rgba(83, 111, 205, ${opacity})`;
      ctx.beginPath();
      ctx.arc(point.x, point.y, Math.max(0.8, point.radius), 0, Math.PI * 2);
      ctx.fill();
    });

    animationFrameId = requestAnimationFrame(render);
  };

  const resize = () => {
    const rect = targetCanvas.parentElement?.getBoundingClientRect() || targetCanvas.getBoundingClientRect();
    width = Math.max(1, rect.width);
    height = Math.max(1, rect.height);
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    targetCanvas.width = Math.ceil(width * dpr);
    targetCanvas.height = Math.ceil(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    points = createPoints();
  };

  const resizeObserver = new ResizeObserver(resize);
  if (targetCanvas.parentElement) {
    resizeObserver.observe(targetCanvas.parentElement);
  }

  resize();
  animationFrameId = requestAnimationFrame(render);

  return () => {
    cancelAnimationFrame(animationFrameId);
    resizeObserver.disconnect();
  };
};

onMounted(() => {
  if (dynamicBgRef.value) {
    cleanupDynamicBg = initDynamicBackground(dynamicBgRef.value);
  }
});

onBeforeMount(() => {
  getConfigData();
  initLanguages();
});

onBeforeUnmount(() => {
  cleanupDynamicBg?.();
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
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: #edf4ff;
}

.dynamic-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.footer {
  z-index: 1;
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

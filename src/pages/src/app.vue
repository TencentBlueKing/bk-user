<script setup lang="ts">
import { Message } from 'bkui-vue';
import en from 'bkui-vue/dist/locale/en.esm';
import zhCn from 'bkui-vue/dist/locale/zh-cn.esm';
import Cookies from 'js-cookie';
import { computed, onBeforeMount, ref } from 'vue';
import { NavigationGuardNext, RouteLocationNormalizedGeneric, useRouter } from 'vue-router';

import { getPlatformConfig, setDocumentTitle, setShortcutIcon } from '@blueking/platform-config';

import { ROLE } from './common/constant';
import { noNeedLoginRouteNames } from './router/routes';
import HeaderBox from './views/MainHeader.vue';

import { getSupportedLanguages } from '@/http/api';
import I18n, { DEFAULT_LANGUAGE_OPTIONS, loadMessages, locale as i18nLocal, t } from '@/language/index';
import { platformConfig, useUser } from '@/store';
import Password from '@/views/reset-password/index.vue';
import ResetPassword from '@/views/reset-password/newPassword.vue';

const router = useRouter();

const showName = ref(null);
/** 语言选项列表 */
const defaultLanguages = [...DEFAULT_LANGUAGE_OPTIONS];
const platformConfigData = platformConfig();

/** 获取后端允许的语言列表并预加载语言包 */
const fetchAllowedLanguages = async () => {
  const prefix = '[bk-user][i18n]';
  try {
    console.log(`${prefix} fetchAllowedLanguages 开始`);
    const res = await getSupportedLanguages();
    const supportedLanguages = res?.data || [];
    console.log(`${prefix} getSupportedLanguages 返回 data=`, supportedLanguages);
    if (supportedLanguages?.length > 0) {
      // 先加载非默认语言包，记录成功的语言
      const defaultCodes = new Set(DEFAULT_LANGUAGE_OPTIONS.map(opt => opt.value));
      console.log(`${prefix} 默认语言列表`, [...defaultCodes]);
      const nonDefault = supportedLanguages.filter(lang => !defaultCodes.has(lang.code));
      console.log(`${prefix} 需要动态加载的语言`, nonDefault.map(l => l.code));
      const loadResults = await Promise.all(nonDefault.map(lang => loadMessages(lang.code)));

      // 可用的语言 code 集合：默认语言 + 加载成功的非默认语言
      const availableCodes = new Set(DEFAULT_LANGUAGE_OPTIONS.map(opt => opt.value));
      nonDefault.forEach((lang, i) => {
        if (loadResults[i]) availableCodes.add(lang.code);
      });

      // 仅追加可用语言选项（去重）
      const existingCodes = new Set(defaultLanguages.map(opt => opt.value));
      supportedLanguages.forEach((lang) => {
        if (availableCodes.has(lang.code) && !existingCodes.has(lang.code)) {
          defaultLanguages.push({ value: lang.code, label: lang.name });
          console.log(`${prefix} 追加语言选项 code=${lang.code} label=${lang.name}`);
        }
      });
      console.log(`${prefix} 最终语言选项`, defaultLanguages);
    } else {
      console.log(`${prefix} 后端未返回支持的语言，使用默认语言选项`);
    }

    // 保存到 store，供 MainHeader 等组件使用
    platformConfigData.languageOptions = [...defaultLanguages];
    console.log(`${prefix} 已保存到 platformConfigData.languageOptions`);
    // 加载完语言包后，设置当前 locale 为 cookie 中的语言
    const cookieLang = Cookies.get('blueking_language') || 'zh-cn';
    console.log(`${prefix} cookie 语言=${cookieLang} 当前 locale=${I18n.global.locale.value}`);
    if (cookieLang !== I18n.global.locale.value) {
      (I18n.global.locale as any).value = cookieLang;
      console.log(`${prefix} locale 已切换为 ${cookieLang}`);
    }
  } catch (err) {
    console.warn(`${prefix} fetchAllowedLanguages 失败`, err);
  }
};

// 加载完用户数据才会展示页面
const isLoading = ref(true);
// 获取用户数据
const userStore = useUser();

const currentLang = ref(i18nLocal.value);
// 多语言注入, 此处引用组件库内置多语言配置
const localeData = {
  'zh-cn': zhCn,
  en,
};

const locale = computed(() => localeData[currentLang.value]);

const url = `${window.BK_SHARED_RES_URL}/bk_user/base.js`;  // url 远程配置文件地址
const defaults = {
  name: '用户管理',
  nameEn: 'User Management',
  productName: '蓝鲸用户管理',
  productNameEn: 'BK User Management',
  brandName: '蓝鲸智云',
  brandNameEn: 'Tencent BlueKing',
  version: '3.0',
};

const getConfigData = async () => {
  const config =  await getPlatformConfig(url, defaults);
  setShortcutIcon(config.favicon); // 设置favicon
  setDocumentTitle(config.i18n); // 设置document.title
  platformConfigData.update(config);
};

/**
 * 检查用户角色权限并在需要时重定向
 * @returns true 表示已重定向，调用方无需再调用 next()
 */
const handleRoleRedirect = (to: RouteLocationNormalizedGeneric, next: NavigationGuardNext) => {
  const { role } = userStore.user;
  const isSingleTenantMode = window.ENABLE_MULTI_TENANT_MODE === 'False';

  // 普通用户只能访问个人中心
  if (role === ROLE.NATURAL_USER && to.name !== 'personalCenter') {
    next({ name: 'personalCenter' });
    return true;
  }

  // 租户管理员或单租户模式下，不能访问租户管理页
  if ((role === ROLE.TENANT_MANAGER || isSingleTenantMode) && to.name === 'tenant') {
    next({ name: 'organization' });
    return true;
  }

  return false;
};

router.beforeEach(async (to, from, next) => {
  if (noNeedLoginRouteNames.includes(to.name as string)) {
    next();
    isLoading.value = false;
    return;
  }

  // 已登录用户，检查角色权限
  if (userStore.user.username) {
    const redirected = handleRoleRedirect(to, next);
    isLoading.value = false;
    if (!redirected) {
      next();
    }
    return;
  }

  // 未登录用户，初始化用户信息
  try {
    await userStore.initUserInfo();
    const redirected = handleRoleRedirect(to, next);
    isLoading.value = false;
    if (!redirected) {
      next();
    }
    return;
  } catch (err) {
    Message(t('获取用户信息失败，请检查后再试'));
    next();
    isLoading.value = false;
  }
});

onBeforeMount(() => {
  getConfigData();
  fetchAllowedLanguages();
});
</script>

<template>
  <div>
    <bk-config-provider :locale="locale">
      <Password v-if="showName === 'password'" />
      <ResetPassword v-else-if="showName === 'resetPassword'" />
      <bk-loading
        v-else
        :loading="isLoading"
        :class="{
          'main-loading': isLoading
        }"
      >
        <HeaderBox v-if="!isLoading" />
      </bk-loading>
    </bk-config-provider>
  </div>
</template>

<style lang="less" scoped>
  .main-loading {
    margin-top: 25vw;
  }
</style>

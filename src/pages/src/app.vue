<script setup lang="ts">
import { Message } from 'bkui-vue';
import en from 'bkui-vue/dist/locale/en.esm';
import zhCn from 'bkui-vue/dist/locale/zh-cn.esm';
import { computed, ref } from 'vue';
import { NavigationGuardNext, RouteLocationNormalizedGeneric, useRouter } from 'vue-router';

import { getPlatformConfig, setDocumentTitle, setShortcutIcon } from '@blueking/platform-config';

import { ROLE } from './common/constant';
import { noNeedLoginRouteNames } from './router/routes';
import HeaderBox from './views/MainHeader.vue';

import { locale as i18nLocal, t } from '@/language/index';
import { platformConfig, useUser } from '@/store';
import Password from '@/views/reset-password/index.vue';
import ResetPassword from '@/views/reset-password/newPassword.vue';

const router = useRouter();

const showName = ref(null);

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

const platformConfigData = platformConfig();
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
getConfigData();

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

  // 内置管理员或单租户模式下，不能访问租户管理页
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

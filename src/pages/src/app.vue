<script setup lang="ts">
import { Message } from 'bkui-vue';
import en from 'bkui-vue/dist/locale/en.esm';
import zhCn from 'bkui-vue/dist/locale/zh-cn.esm';
import { computed, nextTick, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import BkUserDisplayName from '@blueking/bk-user-display-name';
import { getPlatformConfig, setDocumentTitle, setShortcutIcon } from '@blueking/platform-config';

import { IUser } from './types/store';
import HeaderBox from './views/MainHeader.vue';

import { currentUser, getBuiltinManager } from '@/http';
import { locale as i18nLocal, t } from '@/language/index';
import { routes } from '@/router/routes';
import { platformConfig, useUser } from '@/store';
import Password from '@/views/reset-password/index.vue';
import ResetPassword from '@/views/reset-password/newPassword.vue';

const route = useRoute();
const router = useRouter();

const showName = ref(null);

// 加载完用户数据才会展示页面
const isLoading = ref(true);
// 获取用户数据
const user = useUser();

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


// 判断是否是重置密码的路由
watch(() => route.name, (val) => {
  const filterRoutes = [
    'password',
    'resetPassword',
    'bindResult',
  ];
  if (filterRoutes.includes(val as string)) {
    isLoading.value = false;
    return;
  }

  // 先检查store中是否已有用户信息
  if (user.user.username) {
    isLoading.value = false;
    return;
  }

  currentUser()
    .then(async (res) => {
      const { data } = res as { data: IUser };
      user.setUser(data);
      BkUserDisplayName.configure({
        tenantId: data.tenant_id,
        apiBaseUrl: window.BK_USER_WEB_APIGW_URL,
      });
      // 角色为租户管理员或超级管理员时
      if (data.role === 'super_manager' || data.role === 'tenant_manager') {
        const managerData = await getBuiltinManager();
        if (managerData?.data) {
          user.admin = managerData?.data;
        }
      }
      if (data.role === 'natural_user') {
        // 普通用户直接跳转到个人中心
        router.replace({ name: 'personalCenter' }).finally(() => {
          isLoading.value = false;
        });
      } else {
        // 如果不是普通用户，添加管理员路由
        const managerRoutes = routes.filter(route => route.meta?.manager === true);
        managerRoutes.forEach(route => {
          router.addRoute(route);
        });
        // 等待路由添加完成后再结束 loading
        nextTick(() => {
          // 使用 router.resolve 检查当前路径是否能匹配到路由
          const resolved = router.resolve(route.fullPath);
          // 如果之前是 404，现在能匹配到了，就重新导航
          if (route.name === 'notFound' && resolved.name !== 'notFound') {
            router.replace(route.fullPath).finally(() => {
              isLoading.value = false;
            });
          } else {
            isLoading.value = false;
          }
        });
      }
    })
    .catch(() => {
      Message(t('获取用户信息失败，请检查后再试'));
      isLoading.value = false;
    });
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

<template>
  <MainView>
    <template #menu>
      <bk-menu
        :active-key="activeKey"
        :collapse="menuStore.collapsed"
        @click="handleChangeMenu"
        @mouseenter="menuStore.mouseenter"
        @mouseleave="menuStore.mouseleave">
        <div class="main-menu__list user-scroll-y">
          <bk-menu-group v-for="menu in menuData" :key="menu.key" :name="menu.name">
            <bk-menu-item
              v-for="item in menu.children"
              :key="item.key">
              <template #icon>
                <i :class="`user-icon ${item.icon}`" />
              </template>
              {{ item.name }}
            </bk-menu-item>
          </bk-menu-group>
        </div>
        <div
          class="main-menu__toggle"
          @click="menuStore.toggle">
          <i
            class="user-icon icon-arrow-right main-menu__icon"
            :class="[{
              'main-menu__icon--active': menuStore.toggleCollapsed
            }]" />
        </div>
      </bk-menu>
    </template>
  </MainView>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import MainView from '@/components/layouts/MainView.vue';
import { useMenuInfo } from '@/hooks';
import { t } from '@/language/index';
import { useMenu } from '@/store';

const route = useRoute();
const router = useRouter();
const menuStore = useMenu();
const { activeKey, handleChangeMenu } = useMenuInfo();

const menuData = reactive([
  {
    name: t('管理'),
    key: 'manage',
    children: [
      {
        name: t('管理员配置'),
        key: 'admin',
        icon: 'icon-guanliyuan',
      },
      {
        name: t('数据源配置'),
        key: 'dataSource',
        icon: 'icon-shujuyuanshu',
      },
    ],
  },
  {
    name: t('协作'),
    key: 'collaboration',
    children: [
      {
        name: t('跨租户协同'),
        key: 'collaboration',
        icon: 'icon-tongbu-2',
      },
    ],
  },
  {
    name: t('登录'),
    key: 'login',
    children: [
      {
        name: t('登录设置'),
        key: 'login',
        icon: 'icon-yonghushu',
      },
      {
        name: t('账号设置'),
        key: 'account',
        icon: 'icon-zhanghaoshu',
      },
      // {
      //   name: t('MFA 设置'),
      //   key: 'fma',
      //   icon: 'icon-renzheng'
      // },
    ],
  },
  {
    name: t('其他'),
    key: 'other',
    children: [
      {
        name: t('字段设置'),
        key: 'field',
        icon: 'icon-field',
      },
      {
        name: t('基础设置'),
        key: 'basics',
        icon: 'icon-basic',
      },
    ],
  },
]);

// 递归查找并移除子菜单项
const removeMenuItem = (menuList: any[], targetKey: string) => {
  for (let i = 0; i < menuList.length; i++) {
    const menu = menuList[i];
    // 检查当前菜单项
    if (menu.key === targetKey) {
      menuList.splice(i, 1);
      return true;
    }
    // 检查子菜单
    if (menu.children) {
      if (removeMenuItem(menu.children, targetKey)) {
        // 如果子菜单被清空，移除父菜单
        if (menu.children.length === 0) {
          menuList.splice(i, 1);
        }
        return true;
      }
    }
  }
  return false;
};

onMounted(() => {
  const filterList = {
    // 协同租户
    ENABLE_COLLABORATION_TENANT: 'collaboration',
    // 是否支持多租户
    ENABLE_MULTI_TENANT_MODE: 'other.basics',
  };

  Object.entries(filterList).forEach(([key, path]) => {
    if (window?.[key] === 'False') {
      const keys = path.split('.');
      // 处理菜单移除
      if (keys.length === 1) {
        // 顶级菜单
        removeMenuItem(menuData, keys[0]);
      } else {
        // 嵌套子菜单 (如 'other.basics')
        removeMenuItem(menuData, keys[keys.length - 1]);
      }

      const routeKey = keys[keys.length - 1]; // 使用最后一级作为路由key
      // 路由移除
      if (router.hasRoute(routeKey)) {
        router.removeRoute(routeKey);

        if (route.name === routeKey) {
          router.push('/setting');
        }
      }
    }
  });
});

</script>

<style lang="less" scoped>
@import url("@/css/menuStyle.less");
</style>

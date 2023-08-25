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
          <bk-menu-item
            v-for="item in menuData"
            :key="item.key">
            <template #icon>
              <i class="user-icon icon-qingximoban" />
            </template>
            {{ item.name }}
          </bk-menu-item>
        </div>
        <div
          class="main-menu__toggle"
          @click="menuStore.toggle">
          <i
            class="user-icon icon-arrow-left main-menu__icon"
            :class="[{
              'main-menu__icon--active': menuStore.toggleCollapsed
            }]" />
        </div>
      </bk-menu>
    </template>
  </MainView>
</template>

<script setup lang="ts">
import { reactive } from 'vue';

import MainView from '@/components/layouts/MainView.vue';
import { useMenuInfo } from '@/hooks/useMenuInfo';
import { useMenu } from '@/store/useMenu';

const menuStore = useMenu();
const { activeKey, handleChangeMenu } = useMenuInfo();

const menuData = reactive([
  {
    name: '集团概览',
    key: 'tenantInfo',
  },
  // {
  //   name: '全局设置',
  //   key: 'globalSetting',
  // },
]);
</script>

<style lang="less" scoped>
@import url("@/css/menuStyle.less");
</style>

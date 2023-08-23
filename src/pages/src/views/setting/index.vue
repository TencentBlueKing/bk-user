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

<script setup lang="tsx">
import { reactive } from 'vue';

import { useMenuInfo } from '../../hooks/useMenuInfo';

import MainView from '@/components/layouts/MainView.vue';
import { useMenu } from '@/store/useMenu';

const menuStore = useMenu();
const { activeKey, handleChangeMenu } = useMenuInfo();

const menuData = reactive([
  {
    name: '用户字段设置',
    key: 'userFields',
  },
  {
    name: '登录设置',
    key: 'login',
  },
]);

</script>

<style lang="less" scoped>
@import url("../../css/menuStyle.less");
</style>

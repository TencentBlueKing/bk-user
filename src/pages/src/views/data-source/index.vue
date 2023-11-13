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
    name: '数据源管理',
    key: 'local',
  },
  // {
  //   name: '跨租户协同',
  //   key: 'crossCompany',
  // },
]);
</script>

<style lang="less" scoped>
@import url("../../css/menuStyle.less");

:deep(.main-breadcrumbs) {
  box-shadow: none;
}

:deep(.tab-details) {
  height: calc(100vh - 104px);

  .bk-tab-header {
    font-size: 14px;
    line-height: 36px !important;
    background: #fff;
    border-bottom: none;
    box-shadow: 0 3px 4px 0 rgb(0 0 0 / 4%);

    .bk-tab-header-item {
      padding: 0 5px !important;
      margin: 0 20px;
    }
  }

  .bk-tab-content {
    padding: 0;
  }
}
</style>

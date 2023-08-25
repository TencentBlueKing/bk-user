<template>
  <div class="main-container">
    <div
      class="main-menu"
      :class="[{ 'main-menu--collapsed': menuStore.toggleCollapsed }]">
      <slot name="menu" />
    </div>
    <div class="main-container-content">
      <MainBreadcrumbs
        v-if="!mainViewStore.customBreadcrumbs"
        class="main-container__breadcrumbs" />
      <slot name="main-content">
        <div
          class="main-container__view user-scroll-y user-scroll-x"
          :class="[{
            'pd-24': mainViewStore.hasPadding,
            'has-breadcrumbs': !mainViewStore.customBreadcrumbs
          }]">
          <RouterView />
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import MainBreadcrumbs from './MainBreadcrumbs.vue';

import { useMainViewStore } from '@/store/mainView';
import { useMenu } from '@/store/useMenu';

const menuStore = useMenu();
const mainViewStore = useMainViewStore();
</script>

<style lang="less">
.main-container {
  display: flex;
  height: calc(100vh - 52px);
}

.main-container-content {
  position: relative;
  width: 0;
  height: 100%;
  min-width: 940px;
  flex: 1;
}

.main-container__view {
  height: 100%;
  background-color: #f5f7fa;

  &.has-breadcrumbs {
    height: calc(100% - 52px);
  }
}

.main-menu {
  position: relative;
  z-index: 101;
  height: 100%;
  background-color: #fff;
  flex-shrink: 0;

  &--collapsed {
    width: 60px;
  }

  .bk-menu {
    height: 100%;

    .submenu-header {
      flex-shrink: 0;
    }
  }

  &__list {
    height: calc(100vh - 108px);
    padding: 12px 0 4px;

    &.user-scroll-y {
      &::-webkit-scrollbar-thumb {
        background-color: #515560;
        border-radius: 4px;
      }

      &:hover {
        &::-webkit-scrollbar-thumb {
          background-color: #515560;
        }
      }
    }
  }

  &__toggle {
    display: flex;
    align-items: center;
    width: 60px;
    height: 56px;
    padding-left: 14px;
    color: #96a2b9;
  }

  &__icon {
    display: flex;
    align-items: center;
    width: 32px;
    height: 32px;
    font-size: 16px;
    cursor: pointer;
    border-radius: 50%;
    transform: rotate(180deg);
    transition: all 0.2s;
    justify-content: center;

    &:hover {
      color: #3a84ff;
      background: linear-gradient(270deg, #e1ecff, #e1ecff);
    }

    &--active {
      transform: rotate(0);
    }
  }
}
</style>

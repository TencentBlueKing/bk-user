<template>
  <div class="main-breadcrumbs">
    <slot>
      <i
        v-if="showBack"
        class="user-icon icon-arrow-left main-breadcrumbs__back"
        @click="handleBack" />
      <span class="main-breadcrumbs__current">
        <span>{{ current }}</span>
      </span>
    </slot>
    <slot name="append" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { useMainViewStore } from '@/store/mainView';

const store = useMainViewStore();
const route = useRoute();
const router = useRouter();

/**
 * 当前面包屑展示文案
 */
const current = computed(() => store.breadCrumbsTitle || route.meta.navName);
/**
 * back control
 */
const showBack = computed(() => route.meta.showBack);
const handleBack = () => {
  const { back } = window.history.state;
  if (back) {
    router.go(-1);
  } else {
    const { matched } = route;
    const count = matched.length;
    if (count > 1) {
      const backRoute = matched[count - 1];
      router.push({ name: backRoute.meta.activeMenu });
    }
  }
};
</script>

<style lang="less" scoped>
  .main-breadcrumbs {
    position: relative;
    z-index: 11;
    display: flex;
    width: 100%;
    height: 52px;
    padding: 0 24px;
    background-color: #fff;
    box-shadow: 0 3px 4px 0 rgb(0 0 0 / 4%);
    align-items: center;

    &__back {
      margin-right: 10px;
      font-size: 18px;
      color: #3a84ff;
      cursor: pointer;
    }

    &__current {
      margin-right: 8px;
      font-size: 16px;
      color: #323138;
    }

    .bk-tag {
      margin-right: 4px;
    }
  }
</style>

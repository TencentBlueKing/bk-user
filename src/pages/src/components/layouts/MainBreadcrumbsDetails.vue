<template>
  <div class="main-breadcrumbs-details">
    <slot>
      <div class="main-breadcrumbs__left">
        <i
          class="user-icon icon-arrow-left main-breadcrumbs__back"
          @click="handleBack" />
        <span class="main-breadcrumbs__current">
          <span class="tittle">{{ current }}</span>
          <span class="subtitle" v-if="subtitle">
            &nbsp;-&nbsp;
            {{ subtitle }}
          </span>
        </span>
        <slot name="tag" />
      </div>
      <slot name="content" />
      <slot name="right" />
    </slot>
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { useMainViewStore } from '@/store/mainView';

defineProps({
  subtitle: {
    type: String,
    default: '',
  },
});

const store = useMainViewStore();
const route = useRoute();
const router = useRouter();
store.customBreadcrumbs = true;
/**
 * 当前面包屑展示文案
 */
const current = computed(() => store.breadCrumbsTitle || route.meta.navName);
/**
 * back control
 */
const handleBack = () => {
  const { back } = window.history.state;
  if (back) {
    router.go(-1);
    store.customBreadcrumbs = false;
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

<style lang="less">
.main-breadcrumbs-details {
  position: relative;
  z-index: 11;
  display: flex;
  width: 100%;
  height: 52px;
  padding: 0 24px;
  background-color: #fff;
  box-shadow: 0 3px 4px 0 rgb(0 0 0 / 4%);
  align-items: center;
  justify-content: space-between;

  &__back {
    margin-right: 10px;
    font-size: 18px;
    color: #3a84ff;
    cursor: pointer;
  }

  &__current {
    margin-right: 8px;
    font-size: 16px;
    color: #313238;

    .subtitle {
      font-size: 14px;
      color: #63656E;
    }
  }

  .bk-tag {
    margin-right: 4px;
  }
}
</style>

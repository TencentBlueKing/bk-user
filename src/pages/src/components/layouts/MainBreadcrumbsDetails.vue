<template>
  <div class="main-breadcrumbs-details">
    <slot>
      <div class="main-breadcrumbs-left">
        <i
          class="user-icon icon-arrow-left main-breadcrumbs-back"
          @click="handleBack" />
        <span class="main-breadcrumbs-current">
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
  router.push({ name: 'dataSource' });
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

  .main-breadcrumbs-left {
    display: flex;
    align-items: center;
  }

  .main-breadcrumbs-back {
    margin-right: 10px;
    font-size: 18px;
    color: #3a84ff;
    cursor: pointer;
  }

  .main-breadcrumbs-current {
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
    vertical-align: middle;
  }
}
</style>

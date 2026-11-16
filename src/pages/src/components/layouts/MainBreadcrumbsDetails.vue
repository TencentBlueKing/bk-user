<template>
  <div class="main-breadcrumbs-details">
    <slot>
      <div class="main-breadcrumbs-left">
        <i
          v-if="showBack"
          class="user-icon icon-arrow-left main-breadcrumbs-back"
          @click="handleBack" />
        <span class="main-breadcrumbs-current">
          <span class="tittle">{{ current }}</span>
          <span class="subtitle" v-if="subtitle">
            &nbsp;-&nbsp;
            {{ subtitle }}
          </span>
        </span>
      </div>
      <slot name="right" />
    </slot>
  </div>
</template>

<script setup lang="ts">
import { computed, defineEmits, defineProps } from 'vue';
import { useRoute } from 'vue-router';

import { useMainViewStore } from '@/store';

const props = defineProps({
  /** 页面自定的面包屑标题，传了就不再跟随路由级标题 */
  title: {
    type: String,
    default: '',
  },
  subtitle: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['toBack']);

const store = useMainViewStore();
const route = useRoute();
store.customBreadcrumbs = true;
/**
 * 当前面包屑展示文案
 */
const current = computed(() => props.title || store.breadCrumbsTitle || route.meta.navName);
const showBack = computed(() => route.meta.showBack);
/**
 * back control
 */
const handleBack = () => {
  emit('toBack');
};
</script>

<style lang="less">
.main-breadcrumbs-details {
  position: relative;
  z-index: 11;
  display: flex;
  width: 100%;
  height: var(--breadcrumbs-height);
  padding: 0 24px;
  background-color: #fff;
  box-shadow: 0 3px 4px 0 rgb(0 0 0 / 4%);
  align-items: center;
  justify-content: space-between;

  .main-breadcrumbs-left {
    display: flex;
    align-items: center;
    width: 100%;
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

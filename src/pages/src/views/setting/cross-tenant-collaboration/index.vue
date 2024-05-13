<template>
  <bk-tab
    class="tab-wrapper"
    v-model:active="active"
    type="unborder-card"
  >
    <bk-tab-panel
      v-for="item in panels"
      :key="item.name"
      :name="item.name"
      :label="item.label"
    >
      <component :is="item.component" :active="active"></component>
    </bk-tab-panel>
  </bk-tab>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref } from 'vue';

import { t } from '@/language/index';
import { useMainViewStore } from '@/store';

const MyShare = defineAsyncComponent(() => import('./my-share/index.vue'));
const OtherShare = defineAsyncComponent(() => import('./other-share/index.vue'));

const store = useMainViewStore();
store.customBreadcrumbs = false;

const panels = [
  { name: 'local', label: t('我分享的'), component: MyShare },
  { name: 'other', label: t('其他租户分享的'), component: OtherShare },
];
const active = ref('local');
</script>

<style lang="less" scoped>
.tab-wrapper {
  :deep(.bk-tab-header) {
    padding-left: 24px;
    font-size: 14px;
    line-height: 36px !important;
    background: #fff;
    border-bottom: none;
    box-shadow: 0 3px 4px 0 rgb(0 0 0 / 4%);
  }

  :deep(.bk-tab-content) {
    padding: 0;
  }
}
</style>

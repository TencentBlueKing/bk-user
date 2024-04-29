<template>
  <bk-tab
    class="tab-wrapper"
    v-model:active="active"
    type="unborder-card"
  >
    <bk-tab-panel
      v-for="(item, index) in panels"
      :key="index"
      :name="item.name"
      :label="item.label"
    >
      <MyShare v-if="active === 'local'" />
      <OtherShare v-else />
    </bk-tab-panel>
  </bk-tab>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import MyShare from './my-share/index.vue';
import OtherShare from './other-share/index.vue';

import { t } from '@/language/index';
import { useMainViewStore } from '@/store';

const store = useMainViewStore();
store.customBreadcrumbs = false;

const panels = [
  { name: 'local', label: t('我分享的') },
  { name: 'other', label: t('其他租户分享的') },
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

<template>
  <div>
    <div
      class="details-content-item"
      v-for="(item, index) in extras"
      :key="index">
      <span class="details-content-key">{{ item.display_name }}：</span>
      <bk-overflow-title class="details-content-value" type="tips">
        {{ customFieldsMap(item) }}
      </bk-overflow-title>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

import { customFieldsMap } from '@/utils';

defineProps({
  extras: {
    type: Array,
    default: () => ([]),
  },
});
</script>

<style lang="less" scoped>
@import url("@/css/viewUser.less");
</style>


<template>
  <div>
    <div
      class="details-content-item"
      v-for="(item, index) in extras"
      :key="index">
      <bk-overflow-title class="details-content-key" type="tips">{{ item.display_name }}：</bk-overflow-title>
      <bk-overflow-title class="details-content-value" type="tips">
        {{ customFieldsMap(item) || '--' }}
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
<style  lang="less">
.details-content-key, .details-content-value {
  .text-ov {
    font-size: 14px;
  }
}
</style>


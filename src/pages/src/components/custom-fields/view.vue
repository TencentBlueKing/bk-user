<template>
  <div>
    <div
      class="details-content-item"
      v-for="(item, index) in extras"
      :key="index">
      <span class="details-content-key">{{ item.display_name }}：</span>
      <bk-overflow-title class="details-content-value" type="tips">
        {{ ConvertVal(item) }}
      </bk-overflow-title>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref } from 'vue';

defineProps({
  extras: {
    type: Array,
    default: () => ([]),
  },
});

const ConvertVal = (item: any) => {
  return item.value === '' ? '--' : (item.data_type === 'multi_enum' ? item.value?.join(' ; ') : item.value);
};
</script>

<style lang="less" scoped>
@import url("@/css/viewUser.less");
</style>


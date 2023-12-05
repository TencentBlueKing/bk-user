<template>
  <div>
    <div
      class="details-content-item"
      v-for="(item, index) in extras"
      :key="index">
      <span class="details-content-key">{{ item.key }}：</span>
      <span class="details-content-value">{{ ConvertVal(item.value) }}</span>
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

const ConvertVal = (val: any) => {
  const demo = ref('');
  if (val instanceof Array) {
    demo.value = val?.map(item => item.value).join('；') || '--';
  } else {
    demo.value = val || '--';
  }
  return demo.value;
};
</script>

<style lang="less" scoped>
@import url("@/css/viewUser.less");
</style>


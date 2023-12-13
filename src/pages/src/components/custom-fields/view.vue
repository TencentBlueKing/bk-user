<template>
  <div>
    <div
      class="details-content-item"
      v-for="(item, index) in extras"
      :key="index">
      <span class="details-content-key">{{ item.displayName }}：</span>
      <span class="details-content-value">{{ ConvertVal(item) }}</span>
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
  const demo = ref('');
  if (item.type === 'multi_enum') {
    demo.value = item.value?.map(k => k.value).join('；') || '--';
  } else if (item.type === 'number') {
    demo.value = item.value;
  } else {
    demo.value = item.value || '--';
  }
  return demo.value;
};
</script>

<style lang="less" scoped>
@import url("@/css/viewUser.less");
</style>


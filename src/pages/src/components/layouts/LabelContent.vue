<template>
  <span class="label-content">
    <span class="label-key">{{ `${label ? label + '：' : ''}` }} </span>
    <span class="label-value">
      <slot></slot>
    </span>
  </span>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

defineProps({
  label: {
    type: String,
    required: true,
  },
});
</script>

<style lang="less" scoped>
.label-content {
  display: flex;
  font-size: 14px;
  line-height: 40px;
  align-content: center;

  .label-key {
    width: 98px;
    color: #63656E;
    text-align: right;
  }

  .label-value {
    flex: 1;
    color: #313238;
  }
}
</style>

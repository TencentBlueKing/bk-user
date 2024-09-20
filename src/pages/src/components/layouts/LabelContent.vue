<template>
  <span class="label-content">
    <bk-overflow-title type="tips" :class="['label-key', { 'label-key-en': $i18n.locale === 'en' }]">
      {{ `${label ? label + '：' : ''}` }}
    </bk-overflow-title>
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
    overflow: hidden;
    color: #63656E;
    text-align: right;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .label-key-en {
    width: 150px !important;
  }

  .label-value {
    flex: 1;
    color: #313238;
  }
}
</style>

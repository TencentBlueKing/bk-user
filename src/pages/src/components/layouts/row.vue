<template>
  <div class="row-wrapper">
    <header>
      <p>{{ title }}</p>
      <slot name="header"></slot>
    </header>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

defineProps({
  title: {
    type: String,
    required: true,
  },
});
</script>

<style lang="less" scoped>
.row-wrapper {
  padding: 0 24px 8px;
  margin-bottom: 16px;
  background: #FFF;
  border-radius: 2px;
  box-shadow: 0 2px 4px 0 #1919290d;

  header {
    display: flex;
    align-items: center;

    p {
      margin: 16px 0;
      font-size: 14px;
      font-weight: 700;
      line-height: 22px;
      color: #63656E;
    }
  }
}
</style>

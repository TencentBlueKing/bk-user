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
  margin-bottom: 24px;

  header {
    display: flex;
    place-content: center space-between;

    p {
      margin-bottom: 16px;
      font-size: 14px;
      font-weight: 700;
      line-height: 22px;
      color: #63656E;
    }
  }
}
</style>

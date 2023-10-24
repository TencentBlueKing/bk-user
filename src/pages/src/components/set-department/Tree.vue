<template>
  <bk-tree
    ref="treeRef"
    :data="treeData"
    node-key="id"
    label="name"
    children="children"
    :node-content-action="['selected', 'expand', 'click', 'collapse']"
  >
    <template #nodeAction="item">
      <span style="color: #979ba5;">
        <DownShape class="h-[34px] mt-[4px]" v-if="item.has_children && item.__attr__.isOpen" />
        <RightShape class="h-[34px] mt-[4px]" v-if="item.has_children && !item.__attr__.isOpen" />
      </span>
    </template>
    <template #nodeType="item">
      <i
        class="user-icon icon-homepage"
        v-if="item.__attr__.isRoot"
      />
      <i class="bk-sq-icon icon-file-close" v-else />
    </template>
    <template #node="item">
      <span v-overflow-title>{{ item.name }}</span>
    </template>
  </bk-tree>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

defineProps({
  treeData: {
    type: Array,
    default: () => ([]),
  },
});
</script>

<style>

</style>

<template>
  <div>
    <div
      class="leading-[36px] text-[14px] px-[6px] inline-flex items-center w-full cursor-pointer"
    >
      <img v-if="appStore.currentOrg?.logo" class="w-[20px] h-[20px] mr-[8px]" :src="appStore.currentOrg?.logo" />
      <span
        v-else
        class="bg-[#C4C6CC] text-white mr-[8px] rounded-[4px] inline-block w-[20px] leading-[20px] text-center"
      >
        {{ appStore.currentOrg?.tenant_name?.charAt(0).toUpperCase() }}
      </span>
      {{ appStore.currentOrg?.tenant_name }}
    </div>
    <bk-tree
      :data="treeData"
      :expand-all="true"
      label="name"
      node-key="id"
      children="children"
      :prefix-icon="getPrefixIcon"
    >
    </bk-tree>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import useAppStore from '@/store/app';

const appStore = useAppStore();

/**
 * 根据organization_path转化为树结构
 */
const treeData = computed(() => {
  const orgs = appStore.currentOrg.organization_path || '';
  let root = null;
  let currentParent = null;
  orgs.split('/').forEach((item) => {
    const node = {
      id: appStore.currentOrg.name === item ? appStore.currentOrg.id : item,
      name: item,
      children: [],
    };
    if (!root) {
      root = node;
    } else {
      currentParent.children.push(node);
    }
    currentParent = node;
  });
  return [root];
});

const getPrefixIcon = (item: { children?: any[] }, renderType: string) => {
  if (renderType === 'node_action') {
    return 'default';
  }

  return {
    node: 'span',
    className: 'bk-sq-icon icon-file-close pr-1',
    style: {
      color: '#A3C5FD',
    },
  };
};
</script>

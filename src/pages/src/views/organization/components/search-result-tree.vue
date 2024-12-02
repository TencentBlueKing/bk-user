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
      label="name"
      node-key="id"
      children="children"
      :prefix-icon="getPrefixIcon"
      :async="{
        callback: getRemoteData,
        cache: true,
      }"
    >
    </bk-tree>
  </div>
</template>

<script setup lang="ts">
import { defineExpose, ref } from 'vue';

import { getDepartmentsList } from '@/http/organizationFiles';
import useAppStore from '@/store/app';

const appStore = useAppStore();

/**
 * 根据organization_path转化为树结构
 */
const getData =  (isChildren) => {
  const orgs = appStore.currentOrg.organization_path || '';
  let root = null;
  let currentParent = null;
  orgs.split('/').forEach((item) => {
    const node = {
      id: appStore.currentOrg.name === item ? appStore.currentOrg.id : item,
      name: item,
      children: [],
      async: isChildren,
      isOpen: appStore.currentOrg.name !== item,
    };
    if (!root) {
      root = node;
    } else {
      currentParent.children.push(node);
    }
    currentParent = node;
  });
  return [root];
};

const treeData = ref([]);

const getTreeData = async () => {
  const { data = [] } = await getDepartmentsList(appStore.currentOrg.id, appStore.currentOrg.tenant_id);
  treeData.value = getData(Boolean(data?.length));
};

const formatTreeData = (data = []) => data.map(item => ({ ...item, async: item.has_children }));

const getRemoteData = async (item: IOrg) => {
  const res = await getDepartmentsList(item.id, appStore.currentTenant.id);
  return formatTreeData(res?.data);
};

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

defineExpose({
  getTreeData,
});
</script>

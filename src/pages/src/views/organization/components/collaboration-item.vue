<template>
  <div class="">
    <div
      class="leading-[36px] text-[14px] px-[6px] inline-flex items-center w-full cursor-pointer"
      :class="{ 'text-[#3A84FF] bg-[#ebf2ff]': appStore.currentOrg?.id === tenant?.id }"
      @click="handleNodeClick(tenant)"
    >
      <img v-if="tenant?.logo" class="w-[20px] h-[20px] mr-[8px]" :src="tenant?.logo" />
      <span
        v-else
        class="bg-[#C4C6CC] text-white mr-[8px] rounded-[4px] inline-block w-[20px] leading-[20px] text-center"
        :class="{ 'bg-[#3A84FF]': appStore.currentOrg?.id === tenant?.id }"
      >
        {{ currentTenant?.name.charAt(0).toUpperCase() }}
      </span>
      {{ tenant?.name }}
    </div>
    <bk-tree
      :data="treeData"
      :selected="appStore.currentOrg"
      label="name"
      node-key="id"
      children="children"
      :prefix-icon="getPrefixIcon"
      @node-click="handleNodeClick"
      :async="{
        callback: getRemoteData,
        cache: false,
      }"
    >
      <template #node="node">
        <div class="org-node pr-[12px] relative">
          <span class="text-[14px]">{{ node.name }}</span>
          <operate-more
            :dept="node"
            :tenant="tenant"
            :is-collaboration="true"
            @add-node="addNode"
            @update-node="updateNode">
          </operate-more>
        </div>
      </template>
    </bk-tree>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

import OperateMore from './operate-more.vue';

import useOrganizationAside from '@/hooks/useOrganizationAside';
import { getDepartmentsList } from '@/http/organizationFiles';
import useAppStore from '@/store/app';

const appStore = useAppStore();

const props = defineProps({
  tenant: {
    type: Object,
    default: () => ({}),
  },
});

const formatTreeData = (data = []) => {
  data.forEach((item) => {
    if (item.has_children) {
      item.children = [{}];
      item.async = true;
    }
  });
  return data;
};

watch(
  props.tenant,
  async (val) => {
    if (val) {
      const deptData = await getDepartmentsList(0, val.id);
      treeData.value = formatTreeData(deptData?.data);
    }
  },
  {
    immediate: true,
  },
);

const currentTenant = ref(props.tenant);

const organizationAsideHooks = useOrganizationAside(currentTenant);
const {
  treeData,
  getRemoteData,
  handleNodeClick,
  addNode,
  updateNode,
  getPrefixIcon,
} = organizationAsideHooks;

</script>

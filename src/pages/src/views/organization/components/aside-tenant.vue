<template>
  <section class="bg-white h-full pl-[6px]">
    <div class="h-[calc(100%-36px)]" v-bkloading="{ loading: loading }">
      <div
        class="leading-[36px] text-[14px] px-[6px] inline-flex items-center w-full cursor-pointer"
        :class="{ 'text-[#3A84FF] bg-[#ebf2ff]': appStore.currentOrg?.id === currentTenant?.id }"
        @click="handleNodeClick(currentTenant, currentTenant.id, true)"
      >
        <img
          v-if="currentTenant?.logo"
          class="w-[20px] h-[20px] mr-[8px]"
          :src="currentTenant?.logo" />
        <span
          v-else
          class="bg-[#C4C6CC] text-white mr-[8px] rounded-[4px] inline-block w-[20px] leading-[20px] text-center"
          :class="{ 'bg-[#3A84FF]': appStore.currentOrg?.id === currentTenant?.id }"
        >
          {{ currentTenant?.name.charAt(0).toUpperCase() }}
        </span>
        {{ currentTenant?.name }}
      </div>
      <bk-tree
        :data="treeData"
        :selected="appStore.currentOrg"
        class="overflow-y-auto"
        ref="treeRef"
        label="name"
        node-key="id"
        children="children"
        :prefix-icon="getPrefixIcon"
        @node-click="(node) => handleNodeClick(node, currentTenant.id)"
        :async="{
          callback: getRemoteData,
          cache: true,
        }"
      >
        <template #node="node">
          <div class="org-node pr-[12px] relative">
            <span class="text-[14px]">{{ node.name }}</span>
            <operate-more
              v-if="appStore.currentTenant?.data_source?.plugin_id === 'local'"
              :dept="node"
              :tenant="currentTenant"
              @add-node="addNode"
              @delete-node="deleteNode"
              @update-node="updateNode">
            </operate-more>
          </div>
        </template>
      </bk-tree>
    </div>

  </section>
</template>

<script setup lang="ts">
import { onBeforeMount, ref } from 'vue';

import OperateMore from './operate-more.vue';

import useOrganizationAside from '@/hooks/useOrganizationAside';
import { getCurrentTenant, getDepartmentsList } from '@/http/organizationFiles';
import useAppStore from '@/store/app';

const appStore = useAppStore();

const currentTenant = ref();
const loading = ref(false);

const formatTreeData = (data = []) => {
  data.forEach((item) => {
    if (item.has_children) {
      item.children = [{}];
      item.async = true;
    }
  });
  return data;
};

onBeforeMount(async () => {
  loading.value = true;
  const tenantData = await getCurrentTenant();
  currentTenant.value = tenantData?.data;
  appStore.currentTenant = tenantData?.data;
  appStore.currentOrg = { ...tenantData?.data, isTenant: true };
  const deptData = await getDepartmentsList(0, currentTenant.value?.id);
  treeData.value = formatTreeData(deptData?.data);
  loading.value = false;
});

const organizationAsideHooks = useOrganizationAside(currentTenant);
const {
  treeRef,
  treeData,
  getRemoteData,
  handleNodeClick,
  addNode,
  deleteNode,
  updateNode,
  getPrefixIcon,
} = organizationAsideHooks;

</script>

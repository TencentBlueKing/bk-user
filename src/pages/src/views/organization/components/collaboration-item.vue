<template>
  <div>
    <div
      class="leading-[36px] text-[14px] px-[6px] inline-flex items-center w-full
       cursor-pointer relative org-node hover:bg-[#F0F1F5]"
      :class="{ 'text-[#3A84FF] bg-[#ebf2ff]': activeOrg.id === collaborationTenant?.id }"
      @click="handleNodeClick(collaborationTenant, true)"
    >
      <img
        v-if="collaborationTenant?.logo"
        class="w-[20px] h-[20px] mr-[8px]"
        :src="collaborationTenant?.logo" />
      <span
        v-else
        class="bg-[#C4C6CC] text-white mr-[8px] rounded-[4px] inline-block w-[20px] leading-[20px] text-center"
        :class="{ 'bg-[#3A84FF]': appStore.currentOrg.tenantId === collaborationTenant?.id }"
      >
        {{ collaborationTenant?.name.charAt(0).toUpperCase() }}
      </span>
      <span>{{ collaborationTenant?.name }}</span>
      <operate-more :is-collaboration="true"></operate-more>
    </div>
    <bk-tree
      v-if="treeData.length"
      :data="treeData"
      :selected="selectedNode"
      label="name"
      node-key="id"
      children="children"
      :prefix-icon="getPrefixIcon"
      @node-click="(node: IOrg) => handleNodeClick(node)"
      :async="{
        callback: getRemoteData,
        cache: true,
      }"
    >
      <template #node="node">
        <div class="org-node pr-[12px] relative">
          <span class="text-[14px]">{{ node.name }}</span>
        </div>
      </template>
    </bk-tree>
  </div>
</template>

<script setup lang="ts">
import { ref, toRef, watch } from 'vue';

import OperateMore from './operate-more.vue';

import useOrganizationAside from '@/hooks/useOrganizationAside';
import { getDepartmentsList } from '@/http/organizationFiles';
import { CollaborationItemData } from '@/http/types/organizationFiles';
import useAppStore from '@/store/app';
import { IOrg } from '@/types/organization';
import { CurrentOrg } from '@/types/store';

interface IProps {
  collaborationTenant: CollaborationItemData;
  activeOrg: {
    id: number | string;
    name: string;
  };
}

const props = defineProps<IProps>();
const collaborationTenant = toRef(props, 'collaborationTenant');

const organizationAsideHooks = useOrganizationAside(collaborationTenant);
const {
  treeData,
  formatTreeData,
  getRemoteData,
  getPrefixIcon,
} = organizationAsideHooks;

const appStore = useAppStore();
const selectedNode = ref();

const handleNodeClick = (data: CollaborationItemData | IOrg, isTenant = false) => {
  selectedNode.value = data;
  if (isTenant) {
    // 点击租户节点，只传入租户信息
    appStore.updateCurrentOrg({
      tenantId: collaborationTenant.value.id,
      tenantName: data.name,
    });
  } else {
    // 点击部门节点，传入完整信息
    appStore.updateCurrentOrg({
      tenantId: collaborationTenant.value.id,
      tenantName: collaborationTenant.value.name,
      deptId: data.id,
      deptName: data.name,
    } as CurrentOrg);
  }
};

watch(
  collaborationTenant,
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
</script>

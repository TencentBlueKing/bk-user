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
        :src="collaborationTenant.logo" />
      <span
        v-else
        class="bg-[#C4C6CC] text-white mr-[8px] rounded-[4px] inline-block w-[20px] leading-[20px] text-center"
        :class="{ 'bg-[#3A84FF]': organizationStore.selectedOrg.tenantId === collaborationTenant?.id }"
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
        callback: (node: IOrg) => getRemoteData(node, collaborationTenant.id),
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
import { onMounted, ref, toRef } from 'vue';

import OperateMore from './operate-more.vue';

import useOrganizationAside from '@/hooks/useOrganizationAside';
import { getDepartmentsList } from '@/http/organizationFiles';
import { CollaborationItemData } from '@/http/types/organizationFiles';
import useOrganizationStore from '@/store/organization';
import { IOrg } from '@/types/organization';
import { SelectedOrg } from '@/types/store';

interface IProps {
  collaborationTenant: CollaborationItemData;
  activeOrg: {
    id: number | string;
    name: string;
  };
}

const props = defineProps<IProps>();
const collaborationTenant = toRef(props, 'collaborationTenant');

const organizationAsideHooks = useOrganizationAside();
const {
  treeData,
  formatDataSourceTreeData,
  getRemoteData,
  getPrefixIcon,
} = organizationAsideHooks;

const organizationStore = useOrganizationStore();
const selectedNode = ref();

const handleNodeClick = (data: CollaborationItemData | IOrg, isTenant = false) => {
  selectedNode.value = data;
  if (isTenant) {
    // 点击租户节点，只传入租户信息
    organizationStore.updateSelectedOrg({
      tenantId: collaborationTenant.value.id,
      tenantName: collaborationTenant.value.name,
      tenantLogo: collaborationTenant.value?.logo,
    });
  } else {
    // 点击部门节点，传入完整信息
    organizationStore.updateSelectedOrg({
      tenantId: collaborationTenant.value.id,
      tenantName: collaborationTenant.value.name,
      tenantLogo: collaborationTenant.value?.logo,
      dataSourceId: (data as IOrg).data_source_id,
      deptId: (data as IOrg).id,
      deptName: (data as IOrg).name,
    } as SelectedOrg);
  }
};

onMounted(async () => {
  const deptData = await getDepartmentsList(collaborationTenant.value.id, { parent_department_id: 0 });
  treeData.value = formatDataSourceTreeData(deptData?.data);
});
</script>

<template>
  <div>
    <div
      v-is-multiple-tenant
      class="leading-[36px] text-[14px] px-[6px] inline-flex items-center w-full cursor-pointer"
      :class="{ 'text-[#3A84FF] bg-[#ebf2ff]': activeOrg.id === currentTenant?.id }"
      @click="handleNodeClick(currentTenant, true)"
    >
      <img
        v-if="organizationStore.selectedOrg.tenantLogo"
        class="w-[20px] h-[20px] mr-[8px]"
        :src="organizationStore.selectedOrg.tenantLogo"
      />
      <span
        v-else
        class="bg-[#C4C6CC] text-white mr-[8px] rounded-[4px] inline-block w-[20px] leading-[20px] text-center"
        :class="{ 'bg-[#3A84FF]': activeOrg.id === currentTenant?.id }"
      >
        {{ organizationStore.selectedOrg.tenantName?.charAt(0).toUpperCase() }}
      </span>
      {{ organizationStore.selectedOrg.tenantName }}
    </div>
    <bk-tree
      :data="treeData"
      :selected="selectedNode"
      label="name"
      node-key="id"
      children="children"
      :prefix-icon="getPrefixIcon"
      @node-click="(node: IOrg) => handleNodeClick(node)"
      :async="{
        callback: (node: IOrg) => getRemoteData(node, organizationStore.currentTenant.id),
        cache: true,
      }"
    >
    </bk-tree>
  </div>
</template>

<script setup lang="ts">
import { ref, toRef } from 'vue';

import useOrganizationAside from '@/hooks/useOrganizationAside';
import { getDepartmentsList } from '@/http/organizationFiles';
import { CollaborationItemData, CurrentTenantData } from '@/http/types/organizationFiles';
import useOrganizationStore from '@/store/organization';
import { IOrg } from '@/types/organization';
import { SelectedOrg } from '@/types/store';

interface IProps {
  activeOrg: {
    id: number | string;
    name: string;
  };
}
defineProps<IProps>();

const organizationStore = useOrganizationStore();
const {
  getRemoteData,
  getPrefixIcon,
} = useOrganizationAside();

const treeData = ref([]);
const selectedNode = ref();
const currentTenant = toRef(organizationStore, 'currentTenant');

/**
 * 根据organization_path转化为树结构
 */
const getData =  (isChildren: boolean): Partial<IOrg>[] => {
  const orgs = organizationStore.selectedOrg.organizationPath || '';
  let root: Partial<IOrg> | null = null;
  let currentParent: Partial<IOrg> | null = null;
  orgs.split('/').forEach((item) => {
    const node = {
      id: organizationStore.selectedOrg.deptName === item ? organizationStore.selectedOrg.deptId : item,
      name: item,
      children: [] as IOrg[],
      async: isChildren,
    } as unknown as IOrg;
    if (!root) {
      root = node;
    } else {
      currentParent.children.push(node);
    }
    currentParent = node;
    if (organizationStore.selectedOrg.deptName === item) {
      selectedNode.value = node;
    }
  });
  return [root];
};

const handleNodeClick = (data: CurrentTenantData | CollaborationItemData | IOrg, isTenant = false) => {
  selectedNode.value = data;
  if (isTenant) {
    // 点击租户节点，只传入租户信息
    organizationStore.updateSelectedOrg({
      tenantId: currentTenant.value.id,
      tenantName: currentTenant.value.name,
      tenantLogo: currentTenant.value?.logo,
    });
  } else {
    // 点击部门节点，传入完整信息
    organizationStore.updateSelectedOrg({
      tenantId: currentTenant.value.id,
      tenantName: currentTenant.value.name,
      tenantLogo: currentTenant.value?.logo,
      dataSourceId: (data as IOrg).data_source_id,
      deptId: (data as IOrg).id,
      deptName: (data as IOrg).name,
    } as SelectedOrg);
  }
};

/**
 * 根据搜索选中的组织路径(organization_path)构建树结构并加载子部门
 * 1. 解析 organization_path (如: "租户/部门A/部门B") 构建父子层级关系
 * 2. 为最底层节点异步加载其子部门数据
 */
const getTreeData = async () => {
  const { data = [] } = await getDepartmentsList(
    organizationStore.selectedOrg.deptId,
    organizationStore.selectedOrg.tenantId,
  );
  treeData.value = getData(Boolean(data?.length));
};

defineExpose({
  getTreeData,
});
</script>

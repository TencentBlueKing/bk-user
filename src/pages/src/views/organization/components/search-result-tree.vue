<template>
  <div>
    <div
      v-is-multiple-tenant
      class="leading-[36px] text-[14px] px-[6px] inline-flex items-center w-full cursor-pointer"
    >
      <img
        v-if="organizationStore.selectedOrg.tenantLogo"
        class="w-[20px] h-[20px] mr-[8px]"
        :src="organizationStore.selectedOrg.tenantLogo"
      />
      <span
        v-else
        class="bg-[#C4C6CC] text-white mr-[8px] rounded-[4px] inline-block w-[20px] leading-[20px] text-center"
      >
        {{ organizationStore.selectedOrg.tenantName?.charAt(0).toUpperCase() }}
      </span>
      {{ organizationStore.selectedOrg.tenantName }}
    </div>
    <bk-tree
      :data="treeData"
      label="name"
      node-key="id"
      children="children"
      :prefix-icon="getPrefixIcon"
      :async="{
        callback: (node: IOrg) => getRemoteData(node, organizationStore.currentTenant.id),
        cache: true,
      }"
    >
    </bk-tree>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import useOrganizationAside from '@/hooks/useOrganizationAside';
import { getDepartmentsList } from '@/http/organizationFiles';
import useOrganizationStore from '@/store/organization';
import { IOrg } from '@/types/organization';

const organizationStore = useOrganizationStore();
const {
  getRemoteData,
  getPrefixIcon,
} = useOrganizationAside();

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
      isOpen: organizationStore.selectedOrg.deptName !== item,
    } as unknown as IOrg;
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

<template>
  <div>
    <div
      v-is-multiple-tenant
      class="leading-[36px] text-[14px] px-[6px] inline-flex items-center w-full cursor-pointer"
    >
      <img
        v-if="appStore.curTenantLogo"
        class="w-[20px] h-[20px] mr-[8px]"
        :src="appStore.curTenantLogo"
      />
      <span
        v-else
        class="bg-[#C4C6CC] text-white mr-[8px] rounded-[4px] inline-block w-[20px] leading-[20px] text-center"
      >
        {{ appStore.currentOrg.tenantName?.charAt(0).toUpperCase() }}
      </span>
      {{ appStore.currentOrg.tenantName }}
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
import { ref } from 'vue';

import useOrganizationAside from '@/hooks/useOrganizationAside';
import { getDepartmentsList } from '@/http/organizationFiles';
import useAppStore from '@/store/app';
import { IOrg } from '@/types/organization';

const appStore = useAppStore();
const {
  getRemoteData,
  getPrefixIcon,
} = useOrganizationAside(appStore.currentTenant);

/**
 * 根据organization_path转化为树结构
 */
const getData =  (isChildren: boolean): Partial<IOrg>[] => {
  const orgs = appStore.currentOrg.organizationPath || '';
  let root: Partial<IOrg> | null = null;
  let currentParent: Partial<IOrg> | null = null;
  orgs.split('/').forEach((item) => {
    const node = {
      id: appStore.currentOrg.deptName === item ? appStore.currentOrg.deptId : item,
      name: item,
      children: [] as IOrg[],
      async: isChildren,
      isOpen: appStore.currentOrg.deptName !== item,
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
  const { data = [] } = await getDepartmentsList(appStore.currentOrg.deptId, appStore.currentOrg.tenantId);
  treeData.value = getData(Boolean(data?.length));
};

defineExpose({
  getTreeData,
});
</script>

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
      node-key="treeKey"
      children="children"
      @node-click="(node: IOrg) => handleNodeClick(node)"
      :async="{
        callback: loadNodeChildren,
        cache: true,
      }"
    >
      <template #nodeType="node: IOrg">
        <img
          v-if="node.nodeType === 'source' && node.logo"
          class="source-node-logo"
          :src="node.logo"
          alt=""
          @error="handleLogoError(node)" />
        <i
          v-else-if="node.nodeType === 'source'"
          :class="['user-icon', getDataSourceIcon(node.plugin_id), 'source-node-fallback']" />
        <i v-else class="bk-sq-icon icon-file-close department-node-icon" />
      </template>
      <template #node="node: IOrg">
        <div class="pr-[12px] relative">
          <span class="text-[14px] mr-[6px]">{{ node.name }}</span>
          <bk-tag
            v-if="node.nodeType === 'source'
              && organizationStore.isEqualLocalSourceId(node.data_source_id)"
            theme="info"
          >
            {{ $t('本地') }}
          </bk-tag>
        </div>
      </template>
    </bk-tree>
  </div>
</template>

<script setup lang="ts">
import { ref, toRef } from 'vue';

import useOrganizationAside from '@/hooks/useOrganizationAside';
import { getDepartmentsList } from '@/http/organizationFiles';
import { CollaborationItemData, CurrentTenantData } from '@/http/types/organizationFiles';
import { t } from '@/language/index';
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
} = useOrganizationAside();

const treeData = ref<IOrg[]>([]);
const selectedNode = ref<IOrg | CurrentTenantData>();
const currentTenant = toRef(organizationStore, 'currentTenant');

/**
 * 根据organization_path转化为树结构
 */
const getData = (isChildren: boolean): IOrg[] => {
  const { selectedOrg } = organizationStore;
  const dataSourceId = Number(selectedOrg.dataSourceId);
  const pathSegments = (selectedOrg.organizationPath || '')
    .split('/')
    .map(item => item.trim())
    .filter(Boolean);
  const tenantNames = new Set([
    selectedOrg.tenantName,
    organizationStore.currentTenant.name,
  ].filter(Boolean));
  while (pathSegments.length && tenantNames.has(pathSegments[0])) {
    pathSegments.shift();
  }

  const sourceInfo = selectedOrg.tenantId === organizationStore.currentTenant.id
    ? organizationStore.getDataSourceInfo(dataSourceId)
    : undefined;
  const sourceName = sourceInfo?.name || t('数据源');
  if (sourceInfo && pathSegments[0] === sourceName) {
    pathSegments.shift();
  }

  const sourceNode: IOrg = {
    id: dataSourceId,
    name: sourceName,
    has_children: pathSegments.length > 0,
    data_source_id: dataSourceId,
    nodeType: 'source',
    treeKey: `source:${selectedOrg.tenantId}:${dataSourceId}`,
    logo: sourceInfo?.logo,
    plugin_id: sourceInfo?.plugin_id,
    children: [],
    async: false,
  };
  let currentParent = sourceNode;

  pathSegments.forEach((name, index) => {
    const isLast = index === pathSegments.length - 1;
    const departmentId = isLast ? Number(selectedOrg.deptId) : undefined;
    const node: IOrg = {
      id: departmentId || 0,
      name,
      has_children: isLast ? isChildren : true,
      data_source_id: dataSourceId,
      nodeType: 'department',
      treeKey: isLast
        ? `department:${dataSourceId}:${departmentId}`
        : `department-path:${dataSourceId}:${index}:${pathSegments.slice(0, index + 1).join('/')}`,
      departmentId,
      children: [],
      async: isLast && isChildren,
    };
    currentParent.children?.push(node);
    currentParent = node;
    if (isLast) {
      selectedNode.value = node;
    }
  });

  if (pathSegments.length === 0) {
    selectedNode.value = sourceNode;
  }
  return [sourceNode];
};

const handleNodeClick = (data: CurrentTenantData | CollaborationItemData | IOrg, isTenant = false) => {
  const tenantContext = {
    tenantId: organizationStore.selectedOrg.tenantId,
    tenantName: organizationStore.selectedOrg.tenantName,
    tenantLogo: organizationStore.selectedOrg.tenantLogo,
  };
  if (isTenant) {
    selectedNode.value = data as CurrentTenantData;
    organizationStore.updateSelectedOrg({
      ...tenantContext,
      nodeType: 'tenant',
    });
  } else if ((data as IOrg).nodeType === 'source') {
    selectedNode.value = data as IOrg;
    organizationStore.updateSelectedOrg({
      ...tenantContext,
      dataSourceId: (data as IOrg).data_source_id,
      deptId: 0,
      deptName: (data as IOrg).name,
      nodeType: 'source',
    } as SelectedOrg);
  } else {
    const { departmentId } = data as IOrg;
    // 搜索路径只包含末级部门 ID，中间路径节点不触发无效部门查询。
    if (departmentId === undefined) {
      return;
    }
    selectedNode.value = data as IOrg;
    organizationStore.updateSelectedOrg({
      ...tenantContext,
      dataSourceId: (data as IOrg).data_source_id,
      deptId: departmentId,
      deptName: (data as IOrg).name,
      nodeType: 'department',
    } as SelectedOrg);
  }
};

const loadNodeChildren = (node: IOrg) => {
  if (node.nodeType !== 'department' || node.departmentId === undefined) {
    return Promise.resolve([]);
  }
  return getRemoteData(node, organizationStore.selectedOrg.tenantId);
};

const handleLogoError = (node: IOrg) => {
  node.logo = '';
};

const getDataSourceIcon = (pluginId?: string) => ({
  general: 'icon-http',
  ldap: 'icon-user-directory',
  local: 'icon-shujuku',
}[pluginId || ''] || 'icon-shujuyuanshu');

/**
 * 根据搜索选中的组织路径(organization_path)构建树结构并加载子部门
 * 1. 解析 organization_path (如: "租户/数据源/部门A/部门B") 构建父子层级关系
 * 2. 为最底层节点异步加载其子部门数据
 */
const getTreeData = async () => {
  const { selectedOrg } = organizationStore;
  const departmentId = Number(selectedOrg.deptId);
  const dataSourceId = Number(selectedOrg.dataSourceId);
  const res = await getDepartmentsList(selectedOrg.tenantId, {
    parent_department_id: departmentId,
    data_source_id: dataSourceId,
  });
  treeData.value = getData(Boolean(res.data?.length));
};

defineExpose({
  getTreeData,
});
</script>

<style lang="less" scoped>
.source-node-logo,
.source-node-fallback,
.department-node-icon {
  width: 18px;
  height: 18px;
  margin: 0 6px;
  color: #A3C5FD;
  object-fit: contain;
}

.source-node-fallback,
.department-node-icon {
  font-size: 18px;
  line-height: 18px;
}
</style>

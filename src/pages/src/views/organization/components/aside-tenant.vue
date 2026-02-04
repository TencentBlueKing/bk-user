<template>
  <section class="bg-white h-full pl-[6px]">
    <div class="h-[calc(100%-36px)]" v-bkloading="{ loading: loading }">
      <div
        class="tenant-node leading-[36px] text-[14px] px-[6px] inline-flex
          items-center w-full cursor-pointer relative pr-[12px]"
        :class="{ 'text-[#3A84FF] bg-[#ebf2ff]': activeOrg.id === currentTenant?.id }"
        @click="handleNodeClick(currentTenant, true)"
      >
        <img
          v-if="currentTenant?.logo"
          class="w-[20px] h-[20px] mr-[8px]"
          :src="currentTenant?.logo" />
        <span
          v-else
          class="bg-[#C4C6CC] text-white mr-[8px] rounded-[4px] inline-block w-[20px] leading-[20px] text-center"
          :class="{ 'bg-[#3A84FF]': activeOrg.id === currentTenant?.id }"
        >
          {{ currentTenant?.name.charAt(0).toUpperCase() }}
        </span>
        {{ currentTenant?.name }}
        <operate-more
          v-if="appStore.currentTenant?.data_source?.plugin_id === 'local'"
          :dept="currentTenant"
          :tenant="currentTenant"
          :is-root-add="true"
          @add-node="addNode">
        </operate-more>
      </div>
      <bk-tree
        :data="treeData"
        :selected="selectedNode"
        class="overflow-y-auto"
        ref="treeRef"
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
          <div class="org-node pr-[12px] relative node-overflow">
            <span class="text-[14px]">{{ node.name }}</span>
            <operate-more
              v-if="appStore.currentTenant?.data_source?.plugin_id === 'local'"
              :dept="node"
              :tenant="currentTenant"
              @add-node="addNode"
              @delete-node="deleteNode"
              @update-node="updateNode"
              @move-node="getTreeData">
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
import { getCurrentTenant } from '@/http/organizationFiles';
import { CurrentTenantData } from '@/http/types/organizationFiles';
import useAppStore from '@/store/app';
import { IOrg } from '@/types/organization';
import { CurrentOrg } from '@/types/store';

interface IProps {
  activeOrg: {
    id: number | string;
    name: string;
  };
}
defineProps<IProps>();

const appStore = useAppStore();

const currentTenant = ref();
const loading = ref(false);
const organizationAsideHooks = useOrganizationAside(currentTenant);
const {
  treeData,
  getRemoteData,
  addNode,
  deleteNode,
  updateNode,
  getPrefixIcon,
} = organizationAsideHooks;

const getTreeData = async () => {
  // id为0表示获取根部门
  treeData.value = await getRemoteData({ id: 0 });
};
const selectedNode = ref();

const handleNodeClick = (data: CurrentTenantData | IOrg, isTenant = false) => {
  selectedNode.value = data;
  if (isTenant) {
    // 点击租户节点，只传入租户信息
    appStore.updateCurrentOrg({
      tenantId: currentTenant.value.id,
      tenantName: currentTenant.value.name,
    });
  } else {
    // 点击部门节点，传入完整信息
    appStore.updateCurrentOrg({
      tenantId: currentTenant.value.id,
      tenantName: currentTenant.value.name,
      deptId: data.id,
      deptName: data.name,
    } as CurrentOrg);
  }
};

onBeforeMount(async () => {
  loading.value = true;
  const tenantData = await getCurrentTenant();
  currentTenant.value = tenantData?.data;
  appStore.currentTenant = tenantData?.data;
  appStore.updateCurrentOrg({
    tenantId: tenantData.data?.id,
    tenantName: tenantData.data?.name,
  });
  getTreeData();
  loading.value = false;
});
</script>

<style lang="less" scoped>
.node-overflow{
  min-width: auto;
  overflow: hidden;
  text-align: left;
  text-overflow: ellipsis;
  white-space: nowrap;
  border-radius: 4px;
}

.tenant-node {
  :deep(.opt-more) {
    visibility: hidden;

    &:hover {
      :deep(.icon-more) {
        background-color: #DCDEE5;
      }
    }
  }

  &:hover {
    :deep(.opt-more) {
      visibility: visible;
    }
  }
}
</style>

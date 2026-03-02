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
          v-if="currentTenant.logo"
          class="w-[20px] h-[20px] mr-[8px]"
          :src="currentTenant.logo" />
        <span
          v-else
          class="bg-[#C4C6CC] text-white mr-[8px] rounded-[4px] inline-block w-[20px] leading-[20px] text-center"
          :class="{ 'bg-[#3A84FF]': activeOrg.id === currentTenant?.id }"
        >
          {{ currentTenant?.name.charAt(0).toUpperCase() }}
        </span>
        {{ currentTenant?.name }}
        <operate-more
          v-if="organizationStore.hasPluginDataSource('local')"
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
          callback: (node: IOrg) => getRemoteData(node, organizationStore.currentTenant.id),
          cache: true,
        }"
      >
        <template #node="node: IOrg & { __attr__: { isRoot: boolean } }">
          <div class="org-node pr-[12px] relative node-overflow">
            <span class="text-[14px] mr-[6px]">{{ node.name }}</span>
            <template v-if="organizationStore.isEqualLocalSourceId(node.data_source_id)">
              <bk-tag
                v-if="node.__attr__.isRoot && organizationStore.hasExternalDataSource"
                theme="info"
              >
                {{ $t('本地') }}
              </bk-tag>
              <operate-more
                :dept="node"
                :tenant="currentTenant"
                @add-node="addNode"
                @delete-node="deleteNode"
                @update-node="updateNode"
                @move-node="getTreeData">
              </operate-more>
            </template>
          </div>
        </template>
      </bk-tree>
    </div>

  </section>
</template>

<script setup lang="ts">
import { ref, toRef, watch } from 'vue';

import OperateMore from './operate-more.vue';

import useOrganizationAside from '@/hooks/useOrganizationAside';
import { CurrentTenantData } from '@/http/types/organizationFiles';
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

const currentTenant = toRef(organizationStore, 'currentTenant');
const loading = ref(false);
const organizationAsideHooks = useOrganizationAside();
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
  treeData.value = await getRemoteData({ id: 0 }, organizationStore.currentTenant.id);
};
const selectedNode = ref();

const handleNodeClick = (data: CurrentTenantData | IOrg, isTenant = false) => {
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
 * @description 监听当前租户变化，更新当前组织，组织架构会请求租户信息，避免该侧栏造成的多次请求
 */
watch(
  () => organizationStore.currentTenant.id,
  async (val) => {
    if (val) {
      loading.value = true;
      await getTreeData().finally(() => {
        loading.value = false;
      });
    }
  },
  { immediate: true },
);
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

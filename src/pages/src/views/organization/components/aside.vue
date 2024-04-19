<template>
  <section class="bg-white h-full" ref="asideRef">
    <div class="px-[12px] h-[52px] flex shadow-[0_3px_4px_0_#0000000a] pt-[10px]">
      <bk-input
        v-model="search"
        type="search"
      ></bk-input>
      <div class="user-icon icon-refresh bg-[#F0F1F5] h-[32px] w-[32px] ml-[8px] !leading-[32px] cursor-pointer">
      </div>
    </div>
    <div class="pl-[6px]">
      <div class="leading-[36px] text-[14px] px-[6px]">{{ currentTenant?.name }}</div>
      <bk-tree
        :data="treeData"
        :selected="selected"
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
          <div class="org-node flex justify-between pr-[12px]">
            <span class="text-[14px]">{{ node.name }}</span>
            <operate-more
              :dept="node"
              :tenant="currentTenant"
              @add-node="addNode"
              @update-node="updateNode">
            </operate-more>
          </div>
        </template>
      </bk-tree>
    </div>

  </section>
</template>

<script setup lang="ts">
import { onBeforeMount, ref, watch } from 'vue';

import OperateMore from './operate-more.vue';

import { getCurrentTenant, getDepartmentsList } from '@/http/organizationFiles';
import { IOrg } from '@/types/organization';

const emits = defineEmits(['updateOrg']);
const asideRef = ref();

const treeData = ref<any>({});
const selected = ref<any>({});

const currentTenant = ref();

onBeforeMount(async () => {
  const tenantData = await getCurrentTenant();
  currentTenant.value = tenantData?.data;
  selected.value = tenantData?.data;
  const deptData = await getDepartmentsList(0, currentTenant.value?.id);
  treeData.value = formatTreeData(deptData?.data);
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

const getRemoteData = async (item: IOrg) => {
  const res = await getDepartmentsList(item.id, currentTenant.value?.id);
  return formatTreeData(res?.data);
};

const handleNodeClick = (item: IOrg) => {
  selected.value = item;
};

const search = ref('');

const getPrefixIcon = (item: { children?: any[] }, renderType: string) => {
  const { children = [] } = item;
  if (renderType === 'node_action') {
    return 'default';
  }

  if (children.length) {
    return {
      node: 'span',
      className: 'bk-sq-icon icon-file-close pr-1',
      style: {
        color: '#A3C5FD',
      },
    };
  }
};

/**
 * 添加子组织
 */
const addNode = (id, node) => {
  const findNode = (item: IOrg, id: number) => {
    if (item.id === id) {
      return item;
    }
    if (item.children) {
      for (const child of item.children) {
        const result = findNode(child, id);
        if (result) {
          return result;
        }
      }
    }
    return null;
  };

  for (const item of treeData.value) {
    const current = findNode(item, id);
    if (current) {
      if (current.children) {
        current.children.push(node);
      } else {
        current.children = [node];
      }
    }
  }
};

/**
 * 重命名
 * @param node
 */
const updateNode = (node: IOrg) => {
  const findNode = (item: IOrg, id: number) => {
    if (item.id === id) {
      return item;
    }
    if (item.children) {
      for (const child of item.children) {
        const result = findNode(child, id);
        if (result) {
          return result;
        }
      }
    }
    return null;
  };

  for (const item of treeData.value) {
    const current = findNode(item, node.id);
    if (current) {
      current.name = node.name;
    }
  }
};

/**
 * 监听组织变化
 */
watch(selected, (val) => {
  emits('updateOrg', val);
});

</script>

<style lang="postcss" scoped>
:deep(.bk-node-row) {
  &:hover {
    background-color: #F0F1F5;
  }
}

.org-node {
  .opt-more {
    visibility: hidden;

    &:hover {
      :deep(.icon-more) {
        background-color: #DCDEE5;
      }
    }
  }

  &:hover {
    .opt-more {
      visibility: visible;
    }
  }
}
</style>

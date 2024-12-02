<template>
  <div v-if="isLoading"></div>
  <div v-else>
    <blank-page v-if="isShow"></blank-page>
    <bk-resize-layout
      v-else
      class="h-[calc(100vh-52px)] user-aside"
      immediate
      :min="280"
      :max="400"
      :initial-divide="280">
      <template #aside>
        <search @select="handleSearchSelect"></search>
        <div v-show="appStore.isSearchTree">
          <search-result-tree ref="searchResultTreeRef"></search-result-tree>
        </div>
        <bk-resize-layout
          v-show="!appStore.isSearchTree"
          :key="appStore.reloadIndex"
          placement="top"
          style="height: calc(100vh - 106px)"
          :border="false"
          immediate
          :min="140"
          :max="900"
          :initial-divide="'50%'">
          <template #aside>
            <aside-tenant />
          </template>
          <template #main>
            <aside-collaboration />
          </template>
        </bk-resize-layout>
      </template>
      <template #main>
        <section>
          <div class="text-[#313238] leading-[52px] px-[24px] text-[16px] shadow-[0_3px_4px_0_#0000000a] bg-white">
            {{ appStore.currentOrg?.name }}
          </div>
          <div class="table-main">
            <TableList ref="tableListRef" @click-import="importHandle" />
          </div>
        </section>
      </template>
    </bk-resize-layout>
  </div>
</template>

<script setup lang="ts">

import { ref } from 'vue';

import AsideCollaboration from './components/aside-collaboration.vue';
import AsideTenant from './components/aside-tenant.vue';
import BlankPage from './components/blank-page.vue';
import Search from './components/search-org.vue';
import SearchResultTree from './components/search-result-tree.vue';
import TableList from './components/table-list.vue';

import { getCollaboration, getCurrentTenant, getDepartmentsList } from '@/http/organizationFiles';
import useAppStore from '@/store/app';

const appStore = useAppStore();
const isShow = ref(null);
const isLoading = ref(false);
const tableListRef = ref();

const getList = async () => {
  isLoading.value = true;
  const tenantData = await getCurrentTenant();
  appStore.currentTenant = tenantData?.data;
  const collaborationData = await getCollaboration();
  const deptData = await getDepartmentsList(0, tenantData?.data?.id);
  isLoading.value = false;
  if (deptData.data.length === 0 && collaborationData.data.length === 0) {
    isShow.value = true;
  } else {
    isShow.value = false;
  }
};
getList();

const importHandle = async () => {
  await getList();
  tableListRef.value.importDialogHandle();
};

const searchResultTreeRef = ref();
const handleSearchSelect = () => {
  if (searchResultTreeRef.value) {
    searchResultTreeRef.value.getTreeData();
  }
};
</script>

<style lang="postcss" scoped>
.table-main {
  height: calc(100vh - 170px);
}

:deep(.bk-node-row) {
  &:hover {
    background-color: #F0F1F5;
  }
}

:deep(.org-node) {
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

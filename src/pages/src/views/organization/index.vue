<template>
  <bk-resize-layout
    class="h-[calc(100vh-52px)] user-aside"
    immediate
    :min="280"
    :max="400"
    :initial-divide="280">
    <template #aside>
      <search></search>
      <div v-show="appStore.isSearchTree">
        <search-result-tree></search-result-tree>
      </div>
      <bk-resize-layout
        v-show="!appStore.isSearchTree"
        :key="appStore.reloadIndex"
        placement="top"
        style="height: calc(100vh - 106px);"
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
      </section>
    </template>
  </bk-resize-layout>
</template>

<script setup lang="ts">

import AsideCollaboration from './components/aside-collaboration.vue';
import AsideTenant from './components/aside-tenant.vue';
import Search from './components/search.vue';
import SearchResultTree from './components/search-result-tree.vue';

import useAppStore from '@/store/app';

const appStore = useAppStore();
</script>

<style lang="postcss" scoped>
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

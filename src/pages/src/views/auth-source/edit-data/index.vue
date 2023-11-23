<template>
  <div>
    <MainBreadcrumbs />
    <div class="edit-data-wrapper user-scroll-y">
      <Local v-if="pluginId === 'local'" />
      <WeCom v-else-if="pluginId === 'wecom'" />
      <CustomPlugin v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

import CustomPlugin from './CustomPlugin.vue';
import Local from './Local.vue';
import WeCom from './WeCom.vue';

import MainBreadcrumbs from '@/components/layouts/MainBreadcrumbs.vue';

const route = useRoute();

const pluginId = computed(() => route.params.type);
</script>

<style lang="less">
.container-content {
  overflow: hidden !important;
}

.edit-data-wrapper {
  height: calc(100vh - 104px);
}
</style>

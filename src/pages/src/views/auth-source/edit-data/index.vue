<template>
  <div>
    <MainBreadcrumbs />
    <div ref="boxRef" class="edit-data-wrapper user-scroll-y">
      <Local v-if="pluginId === 'local'" />
      <WeCom v-else-if="pluginId === 'wecom'" :box-ref="boxRef" />
      <CustomPlugin v-else :box-ref="boxRef" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineExpose, ref } from 'vue';
import { useRoute } from 'vue-router';

import CustomPlugin from './CustomPlugin.vue';
import Local from './Local.vue';
import WeCom from './WeCom.vue';

import MainBreadcrumbs from '@/components/layouts/MainBreadcrumbs.vue';

const route = useRoute();

const pluginId = computed(() => route.params.type);

const boxRef = ref();
defineExpose({ boxRef });
</script>

<style lang="less">
.container-content {
  overflow: hidden !important;
}

.edit-data-wrapper {
  position: relative;
  height: calc(100vh - 104px);
  padding-bottom: 48px;
}
</style>

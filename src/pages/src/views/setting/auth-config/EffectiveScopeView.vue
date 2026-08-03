<template>
  <div class="effective-scope-view">
    <bk-tag
      v-for="item in selectedOptions"
      :key="item.id"
      class="scope-tag"
    >
      {{ item.name }}
    </bk-tag>
    <span v-if="selectedOptions.length === 0" class="empty-scope">--</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { useDataSourceStore } from '@/store/dataSource';

interface ScopeOption {
  id: number;
  name: string;
  plugin_id: string;
}

const props = withDefaults(defineProps<{
  sourceIds?: number[];
}>(), {
  sourceIds: () => [],
});

const dataSourceStore = useDataSourceStore();

const scopeOptions = computed<ScopeOption[]>(() => dataSourceStore.dataSource.map(item => ({
  id: item.id,
  plugin_id: item.plugin_id,
  name: item.name
    || dataSourceStore.dataSourcePlugins.find(plugin => plugin.id === item.plugin_id)?.name
    || item.plugin_id,
})));
const selectedOptions = computed(() => {
  const selectedIds = new Set(props.sourceIds);
  return scopeOptions.value.filter(item => selectedIds.has(item.id));
});
</script>

<style lang="less" scoped>
.effective-scope-view {
  display: flex;
  min-height: 40px;
  margin-bottom: 8px;
  line-height: normal;
  align-items: center;
  align-content: center;
  flex-wrap: wrap;
  gap: 4px 8px;
}

.scope-tag {
  margin: 0;
}

.empty-scope {
  line-height: 40px;
}
</style>

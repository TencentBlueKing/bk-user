<template>
  <Row :title="$t('生效范围')">
    <bk-form-item
      :label="$t('数据源')"
      required
      property="data_source"
      :rules="formRules.data_source"
    >
      <bk-select
        class="w-[560px]"
        :model-value="modelValue"
        multiple
        multiple-mode="tag"
        collapse-tags
        :clearable="false"
        :placeholder="$t('请选择生效的数据源')"
        @update:model-value="handleChange"
      >
        <bk-option
          v-for="item in availableOptions"
          :key="item.id"
          :value="item.id"
          :label="item.name"
          :name="item.name"
        />
      </bk-select>
    </bk-form-item>
  </Row>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import Row from '@/components/layouts/ItemRow.vue';
import { useDataSourceStore } from '@/store/dataSource';

interface ScopeOption {
  id: number;
  name: string;
  plugin_id: string;
}

const props = withDefaults(defineProps<{
  modelValue?: number[];
  localOnly?: boolean;
}>(), {
  modelValue: () => [],
  localOnly: false,
});

const emit = defineEmits<{
  'update:modelValue': [value: number[]];
  change: [value: number[]];
}>();

const dataSourceStore = useDataSourceStore();
const { t } = useI18n();

const formRules = {
  data_source: [{
    required: true,
    message: t('请选择生效的数据源'),
    validator: () => props.modelValue?.length > 0,
    trigger: 'change',
  }],
};

const scopeOptions = computed<ScopeOption[]>(() => dataSourceStore.dataSource.map(item => ({
  id: item.id,
  plugin_id: item.plugin_id,
  name: item.name
    || dataSourceStore.dataSourcePlugins.find(plugin => plugin.id === item.plugin_id)?.name
    || item.plugin_id,
})));
const availableOptions = computed(() => (
  props.localOnly ? scopeOptions.value.filter(item => item.plugin_id === 'local') : scopeOptions.value
));

const handleChange = (value: number[]) => {
  emit('update:modelValue', value);
  emit('change', value);
};
</script>

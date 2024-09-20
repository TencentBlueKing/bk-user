<template>
  <BkSchemaForm
    v-model="data"
    :schema="pluginsConfig"
    form-type="vertical"
    ref="BkSchemaFormRef"
    @change="handleChange">
  </BkSchemaForm>
</template>

<script setup lang="ts">
import { computed, defineExpose, ref, watch } from 'vue';

import createForm from '@blueking/bkui-form';

const props = defineProps({
  pluginsConfig: {
    type: Object,
    default: () => ({}),
  },
  formData: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(['changePluginConfig']);

const BkSchemaForm = createForm();

const data = ref(props.formData.plugin_config);

const propsValue = computed(() => props.formData);

watch(propsValue, (value) => {
  data.value = value.plugin_config;
}, { deep: true });

const BkSchemaFormRef = ref();

const handleChange = async (data: any) => {
  emit('changePluginConfig', data);
};
defineExpose({
  element: BkSchemaFormRef,
});
</script>

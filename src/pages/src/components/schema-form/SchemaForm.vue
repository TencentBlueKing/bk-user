<template>
  <BkSchemaForm
    v-model="data"
    :schema="pluginsConfig"
    form-type="vertical"
    @change="handleChange">
  </BkSchemaForm>
</template>

<script setup lang="ts">
import { reactive } from 'vue';

import '@blueking/bkui-form/dist/bkui-form.css';
import createForm from '@/common/bkui-form';

const BkSchemaForm = createForm();

const emit = defineEmits(['changePluginConfig']);

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

const data = reactive({
  ...props.formData.plugin_config,
});

const handleChange = (data: any) => {
  emit('changePluginConfig', data);
};
</script>

<style>

</style>

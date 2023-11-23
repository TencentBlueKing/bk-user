<template>
  <BkSchemaForm
    :model="formData.plugin_config"
    :schema="pluginsConfig"
    form-type="vertical">
  </BkSchemaForm>
</template>

<script setup lang="ts">
import '@blueking/bkui-form/dist/bkui-form.css';
import createForm from '@/common/bkui-form';

const BkSchemaForm = createForm();

defineProps({
  pluginsConfig: {
    type: Object,
    default: () => ({}),
  },
  formData: {
    type: Object,
    default: () => ({}),
  },
});
</script>

<style>

</style>

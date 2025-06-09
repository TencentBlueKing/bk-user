<template>
  <div class="flex">
    <SelectPanel
      :title="$t('字段')"
      :options="fieldOptions"
      class="border-r-[1px] border-[#DCDEE5]"
      :tips="$t('最多仅允许添加3个字段')"
      @change="handleFieldChange" />
    <SelectPanel
      :title="$t('符号')"
      :options="symbolOptions"
      @change="handleSymbolChange" />
  </div>
</template>

<script lang="ts" setup>
import SelectPanel from './selectPanel.vue';
defineProps<{
  fieldOptions: any[]
  symbolOptions: any[]
}>();
const emit = defineEmits(['fieldChange', 'symbolChange']);

const handleFieldChange = (option) => {
  emit('fieldChange', option);
};

const handleSymbolChange = (option) => {
  emit('symbolChange', option);
};

</script>

<template>
  <div>
    <ConfigPreview inner-class-name="absolute -top-[28px] left-[90px]" />
    <div class="flex">
      <div class="mr-[4px]">
        <showTags :data="data" @delete="handleDeleteTag" @sort="handleSortTag" />
      </div>
      <bk-popover
        trigger="click"
        theme="light display-name-config-no-padding-popover"
        placement="bottom-start"
        :arrow="false">
        <div
          class="bg-[#E1ECFF] text-[#3A84FF] w-[32px] h-[32px] leading-[32px]
            text-[12px] cursor-pointer text-center hover:bg-[#CDDFFE]">
          <i class="user-icon icon-add-2"></i>
        </div>
        <template #content>
          <div class="flex">
            <SelectPanel
              title="字段"
              :options="fieldOptions"
              class="border-r-[1px] border-[#DCDEE5]"
              tips="最多仅允许添加3个字段"
              @change="handleFieldChange" />
            <SelectPanel
              title="符号"
              :options="symbolOptions"
              @change="handleSymbolChange" />
          </div>
        </template>
      </bk-popover>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import ConfigPreview from './configPreview.vue';
import { SYMBOL_OPTIONS } from './select-panel/data';
import SelectPanel from './select-panel/selectPanel.vue';
import { IOption } from './select-panel/type';
import showTags from './showTags.vue';

import { getFields } from '@/http';

const data = defineModel<any[]>('data');

const handleDeleteTag = (index: number) => {
  data.value.splice(index, 1);
  for (const item of fieldOptions.value) {
    if (selectedFieldValue.value.findIndex(field => field.value === item.id) !== -1) {
      item.hide = true;
      item.disabled = false;
    } else {
      item.hide = false;
      item.disabled = false;
    }
  }
  isAllFieldDisabled = false;
};

const handleSortTag = ({ oldIndex, newIndex }: {oldIndex: number, newIndex: number}) => {
  const item = data.value.splice(oldIndex, 1)[0];
  data.value.splice(newIndex, 0, item);
};

const fieldOptions = ref([]);
const symbolOptions = ref(SYMBOL_OPTIONS);

const selectedFieldValue = computed(() => data.value.filter(item => item.type === 'field'));

const handleFieldChange = (option: IOption) => {
  if (selectedFieldValue.value.length >= 3) return;

  data.value.push({
    type: 'field',
    value: option.id,
    label: option.value,
  });
  const optionIndex = fieldOptions.value.findIndex(item => item.id === option.id);
  fieldOptions.value[optionIndex].hide = true;

  fieldEnableManagement();
};

let isAllFieldDisabled = false;
const setAllFieldEnable = () => {
  if (!isAllFieldDisabled) return;
  for (const option of fieldOptions.value) {
    option.disabled = false;
  }
  isAllFieldDisabled = false;
};

/** 若字段已选择了3个，需要把所有字段选项禁用 */
const setAllFieldDisabled = () => {
  for (const option of fieldOptions.value) {
    if (option.hide) continue;
    option.disabled = true;
  }
  isAllFieldDisabled = true;
};

/** 字段选项禁用管理 */
const fieldEnableManagement = () => {
  if (selectedFieldValue.value.length >= 3) {
    setAllFieldDisabled();
  } else {
    setAllFieldEnable();
  }
};

const handleSymbolChange = (option: IOption) => {
  data.value.push({
    type: 'symbol',
    value: option.id,
    label: option.value,
  });
};

const handleFetchFields = async () => {
  const res = await getFields();
  const { builtin_fields: builtinFields, custom_fields: customFields } = res.data || {};
  [builtinFields, customFields].forEach((fields) => {
    const fieldsArr = fields.map(item => ({
      id: item.name,
      value: item.display_name,
      icon: 'user-icon icon-app-store-fill bg-[#F8B64F]',
    }));
    fieldOptions.value = [...fieldOptions.value, ...fieldsArr];
  });
};

onMounted(() => {
  handleFetchFields();
});

</script>

<style lang="less">
.display-name-config-no-padding-popover {
  padding: 0 !important;
}
</style>

<template>
  <div>
    <ConfigPreview
      inner-class-name="absolute -top-[28px] left-[90px]"
      :preview-list="previewList" />
    <div class="flex">
      <div class="mr-[4px]">
        <bk-loading :loading="isLoading" size="small">
          <showTags
            :data="data"
            :value-map="tagValueMap"
            @delete="handleDeleteTag"
            @sort="handleSortTag" />
        </bk-loading>
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
      </bk-popover>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref, watch } from 'vue';

import ConfigPreview from './configPreview.vue';
import { SYMBOL_OPTIONS } from './select-panel/data';
import SelectPanel from './select-panel/selectPanel.vue';
import { IOption } from './select-panel/type';
import showTags from './showTags.vue';

import { getFields } from '@/http';

const data = defineModel<any[]>('data');
defineProps<{
  previewList: { display_name: string }[]
}>();
const emit = defineEmits(['change']);
const tagValueMap = computed(() => [...fieldOptions.value, ...symbolOptions.value]);

const handleDeleteTag = (index: number) => {
  const item = data.value.splice(index, 1);
  isAllFieldDisabled = false;
  emit('change', item, 'delete');
};

const handleSortTag = ({ oldIndex, newIndex }: {oldIndex: number, newIndex: number}) => {
  const item = data.value.splice(oldIndex, 1)[0];
  data.value.splice(newIndex, 0, item);
  emit('change', item, 'sort');
};

const fieldOptions = ref([]);
const symbolOptions = ref(SYMBOL_OPTIONS);

const selectedFieldValue = computed(() => data.value.filter(item => item.type === 'field'));

const handleFieldChange = (option: IOption) => {
  if (selectedFieldValue.value.length >= 3) return;
  const curItem = {
    type: 'field',
    value: option.id,
  };
  data.value.push(curItem);
  emit('change', curItem, 'add');
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

const fieldShowManagement = () => {
  for (const item of fieldOptions.value) {
    if (selectedFieldValue.value.findIndex(field => field.value === item.id) !== -1) {
      item.hide = true;
      item.disabled = false;
    } else {
      item.hide = false;
      item.disabled = false;
    }
  }
};

const handleSymbolChange = (option: IOption) => {
  const curItem = {
    type: 'symbol',
    value: option.id,
  };
  data.value.push(curItem);
  emit('change', curItem, 'add');
};

const isLoading = ref(false);
const handleFetchFields = async () => {
  try {
    isLoading.value = true;

    const disabledDataTypes = ['enum', 'multi_enum'];
    const res = await getFields();
    const { builtin_fields: builtinFields, custom_fields: customFields } = res.data || {};
    [builtinFields, customFields].forEach((fields) => {
      const fieldsArr = fields
        .filter(item => !disabledDataTypes.includes(item.data_type))
        .map(item => ({
          id: item.name,
          value: item.display_name,
          icon: 'user-icon icon-app-store-fill bg-[#F8B64F]',
        }));
      fieldOptions.value = [...fieldOptions.value, ...fieldsArr];
    });
  } catch (err) {
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};

watch(data, () => {
  fieldShowManagement();
  fieldEnableManagement();
}, { deep: true });

onMounted(async () => {
  await handleFetchFields();
  fieldShowManagement();
  fieldEnableManagement();
});

</script>

<style lang="less">
.display-name-config-no-padding-popover {
  padding: 0 !important;
}
</style>

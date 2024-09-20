import { ref } from 'vue';

import { t } from '@/language/index';

export const useCustomPlugin = (formData, dataSourceList, builtinFields, customFields) => {
  const changeDataSourceId = (val, oldVal) => {
    dataSourceList.value.forEach((item) => {
      if (item.key === val) {
        item.disabled = true;
      } else if (item.key === oldVal) {
        item.disabled = false;
      }
    });
    handleChange();
  };

  const currentIndex = ref(0);
  const changeSourceField = (val, oldVal) => {
    formData.value.data_source_match_rules[currentIndex.value].targetFields.forEach((item) => {
      if (item.name === val) {
        item.disabled = true;
      } else if (item.name === oldVal) {
        item.disabled = false;
      }
    });
    handleChange();
  };

  const handleToggle = (index) => {
    currentIndex.value = index;
  };

  const getFieldItem = () => ({
    target_field: '',
    source_field: '',
  });

  const handleAddItem = (fields, i) => {
    fields.splice(i + 1, 0, getFieldItem());
    handleChange();
  };

  const handleDeleteItem = (val, index, fields, i) => {
    fields.splice(i, 1);
    formData.value.data_source_match_rules[index].targetFields.forEach((item) => {
      if (item.name === val) {
        item.disabled = false;
      }
    });
    handleChange();
  };

  // 新增数据源匹配
  const handleAdd = () => {
    formData.value.data_source_match_rules.push({
      data_source_id: '',
      field_compare_rules: [
        {
          target_field: '',
          source_field: '',
        },
      ],
      targetFields: [
        ...builtinFields.value?.map(item => ({
          key: item.id, name: item.name, disabled: false, type: t('内置'),
        })) || [],
        ...customFields.value?.map(item => ({
          key: item.id, name: item.name, disabled: false, type: t('自定义'),
        })) || [],
      ],
    });
  };
  // 删除数据源匹配
  const handleDelete = (item, index) => {
    formData.value.data_source_match_rules.splice(index, 1);
    if (Array.isArray(dataSourceList.value)) {
      const foundItem = dataSourceList.value.find(val => val.key === item.data_source_id);
      if (foundItem) {
        foundItem.disabled = false;
      }
    }
    handleChange();
  };

  const hoverItem = ref(null);
  const mouseenter = (index: number) => {
    hoverItem.value = index;
  };

  const mouseleave = () => {
    hoverItem.value = null;
  };

  const handleChange = () => {
    window.changeInput = true;
  };

  return {
    changeDataSourceId,
    changeSourceField,
    handleToggle,
    handleAddItem,
    handleDeleteItem,
    handleAdd,
    handleDelete,
    mouseenter,
    mouseleave,
    handleChange,
    hoverItem,
  };
};

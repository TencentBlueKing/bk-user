import { InfoBox, Message } from 'bkui-vue';
import { h, ref } from 'vue';

import { postIdps, putIdps } from '@/http/authSourceFiles';
import router from '@/router/index';
import { copy } from '@/utils';

export const useCustomPlugin = (formData, dataSourceList, builtinFields, customFields, btnLoading, formRef, type) => {
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
          key: item.id, name: item.name, disabled: false, type: '内置',
        })) || [],
        ...customFields.value?.map(item => ({
          key: item.id, name: item.name, disabled: false, type: '自定义',
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

  const handleCancel = () => {
    router.push({
      name: 'authSourceList',
    });
  };

  const handleSubmit = async () => {
    try {
      await formRef.value.validate();
      btnLoading.value = true;
      const data = formData.value;
      data.data_source_match_rules.forEach((item) => {
        delete item.targetFields;
      });

      if (type === 'add') {
        const res = await postIdps(data);

        InfoBox({
          title: '认证源创建成功',
          extCls: 'info-wrapper',
          subTitle: h('div', {
            class: 'details-url',
            style: {
              display: res.data?.callback_uri ? 'block' : 'none',
            },
          }, [
            h('p', {
              class: 'title',
            }, '请将一下回调地址填写到企业微信配置内：'),
            h('div', {
              class: 'content',
            }, [
              h('p', {}, res.data?.callback_uri),
              h('i', {
                class: 'user-icon icon-copy',
                onClick: () => copy(res.data?.callback_uri),
              }),
            ]),
          ]),
          dialogType: 'confirm',
          confirmText: '确定',
          infoType: 'success',
          quickClose: false,
          onConfirm() {
            window.changeInput = false;
            router.push({
              name: 'authSourceList',
            });
          },
        });
      } else {
        await putIdps(data);
        Message({ theme: 'success', message: '认证源更新成功' });
        window.changeInput = false;
        router.push({ name: 'authSourceList' });
      }
    } catch (e) {
      console.warn(e);
    } finally {
      btnLoading.value = false;
    }
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
    handleCancel,
    handleSubmit,
    hoverItem,
  };
};

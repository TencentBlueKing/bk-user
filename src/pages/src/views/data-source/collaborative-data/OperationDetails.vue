<template>
  <div class="operation-wrapper user-scroll-y">
    <div class="operation-content">
      <div class="operation-card">
        <p class="operation-content-title">{{ $t('源租户信息') }}</p>
        <ul class="operation-content-info flex">
          <li>
            <span class="key">{{ $t('租户名称') }}：</span>
            <span class="value">{{ detailsConfig.data.name }}</span>
          </li>
          <li>
            <span class="key">{{ $t('租户ID') }}：</span>
            <span class="value">{{ detailsConfig.data.id }}</span>
          </li>
        </ul>
      </div>
      <div class="operation-card">
        <div class="operation-content-header">
          <p class="operation-content-title">{{ $t('字段映射') }}</p>
          <bk-button
            v-if="detailsConfig.type === 'edit' && !isEdit"
            class="min-w-[48px] mr-[24px]"
            theme="primary"
            outline
            @click="isEdit = true"
          >
            {{ $t('编辑') }}
          </bk-button>
        </div>
        <bk-form
          v-if="isEdit"
          form-type="vertical"
          ref="formRef2"
          :model="fieldSettingData"
          :rules="rulesFieldSetting">
          <FieldMapping
            :field-setting-data="fieldSettingData"
            :api-fields="apiFields"
            :rules="rulesFieldSetting"
            @changeApiFields="changeApiFields"
            @handleAddField="handleAddField"
            @handleDeleteField="handleDeleteField"
            @changeCustomField="changeCustomField" />
          <div class="ml-[64px]">
            <bk-button
              class="min-w-[64px] mr-[8px]"
              theme="primary">
              {{ $t('保存') }}
            </bk-button>
            <bk-button
              class="min-w-[64px]"
              @click="isEdit = false">
              {{ $t('取消') }}
            </bk-button>
          </div>
        </bk-form>
        <div v-else class="field-mapping-content">
          <ul
            v-for="(item, index) in fieldSettingData.field_mapping.builtin_fields"
            :key="index">
            <li>{{ item.display_name }}</li>
            <li>{{ getCustomCondition(item.mapping_operation) }}</li>
            <li>{{ item.source_field }}</li>
          </ul>
          <ul
            v-for="(item, index) in fieldSettingData.addFieldList"
            :key="index">
            <li>{{ getDisplayName(item.target_field) }}</li>
            <li>{{ getCustomCondition(item.mapping_operation) }}</li>
            <li>{{ item.source_field }}</li>
          </ul>
        </div>
      </div>
    </div>
    <div class="footer fixed" v-if="isEdit">
      <bk-button theme="primary" @click="handleSave">
        {{ $t('确认') }}
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';

import FieldMapping from '@/components/field-mapping/FieldMapping.vue';
import { useValidate } from '@/hooks';
import {
  getDataSourceDetails,
  getFields,
} from '@/http';

const validate = useValidate();

defineProps({
  detailsConfig: {
    type: Object,
    default: () => ({}),
  },
});

const isEdit = ref(false);

const rulesFieldSetting = {
  target_field: [validate.required],
  source_field: [validate.required],
};

const apiFields = ref([]);
const fieldMappingList = ref([]);
const fieldSettingData = reactive({
  field_mapping: {
    // 内置字段
    builtin_fields: [],
    // 自定义字段
    custom_fields: [],
  },
  addFieldList: [],
});

onMounted(async () => {
  const res = await getDataSourceDetails(6);
  fieldMappingList.value = res.data?.field_mapping;
  const fieldsRes = await getFields();

  const list = [];
  const customList = [];
  const mapFields = (fields, item, isDisabled, fieldMappingType) => {
    if (fields.name !== item.target_field) return;

    list.push(item.source_field);
    customList.push(fields.name);
    Object.assign(fields, {
      mapping_operation: item.mapping_operation,
      source_field: item.source_field,
      disabled: isDisabled,
    });
    apiFields.value.push({ key: item.source_field, disabled: isDisabled });

    if (fieldMappingType === 'builtin_fields' && fields.required) {
      fieldSettingData.field_mapping.builtin_fields.push(fields);
    } else {
      fieldSettingData.addFieldList.push(item);
      fieldSettingData.field_mapping.custom_fields.push(fields);
    }
  };

  fieldMappingList.value.forEach((item) => {
    fieldsRes.data?.builtin_fields?.forEach(fields => mapFields(fields, item, true, 'builtin_fields'));
    fieldsRes.data?.custom_fields?.forEach(fields => mapFields(fields, item, true, 'custom_fields'));
  });


  fieldsRes.data?.custom_fields?.concat(fieldsRes.data?.builtin_fields || []).forEach((fields) => {
    if (!customList.includes(fields.name)) {
      fieldSettingData.field_mapping.custom_fields.push(fields);
    }
  });
});

const getDisplayName = (item) => {
  const name = ref('');
  fieldSettingData.field_mapping.custom_fields.forEach((field) => {
    if (field.name === item) {
      name.value = field?.display_name;
    }
  });
  return name.value;
};

const getCustomCondition = (mappingOperation) => {
  switch (mappingOperation) {
    case 'direct':
      return '=';
    default:
      return '自定义';
  }
};

const changeApiFields = (newValue, oldValue) => {
  apiFields.value.forEach((item) => {
    if (item.key === newValue) {
      item.disabled = true;
    } else if (item.key === oldValue) {
      item.disabled = false;
    }
  });
  handleChange();
};

// 新增自定义字段
const handleAddField = () => {
  fieldSettingData.addFieldList.push({ target_field: '', mapping_operation: 'direct', source_field: '' });
  handleChange();
};

// 删除自定义字段
const handleDeleteField = (item, index) => {
  fieldSettingData.addFieldList.splice(index, 1);

  const enableField = (fields, fieldKey, fieldName) => {
    const field = fields.find(element => element[fieldKey] === fieldName);
    if (field) field.disabled = false;
  };

  enableField(fieldSettingData.field_mapping.custom_fields, 'name', item.target_field);
  enableField(apiFields.value, 'key', item.source_field);
  handleChange();
};

// 更改自定义字段
const changeCustomField = (newValue, oldValue) => {
  fieldSettingData.field_mapping.custom_fields.forEach((element) => {
    if (element.name === newValue) {
      element.disabled = true;
    } else if (element.name === oldValue) {
      element.disabled = false;
    }
  });
  handleChange();
};

const handleChange = () => {
  window.changeInput = true;
};
</script>

<style lang="less" scoped>
.operation-wrapper {
  position: relative;
  height: calc(100vh - 52px);
  background: #f5f7fa;

  .operation-content {
    padding: 0 24px 48px;

    .operation-card {
      padding-bottom: 24px;
      margin: 16px 0;
      list-style: none;
      background: #fff;
      border-radius: 2px;
      box-shadow: 0 2px 4px 0 #1919290d;

      .operation-content-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .operation-content-title {
        padding: 16px 24px;
        font-size: 14px;
        font-weight: 700;
        color: #63656e;
      }

      .operation-content-info {
        padding-left: 64px;
      }

      .flex {
        display: flex;
        align-items: center;

        li {
          width: 50%;
          margin-right: 24px;
        }
      }

      .key {
        font-size: 14px;
        color: #63656e;
      }

      .value {
        font-size: 14px;
        color: #313238;
      }

      .field-mapping-content {
        margin-left: 70px;

        ul {
          display: flex;
          width: 528px;
          height: 32px;
          margin-bottom: 8px;
          line-height: 32px;
          color: #63656e;
          background: #F5F7FA;
          border: 1px solid #EAEBF0;

          li:nth-child(1) {
            width: 247px;
            padding-left: 12px;
          }

          li:nth-child(2) {
            width: 32px;
            font-family: MicrosoftYaHei-Bold;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0;
            color: #FF9C01;
            text-align: center;
            background: #FAFBFD;
            border-right: 1px solid #EAEBF0;
            border-left: 1px solid #EAEBF0;
          }

          li:nth-child(3) {
            width: 249px;
            padding-left: 18px;
          }
        }
      }
    }
  }

  .footer {
    position: absolute;
    padding: 0 24px;

    .bk-button {
      min-width: 88px;
      margin-right: 8px;
    }
  }

  .fixed {
    position: fixed;
    bottom: 0;
    z-index: 9;
    width: 100%;
    height: 48px;
    margin-bottom: 0;
    line-height: 48px;
    background: #FAFBFD;
    box-shadow: 0 -1px 0 0 #DCDEE5;
  }
}
</style>

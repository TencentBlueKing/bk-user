<template>
  <div class="operation-wrapper user-scroll-y">
    <div class="operation-content">
      <div class="operation-card">
        <p class="operation-content-title">{{ $t('源租户信息') }}</p>
        <ul class="operation-content-info flex">
          <li>
            <span class="key">{{ $t('租户名称') }}：</span>
            <span class="value">{{ formData.source_tenant_name }}</span>
          </li>
          <li>
            <span class="key">{{ $t('租户ID') }}：</span>
            <span class="value">{{ formData.source_tenant_id }}</span>
          </li>
        </ul>
      </div>
      <div class="operation-card">
        <p class="operation-content-title">{{ $t('协同数据选择') }}</p>
        <ul class="operation-content-info">
          <li>
            <span class="key">{{ $t('已协同') }}：</span>
            <span class="value">{{ $t('所有部门 + 用户') }}</span>
          </li>
        </ul>
      </div>
      <div class="operation-card" v-bkloading="{ loading: isLoading }">
        <div class="operation-content-header">
          <p class="operation-content-title">{{ $t('字段映射') }}</p>
          <bk-button
            v-if="!isEdit"
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
          ref="formRef"
          :model="fieldSettingData"
          :rules="rulesFieldSetting">
          <FieldMapping
            :field-setting-data="fieldSettingData"
            :api-fields="apiFields"
            :rules="rulesFieldSetting"
            :source-field="$t('本租户用户字段')"
            :target-field="$t('源租户用户字段')"
            :disabled-builtin-field="true"
            @change-api-fields="changeApiFields"
            @handle-add-field="handleAddField"
            @handle-delete-field="handleDeleteField"
            @change-custom-field="changeCustomField" />
          <div class="ml-[64px]">
            <bk-button
              class="min-w-[64px] mr-[8px]"
              theme="primary"
              @click="saveEdit">
              {{ $t('保存') }}
            </bk-button>
            <bk-button
              class="min-w-[64px]"
              @click="cancelEdit">
              {{ $t('取消') }}
            </bk-button>
          </div>
        </bk-form>
        <div v-else class="field-mapping-content">
          <ul
            v-for="(item, index) in fieldSettingData.field_mapping.builtin_fields"
            :key="index">
            <li>{{`${item.display_name}（${item.name}）`}}</li>
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
    <div class="footer fixed" v-if="config.type === 'edit'">
      <bk-button theme="primary" :disabled="isEdit" @click="handleSave">
        {{ $t('确认并同步') }}
      </bk-button>
      <bk-button :disabled="isEdit" @click="$emit('cancel')">
        {{ $t('取消') }}
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { defineEmits, defineProps, onMounted, reactive, ref } from 'vue';

import FieldMapping from '@/components/field-mapping/FieldMapping.vue';
import { useValidate } from '@/hooks';
import {
  getFields,
  getSourceTenantCustomFields,
  putFromStrategies,
  putFromStrategiesConfirm,
} from '@/http';
import { t } from '@/language';

const props = defineProps({
  config: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(['updateList', 'cancel']);

const validate = useValidate();

const formData = reactive(props.config.data);

const isEdit = ref(false);
const isLoading = ref(false);
const formRef = ref();

const rulesFieldSetting = {
  target_field: [validate.required],
  source_field: [validate.required],
};

const apiFields = ref([]);
const fieldSettingData = reactive({
  field_mapping: {
    // 内置字段
    builtin_fields: [],
    // 自定义字段
    custom_fields: [],
  },
  addFieldList: [],
});

onMounted(() => {
  initFields();
});

// 初始化字段映射
const initFields = async () => {
  try {
    isLoading.value = true;
    if (formData.target_config?.field_mapping) {
      fieldSettingData.addFieldList = JSON.parse(JSON.stringify(formData.target_config.field_mapping));
    }

    const [fieldsRes, customRes] = await Promise.all([getFields(), getSourceTenantCustomFields(formData.id)]);

    const mapFields = (fields, isDisabled, fieldMappingType) => {
      Object.assign(fields, {
        mapping_operation: 'direct',
        source_field: fields.name,
        disabled: isDisabled,
      });

      if (fieldMappingType !== 'source_fields') {
        const targetFieldList = fieldSettingData.field_mapping[fieldMappingType];
        targetFieldList.push(fields);
      }

      const filterKeys = new Set(fieldSettingData.addFieldList?.map(item => (fieldMappingType === 'custom_fields'
        ? item.target_field
        : item.source_field
      )));
      fields.disabled = filterKeys.has(fields.name);

      if (fieldMappingType === 'custom_fields') {
        fieldSettingData.field_mapping.custom_fields?.forEach((item) => {
          if (filterKeys.has(item.name)) {
            item.disabled = true;
          }
        });
      } else if (fieldMappingType === 'source_fields') {
        apiFields.value.push({ key: fields.name, disabled: isDisabled, display_name: fields.display_name });
        apiFields.value.forEach((item) => {
          if (filterKeys.has(item.key)) {
            item.disabled = true;
          }
        });
      }
    };
    // 自定义字段的数据来源是本租户的自定义字段
    fieldsRes.data?.builtin_fields?.forEach(field => mapFields(field, true, 'builtin_fields'));
    fieldsRes.data?.custom_fields?.forEach(field => mapFields(field, false, 'custom_fields'));
    customRes?.data?.forEach(field => mapFields(field, false, 'source_fields'));
  } finally {
    isLoading.value = false;
  }
};

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

// 取消编辑
const cancelEdit = () => {
  isEdit.value = false;
  apiFields.value = [];
  fieldSettingData.addFieldList = [];
  fieldSettingData.field_mapping.builtin_fields = [];
  fieldSettingData.field_mapping.custom_fields = [];
  initFields();
};

const saveEdit = async () => {
  await formRef.value.validate();
  if (props.config.type === 'view') {
    await handleSave();
    isEdit.value = false;
  } else {
    isEdit.value = false;
  }
};

const handleSave = async () => {
  const params = {
    id: formData.id,
    target_config: {
      organization_scope_type: 'all',
      organization_scope_config: {},
      field_mapping: fieldSettingData.addFieldList,
    },
  };

  props.config.type === 'view' ? await putFromStrategies(params) : await putFromStrategiesConfirm(params);
  Message({ theme: 'success', message: t('更新成功') });
  emit('updateList');
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

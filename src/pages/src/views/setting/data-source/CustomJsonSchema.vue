<template>
  <div class="json-schema-container" v-if="formData.plugin_config.plugin_id">
    <template v-if="props.curStep === 1">
      <SchemaForm
        ref="schemaFormRef"
        :form-data="formData"
        :plugins-config="jsonSchema"
        class="json-schema-form"
        @change-plugin-config="changePluginConfig" />
      <div class="btn">
        <div>
          <bk-button
            class="mr-[8px]"
            theme="primary"
            :outline="!nextDisabled"
            :loading="connectionLoading"
            @click="handleTestConnection">{{ $t('连通性测试') }}</bk-button>
          <bk-button theme="primary" class="mr8" :disabled="nextDisabled" @click="handleNext">
            {{ $t('下一步') }}
          </bk-button>
          <bk-button @click="handleCancel">{{ $t('取消') }}</bk-button>
        </div>
        <div class="connection-alert" v-if="connectionStatus !== null">
          <bk-alert
            :theme="connectionStatus ? 'success' : 'error'"
            :show-icon="false">
            <template #title>
              <span>
                <i v-if="connectionStatus" class="user-icon icon-duihao-2" />
                <i v-else class="bk-sq-icon icon-close-fill" />
                {{ connectionText }}
              </span>
            </template>
          </bk-alert>
        </div>
      </div>
    </template>
    <bk-form
      v-else
      form-type="vertical"
      ref="formRef2"
      :model="fieldSettingData"
      :rules="rulesFieldSetting">
      <Row :title="$t('字段映射')">
        <FieldMapping
          :field-setting-data="fieldSettingData"
          :api-fields="apiFields"
          :rules="rulesFieldSetting"
          :source-field="$t('用户管理字段')"
          :target-field="$t('API返回字段')"
          @change-api-fields="changeApiFields"
          @handle-add-field="handleAddField"
          @handle-delete-field="handleDeleteField"
          @change-custom-field="changeCustomField" />
      </Row>
      <Row :title="$t('同步配置')">
        <bk-form-item :label="$t('同步周期')" required>
          <bk-select
            class="w-[560px]"
            :clearable="false"
            v-model="fieldSettingData.sync_config.sync_period"
            @change="handleChange">
            <bk-option
              v-for="item in SYNC_CONFIG_LIST"
              :key="item.value"
              :value="item.value"
              :label="item.label"
            />
          </bk-select>
        </bk-form-item>
        <bk-form-item :label="$t('同步超时时间')" required>
          <bk-select
            class="w-[560px]"
            :clearable="false"
            v-model="fieldSettingData.sync_config.sync_timeout"
            @change="handleChange">
            <bk-option
              v-for="item in SYNC_TIMEOUT_LIST"
              :key="item.value"
              :value="item.value"
              :label="item.label"
            />
          </bk-select>
        </bk-form-item>
        <div class="btn">
          <bk-button class="mr8" @click="handleLastStep">{{ $t('上一步') }}</bk-button>
          <bk-button theme="primary" class="mr8" :loading="submitLoading" @click="handleSubmit">
            {{ dataSourceId ? $t('保存') : $t('提交') }}
          </bk-button>
          <bk-button @click="handleCancel">{{ $t('取消') }}</bk-button>
        </div>
      </Row>
    </bk-form>
  </div>

</template>

<script setup lang="ts">
import { defineEmits, inject, onMounted, reactive, ref, watch } from 'vue';

import FieldMapping from '@/components/field-mapping/FieldMapping.vue';
import Row from '@/components/layouts/ItemRow.vue';
import SchemaForm from '@/components/schema-form/SchemaForm.vue';
import { useValidate } from '@/hooks';
import { getCustomPlugin, getDataSourceDetails, getFields, newDataSource, postTestConnection, putDataSourceDetails } from '@/http';
import { t } from '@/language/index';
import router from '@/router/index';
import { SYNC_CONFIG_LIST, SYNC_TIMEOUT_LIST } from '@/utils';
const props = defineProps({
  currentType: {
    type: String,
  },
  dataSourceId: {
    type: String,
  },
  isReset: {
    type: Boolean,
    default: false,
  },
  curStep: {
    type: Number,
  },
});

const emit = defineEmits(['updateCurStep', 'updateSuccess']);

const formData = reactive({
  plugin_config: {},
});
const jsonSchema = ref({});
const schemaFormRef = ref();
const formRef2 = ref();
const fieldSettingData = ref({
  field_mapping: {
    // 内置字段
    builtin_fields: [],
    // 自定义字段
    custom_fields: [],
  },
  // 同步配置
  sync_config: {
    sync_period: 24 * 60,
    sync_timeout: 60 * 60,
  },
  addFieldList: [],
});
const submitLoading = ref(false);

const validate = useValidate();
const rulesFieldSetting = {
  target_field: [validate.required],
  source_field: [validate.required],
};
const apiFields = ref([]);
const fieldMappingList = ref([]);

const getJsonSchema = () => {
  getCustomPlugin(props.currentType).then((res) => {
    jsonSchema.value = res.data?.json_schema;
  });
};
const changePluginConfig = (value: any) => {
  if (value instanceof Event) return;
  formData.plugin_config = value;
};
const nextDisabled = ref(true);
const connectionLoading = ref(false);
const connectionStatus = ref(null);
const connectionText = ref('');
const userProperties = ref([]);
const isLoading = ref(false);

const defaultServerConfig = () => ({
  plugin_id: '',
  server_config: {
    server_base_url: '',
    user_api_path: '',
    user_api_query_params: [],
    department_api_path: '',
    department_api_query_params: [],
    request_timeout: 5,
    retries: 3,
    page_size: 100,
  },
  auth_config: {},
});

const handleCancel = () => {
  router.push({ name: 'dataSource' });
};

// 连通性测试
const handleTestConnection = async () => {
  try {
    await schemaFormRef.value.element.validate();
    connectionLoading.value = true;
    connectionStatus.value = null;
    const params = {
      plugin_id: props.currentType,
      plugin_config: formData.plugin_config,
    };
    const res = await postTestConnection(params);
    if (res.data.error_message === '') {
      connectionStatus.value = true;
      connectionText.value = t('测试成功');
      nextDisabled.value = false;
      userProperties.value = Object.keys(res.data?.user?.properties);
    } else {
      connectionStatus.value = false;
      connectionText.value = res.data.error_message;
      nextDisabled.value = true;
    }
  } catch (e) {
    console.warn(e);
  } finally {
    connectionLoading.value = false;
  }
};

const handleNext = async () => {
  try {
    emit('updateCurStep', 2);
    isLoading.value = true;
    const res = await getFields();
    if (props?.dataSourceId) {
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
          fieldSettingData.value.field_mapping.builtin_fields.push(fields);
        } else {
          fieldSettingData.value.addFieldList.push(item);
          fieldSettingData.value.field_mapping.custom_fields.push(fields);
        }
      };

      fieldMappingList.value.forEach((item) => {
        res.data?.builtin_fields?.forEach(fields => mapFields(fields, item, true, 'builtin_fields'));
        res.data?.custom_fields?.forEach(fields => mapFields(fields, item, true, 'custom_fields'));
      });

      const filterKeys = new Set(apiFields.value.map(item => item.key));

      const addApiField = (fields, isDisabled) => {
        if (!filterKeys.has(fields.name)) {
          apiFields.value.push({ key: fields.name, disabled: isDisabled });
          filterKeys.add(fields.name);
        }
      };

      res.data?.custom_fields?.concat(res.data?.builtin_fields || []).forEach((fields) => {
        if (!customList.includes(fields.name)) {
          fieldSettingData.value.field_mapping.custom_fields.push(fields);
        }
      });

      userProperties.value.forEach(item => addApiField({ name: item }, false));
    } else {
      const { builtin_fields: builtinFields, custom_fields: customFields } = res.data || {};

      const updateFields = (fields, isBuiltin) => {
        fields.forEach((field) => {
          Object.assign(field, {
            mapping_operation: 'direct',
            source_field: '',
            disabled: isBuiltin && !field.required,
          });

          const target = isBuiltin && field.required ? 'builtin_fields' : 'custom_fields';
          fieldSettingData.value.field_mapping[target].push(field);

          if (isBuiltin && !field.required) {
            fieldSettingData.value.addFieldList.push({
              mapping_operation: 'direct',
              source_field: '',
              target_field: field.name,
            });
          }
        });
      };

      updateFields(builtinFields, true);
      updateFields(customFields, false);

      apiFields.value = userProperties.value.map(item => ({ key: item, disabled: false }));
    }
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
};

const editLeaveBefore = inject('editLeaveBefore');
const handleLastStep = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }

  nextDisabled.value = true;
  connectionStatus.value = null;
  emit('updateCurStep', 1);

  fieldSettingData.value.field_mapping.builtin_fields = [];
  fieldSettingData.value.field_mapping.custom_fields = [];
  apiFields.value = [];
  fieldSettingData.value.addFieldList = [];
  if (props?.dataSourceId) {
    const res = await getDataSourceDetails(props.dataSourceId);
    fieldSettingData.value.sync_config = res.data?.sync_config;
  } else {
    fieldSettingData.value.sync_config.sync_period = 24 * 60;
  }
};

const handleSubmit = async () => {
  try {
    await formRef2.value.validate();
    submitLoading.value = true;

    const list = fieldSettingData.value.field_mapping.builtin_fields.map(item => ({
      target_field: item.name,
      mapping_operation: item.mapping_operation,
      source_field: item.source_field,
    }));

    const params = {
      plugin_config: formData.plugin_config,
      field_mapping: [
        ...list,
        ...fieldSettingData.value.addFieldList,
      ],
      sync_config: fieldSettingData.value.sync_config,
    };

    if (props?.dataSourceId) {
      params.id = props.dataSourceId;
      await putDataSourceDetails(params);
      emit('updateSuccess', t('更新'));
    } else {
      params.plugin_id = props.currentType;
      await newDataSource(params);
      emit('updateSuccess', t('新建成功'));
    }
    window.changeInput = false;
  } catch (e) {
    console.warn(e);
  } finally {
    submitLoading.value = false;
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
  fieldSettingData.value.addFieldList.push({ target_field: '', mapping_operation: 'direct', source_field: '' });
  handleChange();
};

// 删除自定义字段
const handleDeleteField = (item, index) => {
  fieldSettingData.value.addFieldList.splice(index, 1);

  const enableField = (fields, fieldKey, fieldName) => {
    const field = fields.find(element => element[fieldKey] === fieldName);
    if (field) field.disabled = false;
  };

  enableField(fieldSettingData.value.field_mapping.custom_fields, 'name', item.target_field);
  enableField(apiFields.value, 'key', item.source_field);
  handleChange();
};

// 更改自定义字段
const changeCustomField = (newValue, oldValue) => {
  fieldSettingData.value.field_mapping.custom_fields.forEach((element) => {
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
  nextDisabled.value = true;
  connectionStatus.value = null;
};

// 重置数据
watch(() => props.isReset, () => {
  if (props.curStep === 1) {
    nextDisabled.value = true;
    connectionStatus.value = null;
    formData.plugin_config = defaultServerConfig();
  } else {
    const { field_mapping: fieldMapping, addFieldList, sync_config: syncConfig } = fieldSettingData.value;
    fieldMapping.builtin_fields.forEach(item => item.source_field = '');
    addFieldList.forEach(item => item.source_field = '');
    apiFields.value.forEach(item => item.disabled = false);
    syncConfig.sync_period = 24 * 60;
  }
});

onMounted(async () => {
  try {
    isLoading.value = true;
    getJsonSchema();
    if (props?.dataSourceId) {
      const res = await getDataSourceDetails(props.dataSourceId);
      formData.plugin_config.plugin_id = res.data?.plugin?.id;
      if (JSON.stringify(res.data?.plugin_config) !== '{}') {
        formData.plugin_config.server_config = res.data?.plugin_config?.server_config;
        formData.plugin_config.auth_config = res.data?.plugin_config?.auth_config;
      }
      fieldSettingData.value.sync_config = res.data?.sync_config;
      fieldMappingList.value = res.data?.field_mapping;
    } else {
      formData.plugin_config = defaultServerConfig();
    }
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style lang="less" scoped>
.json-schema-container {
  padding: 24px;
  margin-bottom: 0;
  border-bottom: 1px solid #EAEBF0;
  background: #FFF;
  border-radius: 2px;
  box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05098);
  .json-schema-form {
    ::v-deep .bk-schema-form-group {
      padding: 0 4px;
    }
  }
  .btn {
    position: relative;
    padding: 24px;

    button {
      min-width: 88px;
    }

    .connection-alert {
      width: 100%;
      margin-top: 8px;
    }

    .icon-close-fill {
      font-size: 14px;
      color: #EA3636;
    }

    .icon-duihao-2 {
      font-size: 14px;
      color: #2DCB56;
    }
  }
}
</style>

<template>
  <bk-loading :loading="isLoading" class="data-source-content user-scroll-y">
    <bk-form
      v-if="props.curStep === 1 && serverConfigData.plugin_id"
      form-type="vertical"
      ref="formRef1"
      :model="serverConfigData"
      :rules="rulesServerConfig">
      <Row :title="$t('服务配置')">
        <bk-form-item class="w-[560px]" :label="$t('服务地址')" property="server_config.server_base_url" required>
          <bk-input
            v-model="serverConfigData.server_config.server_base_url"
            :placeholder="validate.serverBaseUrl.message"
            @focus="handleFocus"
            @input="handleChange" />
        </bk-form-item>
        <div class="api-url-style">
          <bk-form-item
            class="w-[560px] mr-[24px]"
            :label="$t('用户数据 API 路径')"
            property="server_config.user_api_path"
            required>
            <bk-input
              v-model="serverConfigData.server_config.user_api_path"
              :placeholder="validate.apiPath.message"
              @focus="handleFocus"
              @input="handleChange" />
          </bk-form-item>
          <QueryParams
            :current-id="dataSourceId"
            :params-list="serverConfigData.server_config.user_api_query_params"
            @save-params="(list) => saveParams(list, 'user')"
            @update-status="handleChange" />
        </div>
        <div class="api-url-style">
          <bk-form-item
            class="w-[560px] mr-[24px]"
            :label="$t('部门数据 API 路径')"
            property="server_config.department_api_path"
            required>
            <bk-input
              v-model="serverConfigData.server_config.department_api_path"
              :placeholder="validate.apiPath.message"
              @focus="handleFocus"
              @input="handleChange" />
          </bk-form-item>
          <QueryParams
            :current-id="dataSourceId"
            :params-list="serverConfigData.server_config.department_api_query_params"
            @save-params="(list) => saveParams(list, 'department')"
            @update-status="handleChange" />
        </div>
        <div class="flex w-[560px]">
          <bk-form-item class="flex-1" :label="$t('分页请求每页数量')" property="server_config.page_size" required>
            <bk-select
              :clearable="false"
              v-model="serverConfigData.server_config.page_size"
              @change="handleChange">
              <bk-option
                v-for="item in pageSizeList"
                :key="item.value"
                :value="item.value"
                :label="item.label"
              />
            </bk-select>
          </bk-form-item>
          <bk-form-item
            class="ml-[24px] flex-1"
            :label="$t('请求超时时间')"
            property="server_config.request_timeout"
            required>
            <bk-input
              type="number"
              :suffix="$t('秒')"
              :min="5"
              :max="120"
              v-model="serverConfigData.server_config.request_timeout"
              @change="handleChange"
            />
          </bk-form-item>
          <bk-form-item class="ml-[24px] flex-1" :label="$t('重试次数')" property="server_config.retries" required>
            <bk-input
              type="number"
              :suffix="$t('次')"
              :min="0"
              :max="3"
              v-model="serverConfigData.server_config.retries"
              @change="handleChange"
            />
          </bk-form-item>
        </div>
      </Row>
      <Row :title="$t('认证配置')">
        <bk-form-item :label="$t('认证方式')" required>
          <bk-radio-group
            v-model="serverConfigData.auth_config.method"
            @change="handleChange"
          >
            <bk-radio-button style="width: 120px;" label="bearer_token">Bearer Token</bk-radio-button>
            <bk-radio-button style="width: 120px;" label="basic_auth">Basic Auth</bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item
          v-if="serverConfigData.auth_config.method === 'bearer_token'"
          class="w-[560px]"
          label="Token"
          property="auth_config.bearer_token"
          required>
          <bk-input
            type="password"
            autocomplete="new-password"
            v-model="serverConfigData.auth_config.bearer_token"
            @focus="handleFocus"
            @input="handleChange" />
        </bk-form-item>
        <div v-else class="item-flex w-[560px]">
          <bk-form-item :label="$t('用户名')" property="auth_config.username" required>
            <bk-input
              v-model="serverConfigData.auth_config.username"
              @focus="handleFocus"
              @input="handleChange"
            />
          </bk-form-item>
          <bk-form-item :label="$t('密码')" property="auth_config.password" required>
            <passwordInput
              v-model="serverConfigData.auth_config.password"
              :value="serverConfigData.auth_config.password"
              @focus="handleFocus"
              @input="handleChange" />
          </bk-form-item>
        </div>
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
      </Row>
    </bk-form>
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
        <div class="btn">
          <bk-button class="mr8" @click="handleLastStep">{{ $t('上一步') }}</bk-button>
          <bk-button theme="primary" class="mr8" :loading="submitLoading" @click="handleSubmit">
            {{ dataSourceId ? $t('保存') : $t('提交') }}
          </bk-button>
          <bk-button @click="handleCancel">{{ $t('取消') }}</bk-button>
        </div>
      </Row>
    </bk-form>
  </bk-loading>
</template>

<script setup lang="ts">
import { inject, onMounted, ref, watch } from 'vue';

import QueryParams from './query-params/QueryParams.vue';

import FieldMapping from '@/components/field-mapping/FieldMapping.vue';
import Row from '@/components/layouts/row.vue';
import passwordInput from '@/components/passwordInput.vue';
import { useValidate } from '@/hooks';
import {
  getDataSourceDetails,
  getFields,
  newDataSource,
  postTestConnection,
  putDataSourceDetails,
} from '@/http';
import { t } from '@/language/index';
import router from '@/router/index';
import { SYNC_CONFIG_LIST } from '@/utils';

const validate = useValidate();

const props = defineProps({
  curStep: {
    type: Number,
  },
  dataSourceId: {
    type: Number,
  },
  isReset: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['updateCurStep', 'updateSuccess']);

const isLoading = ref(false);
const formRef1 = ref();
const editLeaveBefore = inject('editLeaveBefore');

const formRef2 = ref();

const defaultServerConfig = () => ({
  plugin_id: 'general',
  server_config: {
    server_base_url: '',
    user_api_path: '',
    user_api_query_params: [{ key: '', value: '' }],
    department_api_path: '',
    department_api_query_params: [{ key: '', value: '' }],
    request_timeout: '5',
    retries: '3',
    page_size: 100,
  },
  auth_config: {
    method: 'bearer_token',
    bearer_token: '',
    username: '',
    password: '',
  },
});

const serverConfigData = ref({});

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
  },
  addFieldList: [],
});

// 重置数据
watch(() => props.isReset, () => {
  if (props.curStep === 1) {
    nextDisabled.value = true;
    connectionStatus.value = null;
    serverConfigData.value = defaultServerConfig();
  } else {
    const { field_mapping: fieldMapping, addFieldList, sync_config: syncConfig } = fieldSettingData.value;
    fieldMapping.builtin_fields.forEach(item => item.source_field = '');
    addFieldList.forEach(item => item.source_field = '');
    apiFields.value.forEach(item => item.disabled = false);
    syncConfig.sync_period = 24 * 60;
  }
});

const pageSizeList = ref([
  {
    value: 100,
    label: '100',
  },
  {
    value: 200,
    label: '200',
  },
  {
    value: 500,
    label: '500',
  },
  {
    value: 1000,
    label: '1000',
  },
  {
    value: 2000,
    label: '2000',
  },
  {
    value: 5000,
    label: '5000',
  },
]);

const rulesServerConfig = {
  name: [validate.required, validate.name],
  'server_config.server_base_url': [validate.required, validate.serverBaseUrl],
  'server_config.user_api_path': [validate.required, validate.apiPath],
  'server_config.department_api_path': [validate.required, validate.apiPath],
  'server_config.request_timeout': [validate.required],
  'server_config.retries': [validate.required],
  'auth_config.bearer_token': [validate.required],
};

const rulesFieldSetting = {
  target_field: [validate.required],
  source_field: [validate.required],
};

const apiFields = ref([]);
const fieldMappingList = ref([]);

onMounted(async () => {
  try {
    isLoading.value = true;
    if (props?.dataSourceId) {
      const res = await getDataSourceDetails(props.dataSourceId);
      serverConfigData.value.plugin_id = res.data?.plugin?.id;
      if (JSON.stringify(res.data?.plugin_config) !== '{}') {
        serverConfigData.value.server_config = res.data?.plugin_config?.server_config;
        serverConfigData.value.auth_config = res.data?.plugin_config?.auth_config;
      }
      fieldSettingData.value.sync_config = res.data?.sync_config;
      fieldMappingList.value = res.data?.field_mapping;
    } else {
      serverConfigData.value = defaultServerConfig();
    }
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});

const saveParams = (list, type) => {
  serverConfigData.value.server_config[`${type === 'user' ? 'user' : 'department'}_api_query_params`] = list;
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

const nextDisabled = ref(true);
const connectionLoading = ref(false);
const connectionStatus = ref(null);
const connectionText = ref('');
const userProperties = ref([]);

// 连通性测试
const handleTestConnection = async () => {
  try {
    await formRef1.value.validate();
    connectionLoading.value = true;
    connectionStatus.value = null;

    const clearEmptyParams = params => (params.every(item => !item.key && !item.value) ? [] : params);
    const {
      user_api_query_params: user,
      department_api_query_params: department,
    } = serverConfigData.value.server_config;

    serverConfigData.value.server_config.user_api_query_params = clearEmptyParams(user);
    serverConfigData.value.server_config.department_api_query_params = clearEmptyParams(department);

    const params = {
      plugin_id: serverConfigData.value.plugin_id,
      plugin_config: {
        server_config: serverConfigData.value.server_config,
        auth_config: serverConfigData.value.auth_config,
      },
    };
    if (props?.dataSourceId) {
      params.data_source_id = props.dataSourceId;
    }
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

const submitLoading = ref(false);

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
      plugin_config: {
        server_config: serverConfigData.value.server_config,
        auth_config: serverConfigData.value.auth_config,
      },
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
      params.plugin_id = serverConfigData.value.plugin_id;
      await newDataSource(params);
      emit('updateSuccess', t('新建'));
    }
    window.changeInput = false;
  } catch (e) {
    console.warn(e);
  } finally {
    submitLoading.value = false;
  }
};

const handleChange = () => {
  window.changeInput = true;
  nextDisabled.value = true;
  connectionStatus.value = null;
};

const handleFocus = () => {
  window.changeInput = true;
};

const handleCancel = () => {
  router.push({ name: 'dataSource' });
};
</script>

<style lang="less" scoped>
.api-url-style {
  display: flex;
  align-items: center;

  .bk-button {
    margin-left: 24px;

    .bk-button-text {
      font-size: 12px;
    }

    .icon-canshu {
      margin-right: 5px;
      font-size: 14px;
    }
  }
}

.row-wrapper {
  padding: 0 24px;
  margin-bottom: 0;
  border-bottom: 1px solid #EAEBF0;

  &:last-child {
    border-bottom: none;
  }
}

.btn {
  position: relative;
  padding: 8px 0 32px;

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
:deep(.copy-icon) {
  right: 30px;
}
</style>

<template>
  <bk-loading :loading="isLoading" class="data-source-content user-scroll-y">
    <bk-form
      v-if="props.curStep === 1"
      form-type="vertical"
      ref="formRef1"
      :model="serverConfigData"
      :rules="rulesServerConfig">
      <div class="content-item">
        <p class="item-title">基础信息</p>
        <bk-form-item class="w-[560px]" label="数据源名称" property="name" required>
          <bk-input v-model="serverConfigData.name" @focus="handleFocus" @input="handleChange" />
        </bk-form-item>
      </div>
      <div class="content-item">
        <p class="item-title">服务配置</p>
        <bk-form-item class="w-[560px]" label="服务地址" property="server_config.server_base_url" required>
          <bk-input
            v-model="serverConfigData.server_config.server_base_url"
            placeholder="请输入服务地址，需以 https/http 开头，不得以 / 结尾"
            @focus="handleFocus"
            @input="handleChange" />
        </bk-form-item>
        <div class="api-url-style">
          <bk-form-item class="w-[560px]" label="用户数据 API 路径" property="server_config.user_api_path" required>
            <bk-input
              v-model="serverConfigData.server_config.user_api_path"
              placeholder="请输入路径，需以 / 开头"
              @focus="handleFocus"
              @input="handleChange" />
          </bk-form-item>
          <QueryParams
            :current-id="currentId"
            :params-list="serverConfigData.server_config.user_api_query_params"
            @saveParams="(list) => saveParams(list, 'user')" />
        </div>
        <div class="api-url-style">
          <bk-form-item class="w-[560px]" label="部门数据 API 路径" property="server_config.department_api_path" required>
            <bk-input
              v-model="serverConfigData.server_config.department_api_path"
              placeholder="请输入路径，需以 / 开头"
              @focus="handleFocus"
              @input="handleChange" />
          </bk-form-item>
          <QueryParams
            :current-id="currentId"
            :params-list="serverConfigData.server_config.department_api_query_params"
            @saveParams="(list) => saveParams(list, 'department')" />
        </div>
        <div class="item-flex3">
          <bk-form-item label="分页请求每页数量" property="server_config.page_size" required>
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
          <bk-form-item class="ml-[24px]" label="请求超时时间" property="server_config.request_timeout" required>
            <bk-input
              type="number"
              suffix="秒"
              :min="5"
              :max="120"
              v-model="serverConfigData.server_config.request_timeout"
              @change="handleChange"
            />
          </bk-form-item>
          <bk-form-item class="ml-[24px]" label="重试次数" property="server_config.retries" required>
            <bk-input
              type="number"
              suffix="次"
              :min="0"
              :max="3"
              v-model="serverConfigData.server_config.retries"
              @change="handleChange"
            />
          </bk-form-item>
        </div>
      </div>
      <div class="content-item">
        <p class="item-title">认证配置</p>
        <bk-form-item label="认证方式" required>
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
        <div v-else class="item-flex">
          <bk-form-item label="用户名" property="auth_config.username" required>
            <bk-input
              v-model="serverConfigData.auth_config.username"
              @focus="handleFocus"
              @input="handleChange"
            />
          </bk-form-item>
          <bk-form-item label="密码" property="auth_config.password" required>
            <bk-input
              type="password"
              v-model="serverConfigData.auth_config.password"
              @focus="handleFocus"
              @input="handleChange"
            />
          </bk-form-item>
        </div>
      </div>
      <div class="btn">
        <div>
          <bk-button
            class="w-[100px] mr-[8px]"
            theme="primary"
            :outline="!nextDisabled"
            :loading="connectionLoading"
            @click="handleTestConnection">连通性测试</bk-button>
          <bk-button theme="primary" class="mr8" :disabled="nextDisabled" @click="handleNext">下一步</bk-button>
          <bk-button @click="handleCancel">取消</bk-button>
        </div>
        <div class="connection-tips" v-if="connectionStatus !== null">
          <i :class="['bk-sq-icon', connectionStatus ? 'icon-duihao-2' : 'icon-close-fill']"></i>
          {{ connectionText }}
        </div>
      </div>
    </bk-form>
    <bk-form
      v-else
      form-type="vertical"
      ref="formRef2"
      :model="fieldSettingData"
      :rules="rulesFieldSetting">
      <div class="content-item mb-[24px]">
        <p class="item-title">字段映射</p>
        <FieldMapping
          :field-setting-data="fieldSettingData"
          :api-fields="apiFields"
          :rules="rulesFieldSetting"
          @changeApiFields="changeApiFields"
          @handleAddField="handleAddField"
          @handleDeleteField="handleDeleteField"
          @changeCustomField="changeCustomField" />
      </div>
      <div class="content-item">
        <p class="item-title">同步配置</p>
        <bk-form-item label="同步周期" required>
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
      </div>
      <div class="btn">
        <bk-button theme="primary" class="mr8" @click="handleLastStep">上一步</bk-button>
        <bk-button class="mr8" :loading="submitLoading" @click="handleSubmit">
          {{ currentId ? '保存' : '提交' }}
        </bk-button>
        <bk-button @click="handleCancel">取消</bk-button>
      </div>
    </bk-form>
  </bk-loading>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, inject, onMounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

import QueryParams from './query-params/QueryParams.vue';

import FieldMapping from '@/components/field-mapping/FieldMapping.vue';
import useValidate from '@/hooks/use-validate';
import { getDataSourceDetails, newDataSource, postTestConnection, putDataSourceDetails } from '@/http/dataSourceFiles';
import { getFields } from '@/http/settingFiles';
import router from '@/router/index';
import { SYNC_CONFIG_LIST } from '@/utils';

const validate = useValidate();

const props = defineProps({
  curStep: {
    type: Number,
  },
});

const emit = defineEmits(['updateCurStep']);

const route = useRoute();
const currentId = computed(() => route.params.id);
const isLoading = ref(false);
const formRef1 = ref();
const editLeaveBefore = inject('editLeaveBefore');

const serverConfigData = reactive({
  name: '',
  plugin_id: 'general',
  // 服务配置
  server_config: {
    server_base_url: '',
    user_api_path: '',
    user_api_query_params: [],
    department_api_path: '',
    department_api_query_params: [],
    request_timeout: '',
    retries: '',
    page_size: 100,
  },
  // 鉴权配置
  auth_config: {
    method: 'bearer_token',
    bearer_token: '',
    username: '',
    password: '',
  },
});

const formRef2 = ref();

const fieldSettingData = reactive({
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
    if (currentId.value) {
      const res = await getDataSourceDetails(currentId.value);
      serverConfigData.name = res.data?.name;
      serverConfigData.plugin_id = res.data?.plugin?.id;
      serverConfigData.server_config = res.data?.plugin_config?.server_config;
      serverConfigData.auth_config = res.data?.plugin_config?.auth_config;
      fieldSettingData.sync_config = res.data?.sync_config;
      fieldMappingList.value = res.data?.field_mapping;
    }
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});

const saveParams = (list, type) => {
  serverConfigData.server_config[`${type === 'user' ? 'user' : 'department'}_api_query_params`] = list;
};

const handleNext = async () => {
  try {
    emit('updateCurStep', 2);
    isLoading.value = true;
    const res = await getFields();
    if (currentId.value) {
      const list = [];
      const customList = [];
      const mapFields = (fields, item, isDisabled, fieldMappingType) => {
        if (fields.name !== item.target_field) return;

        list.push(item.source_field);
        Object.assign(fields, {
          mapping_operation: item.mapping_operation,
          source_field: item.source_field,
          disabled: isDisabled,
          target_field: fields.name,
        });
        fieldSettingData.field_mapping[fieldMappingType].push(fields);
        apiFields.value.push({ key: item.source_field, disabled: isDisabled });

        if (fieldMappingType === 'custom_fields') {
          fieldSettingData.addFieldList.push(item);
          customList.push(fields.name);
        }
      };

      fieldMappingList.value.forEach((item) => {
        res.data?.builtin_fields?.forEach(fields => mapFields(fields, item, true, 'builtin_fields'));
        res.data?.custom_fields?.forEach(fields => mapFields(fields, item, true, 'custom_fields'));
      });

      const filterKeys = apiFields.value.map(item => item.key);

      res.data?.builtin_fields?.forEach((fields) => {
        if (filterKeys.includes(fields.name)) return;
        apiFields.value.push({ key: fields.name, disabled: false });
      });

      res.data?.custom_fields?.forEach((fields) => {
        if (!customList.includes(fields.name)) {
          fieldSettingData.field_mapping.custom_fields.push(fields);
        }
        if (list.includes(fields.name)) return;

        Object.assign(fields, {
          mapping_operation: 'direct',
          source_field: '',
          disabled: false,
          target_field: fields.name,
        });

        apiFields.value.push({ key: fields.name, disabled: false });
      });
    } else {
      fieldSettingData.field_mapping.builtin_fields = res.data?.builtin_fields;
      fieldSettingData.field_mapping.custom_fields = res.data?.custom_fields;
      [fieldSettingData.field_mapping.builtin_fields, fieldSettingData.field_mapping.custom_fields]
        .forEach((fields) => {
          fields.forEach((item) => {
            item.mapping_operation = 'direct';
            item.source_field = '';
            apiFields.value.push({ key: item.name, disabled: false });
          });
        });
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

  fieldSettingData.field_mapping.builtin_fields = [];
  fieldSettingData.field_mapping.custom_fields = [];
  apiFields.value = [];
  fieldSettingData.addFieldList = [];
  if (currentId.value) {
    const res = await getDataSourceDetails(currentId.value);
    fieldSettingData.sync_config = res.data?.sync_config;
  } else {
    fieldSettingData.sync_config.sync_period = 24 * 60;
  }
};

const nextDisabled = ref(true);
const connectionLoading = ref(false);
const connectionStatus = ref(null);
const connectionText = ref('');

// 连通性测试
const handleTestConnection = async () => {
  try {
    await formRef1.value.validate();
    connectionLoading.value = true;
    const params = {
      plugin_id: serverConfigData.plugin_id,
      plugin_config: {
        server_config: serverConfigData.server_config,
        auth_config: serverConfigData.auth_config,
      },
    };
    if (currentId.value) {
      params.data_source_id = currentId.value;
    }
    const res = await postTestConnection(params);
    if (res.data.error_message === '') {
      connectionStatus.value = true;
      connectionText.value = '测试成功';
      nextDisabled.value = false;
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

const submitLoading = ref(false);

const handleSubmit = async () => {
  try {
    await formRef2.value.validate();
    submitLoading.value = true;

    const list = fieldSettingData.field_mapping.builtin_fields.map(item => ({
      target_field: item.name,
      mapping_operation: item.mapping_operation,
      source_field: item.source_field,
    }));

    const params = {
      name: serverConfigData.name,
      plugin_config: {
        server_config: serverConfigData.server_config,
        auth_config: serverConfigData.auth_config,
      },
      field_mapping: [
        ...list,
        ...fieldSettingData.addFieldList,
      ],
      sync_config: fieldSettingData.sync_config,
    };

    if (currentId.value) {
      params.id = currentId.value;
      await putDataSourceDetails(params);
      Message({ theme: 'success', message: '数据源更新成功' });
    } else {
      params.plugin_id = serverConfigData.plugin_id;
      await newDataSource(params);
      Message({ theme: 'success', message: '数据源创建成功' });
    }
    window.changeInput = false;
    router.push({ name: 'dataSource' });
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
@import url('./index.less');

.item-flex {
  display: flex;
  margin-bottom: 24px;

  ::v-deep .bk-form-item {
    width: 268px;
    padding-bottom: 0 !important;

    &:last-child {
      margin-left: 24px;
    }
  }
}

.item-flex3 {
  display: flex;
  margin-bottom: 24px;
  margin-left: 40px;

  ::v-deep .bk-form-item {
    width: 170px;
    padding-bottom: 0 !important;
    margin-left: 24px !important;
  }
}
</style>

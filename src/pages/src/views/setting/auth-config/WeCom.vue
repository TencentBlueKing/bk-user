<template>
  <div class="details-wrapper user-scroll-y" v-bkloading="{ loading: isLoading, zIndex: 9 }">
    <bk-form
      class="auth-source-form"
      ref="formRef"
      form-type="vertical"
      :model="formData"
      :rules="rules">
      <Row :title="$t('基本信息')">
        <bk-form-item :label="$t('名称')" property="name" required>
          <bk-input v-model="formData.name" :placeholder="validate.name.message" @change="handleChange" />
        </bk-form-item>
        <bk-form-item label="是否启用" required>
          <bk-switcher
            :value="formData.status === 'enabled'"
            size="large"
            theme="primary"
            @change="changeStatus"
          />
        </bk-form-item>
      </Row>
      <Row :title="$t('基础配置')" v-if="formData.plugin_config">
        <bk-form-item :label="$t('企业 ID')" property="plugin_config.corp_id" required>
          <bk-input v-model="formData.plugin_config.corp_id" @change="handleChange" />
        </bk-form-item>
        <bk-form-item label="Agent ID" property="plugin_config.agent_id" required>
          <bk-input v-model="formData.plugin_config.agent_id" @change="handleChange" />
        </bk-form-item>
        <bk-form-item label="Secret" property="plugin_config.secret" required>
          <bk-input type="password" v-model="formData.plugin_config.secret" @change="handleChange" />
        </bk-form-item>
      </Row>
      <Row :title="$t('登录模式')">
        <bk-form-item>
          <bk-radio-group v-model="LoginMethod">
            <bk-radio-button label="a">{{ $t('仅用于登录') }}</bk-radio-button>
            <bk-radio-button label="b" :disabled="true">{{ $t('可用于登录注册') }}</bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
      </Row>
      <Row :title="$t('登录认证匹配')">
        <div class="item-flex-header">
          <bk-form-item class="w-[236px]" :label="$t('数据源字段')" required />
          <bk-form-item class="w-[236px] auth-source-fields" :label="$t('认证源字段')" required />
        </div>
        <div v-for="(item, index) in formData.data_source_match_rules" :key="index">
          <div class="item-flex" v-for="(field, i) in item.field_compare_rules" :key="i">
            <bk-form-item
              class="w-[236px]"
              error-display-type="tooltips"
              :property="`data_source_match_rules.${index}.field_compare_rules.${i}.target_field`"
              :rules="rulesData.target_field">
              <bk-select
                v-model="field.target_field"
                @change="changeSourceField"
                @toggle="handleToggle(index)"
              >
                <bk-option
                  class="option-select"
                  v-for="option in item.targetFields"
                  :key="option.name"
                  :id="option.name"
                  :name="option.name"
                  :disabled="option.disabled">
                  <span>{{option.name}}</span>
                  <span>{{option.type}}</span>
                </bk-option>
              </bk-select>
            </bk-form-item>
            <bk-form-item
              class="w-[236px] auth-source-fields"
              error-display-type="tooltips"
              :property="`data_source_match_rules.${index}.field_compare_rules.${i}.source_field`"
              :rules="rulesData.source_field">
              <bk-input v-model="field.source_field" @focus="handleChange" />
            </bk-form-item>
            <bk-button
              text
              @click="handleAddItem(item.field_compare_rules, i)"
            >
              <i class="user-icon icon-plus-fill" />
            </bk-button>
            <bk-button
              text
              :disabled="item.field_compare_rules.length === 1"
              @click="handleDeleteItem(field.target_field, index, item.field_compare_rules, i)">
              <i :class="['user-icon icon-minus-fill', { 'forbid': item.field_compare_rules.length === 1 }]" />
            </bk-button>
          </div>
        </div>
      </Row>
    </bk-form>
    <div class="footer">
      <bk-button theme="primary" :loading="btnLoading" @click="handleSubmit">
        {{ $t('提交') }}
      </bk-button>
      <bk-button @click="emit('cancelEdit')">
        {{ $t('取消') }}
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { InfoBox, Message } from 'bkui-vue';
import { defineEmits, defineProps, onMounted, ref } from 'vue';

import Row from '@/components/layouts/row.vue';
import { useCustomPlugin, useValidate } from '@/hooks';
import { getDataSourceList, getFields, getIdpsDetails, postIdps, putIdps } from '@/http';
import { t } from '@/language/index';

const validate = useValidate();

const emit = defineEmits(['cancelEdit', 'success']);
const props = defineProps({
  dataSourceId: {
    type: String,
    default: '',
  },
  currentId: {
    type: String,
    default: '',
  },
});

const formRef = ref();
const isLoading = ref(false);
const btnLoading = ref(false);

const formData = ref({
  name: '',
  status: 'enabled',
  plugin_id: 'wecom',
  plugin_config: {
    corp_id: '',
    agent_id: '',
    secret: '',
  },
  data_source_match_rules: [
    {
      data_source_id: props?.dataSourceId,
      field_compare_rules: [
        {
          target_field: '',
          source_field: '',
        },
      ],
      targetFields: [],
    },
  ],
});

const LoginMethod = ref('a');

const rules = {
  name: [validate.required, validate.name],
  'plugin_config.corp_id': [validate.required],
  'plugin_config.agent_id': [validate.required],
  'plugin_config.secret': [validate.required],
};

const rulesData = {
  data_source_id: [validate.required],
  target_field: [validate.required],
  source_field: [validate.required, validate.sourceField],
};

const dataSourceList = ref([]);
const builtinFields = ref([]);
const customFields = ref([]);

onMounted(async () => {
  try {
    isLoading.value = true;
    const [sourceRes, fieldRes] = await Promise.all([
      getDataSourceList({ type: 'real' }),
      getFields(),
    ]);
    if (props?.currentId) {
      // 获取已配置详情
      const authRes = await getIdpsDetails(props.currentId);
      if (authRes.data?.id) {
        formData.value = authRes.data;
        formData.value.data_source_match_rules[0].data_source_id = props?.dataSourceId;
      }
    }
    // 获取数据源字段
    const sourceIds = new Set(formData.value.data_source_match_rules.map(item => item.data_source_id));

    dataSourceList.value = sourceRes.data?.map(item => ({
      key: item.id,
      name: item.name,
      disabled: sourceIds.has(item.id),
    })) || [];

    const allFields = [
      ...(fieldRes.data?.builtin_fields?.map(item => ({ ...item, type: t('内置') })) || []),
      ...(fieldRes.data?.custom_fields?.map(item => ({ ...item, type: t('自定义') })) || []),
    ];

    builtinFields.value = fieldRes.data?.builtin_fields || [];
    customFields.value = fieldRes.data?.custom_fields || [];

    formData.value.data_source_match_rules?.forEach((rule) => {
      rule.targetFields = allFields.map(field => ({
        key: field.id,
        name: field.name,
        disabled: rule.field_compare_rules.some(compareRule => compareRule.target_field === field.name),
        type: field.type,
      }));
    });
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
});

// 切换启用状态
const changeStatus = (value: boolean) => {
  if (!value) {
    InfoBox({
      title: t('确认要关闭企业微信登录吗？'),
      subTitle: t('关闭后用户将无法通过企业微信登录'),
      onConfirm() {
        formData.value.status = 'disabled';
      },
      onClosed() {
        formData.value.status = 'enabled';
      },
      quickClose: false,
    });
  } else {
    formData.value.status = 'enabled';
  }
  window.changeInput = true;
};

//  提交企业微信认证源配置信息
const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    btnLoading.value = true;
    const data = formData.value;
    data.data_source_match_rules.forEach((item) => {
      delete item.targetFields;
    });

    if (!formData.value.id) {
      const res = await postIdps(data);
      emit('success', res.data?.callback_uri);
    } else {
      await putIdps(data);
      Message({ theme: 'success', message: t('认证源更新成功') });
      emit('success');
    }
  } catch (e) {
    console.warn(e);
  } finally {
    btnLoading.value = false;
  }
};

const {
  changeSourceField,
  handleToggle,
  handleAddItem,
  handleDeleteItem,
  handleChange,
} = useCustomPlugin(
  formData,
  dataSourceList,
  builtinFields,
  customFields,
);
</script>

<style lang="less" scoped>
@import url('./WeCom.less');
</style>

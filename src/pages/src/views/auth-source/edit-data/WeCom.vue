<template>
  <bk-loading class="details-wrapper" :loading="isLoading">
    <div class="details-type">
      <img :src="authSourceData.plugin?.logo" class="w-[24px] h-[24px] mr-[15px]">
      <div>
        <p class="title">{{ authSourceData.plugin?.name }}</p>
        <p class="subtitle">{{ authSourceData.plugin?.description }}</p>
      </div>
    </div>
    <bk-form
      class="auth-source-form"
      ref="formRef"
      form-type="vertical"
      :model="formData"
      :rules="rules">
      <div class="content-item">
        <p class="item-title">基础信息</p>
        <bk-form-item class="w-[600px]" label="名称" property="name" required>
          <bk-input v-model="formData.name" @change="handleChange" />
        </bk-form-item>
      </div>
      <div class="content-item" v-if="formData.plugin_config">
        <p class="item-title">基础配置</p>
        <bk-form-item class="w-[600px]" label="企业 ID" property="plugin_config.corp_id" required>
          <bk-input v-model="formData.plugin_config.corp_id" @change="handleChange" />
        </bk-form-item>
        <bk-form-item class="w-[600px]" label="Agent ID" property="plugin_config.agent_id" required>
          <bk-input v-model="formData.plugin_config.agent_id" @change="handleChange" />
        </bk-form-item>
        <bk-form-item class="w-[600px]" label="Secret" property="plugin_config.secret" required>
          <bk-input type="password" v-model="formData.plugin_config.secret" @change="handleChange" />
        </bk-form-item>
      </div>
      <div class="content-item">
        <p class="item-title">登录模式</p>
        <bk-form-item>
          <bk-radio-group v-model="LoginMethod">
            <bk-radio-button label="a">仅用于登录</bk-radio-button>
            <bk-radio-button label="b" :disabled="true">可用于登录注册</bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
      </div>
      <div class="content-item pb-[24px]">
        <p class="item-title">数据源匹配</p>
        <div class="data-source-matching">
          <div
            :class="['matching-item', { 'hover-item': hoverItem === index }]"
            v-for="(item, index) in formData.data_source_match_rules"
            :key="index"
            @mouseenter="mouseenter(index)"
            @mouseleave="mouseleave">
            <bk-form-item
              class="w-[518px]"
              label="数据源"
              :property="`data_source_match_rules.${index}.data_source_id`"
              :rules="rulesData.data_source_id"
              required>
              <bk-select v-model="item.data_source_id" @change="changeDataSourceId">
                <bk-option
                  v-for="option in dataSourceList"
                  :key="option.key"
                  :id="option.key"
                  :name="option.name"
                  :disabled="option.disabled">
                  <span>{{option.name}}</span>
                </bk-option>
              </bk-select>
            </bk-form-item>
            <div class="item-flex-header">
              <bk-form-item class="w-[250px]" label="数据源字段" required />
              <bk-form-item class="w-[250px] auth-source-fields" label="认证源字段" required />
            </div>
            <div class="item-flex" v-for="(field, i) in item.field_compare_rules" :key="i">
              <bk-form-item
                class="w-[250px]"
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
                class="w-[250px] auth-source-fields"
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
              <span class="and" v-if="i !== 0">and</span>
            </div>
            <i
              class="bk-sq-icon icon-close-fill"
              v-if="formData.data_source_match_rules.length > 1 && hoverItem === index"
              @click="handleDelete(item, index)"></i>
            <span class="or" v-if="index !== 0">or</span>
          </div>
        </div>
        <div class="add-data-source" @click="handleAdd">
          <i class="user-icon icon-add-2"></i>
          <span>新增数据源匹配</span>
        </div>
      </div>
    </bk-form>
    <div class="footer-wrapper">
      <bk-button theme="primary" :loading="btnLoading" @click="handleSubmit">
        提交
      </bk-button>
      <bk-button @click="handleCancel">
        取消
      </bk-button>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">

import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import useValidate from '@/hooks/use-validate';
import { useCustomPlugin } from '@/hooks/useCustomPlugin';
import { getIdpsDetails } from '@/http/authSourceFiles';
import { getDataSourceList } from '@/http/dataSourceFiles';
import { getFields } from '@/http/settingFiles';
import { useMainViewStore } from '@/store/mainView';

const route = useRoute();
const validate = useValidate();
const store = useMainViewStore();

const formRef = ref();
const isLoading = ref(false);
const authSourceData = ref({});
const btnLoading = ref(false);

const formData = ref({
  name: '',
  id: route.params.id,
  plugin_config: {
    corp_id: '',
    agent_id: '',
    secret: '',
  },
  data_source_match_rules: [
    {
      data_source_id: '',
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
  name: [validate.required],
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
    const [authRes, sourceRes, fieldRes] = await Promise.all([
      getIdpsDetails(route.params.id),
      getDataSourceList(''),
      getFields(),
    ]);

    authSourceData.value = authRes.data;
    store.breadCrumbsTitle = `编辑${authSourceData.value.plugin.name}认证源`;
    formData.value = {
      ...formData.value,
      name: authRes.data.name,
      plugin_config: authRes.data?.plugin_config,
      data_source_match_rules: authRes.data?.data_source_match_rules,
    };

    const sourceIds = new Set(formData.value.data_source_match_rules.map(item => item.data_source_id));

    dataSourceList.value = sourceRes.data?.map(item => ({
      key: item.id,
      name: item.name,
      disabled: sourceIds.has(item.id),
    })) || [];

    const allFields = [
      ...(fieldRes.data?.builtin_fields?.map(item => ({ ...item, type: '内置' })) || []),
      ...(fieldRes.data?.custom_fields?.map(item => ({ ...item, type: '自定义' })) || []),
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

const {
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
} = useCustomPlugin(
  formData,
  dataSourceList,
  builtinFields,
  customFields,
  btnLoading,
  formRef,
  'edit',
);
</script>

<style lang="less" scoped>
@import url('../new-data/WeCom.less');
</style>

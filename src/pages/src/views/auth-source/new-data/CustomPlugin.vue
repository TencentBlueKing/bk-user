<template>
  <bk-loading class="details-wrapper" :loading="isLoading" :z-index="9">
    <div class="details-type">
      <img :src="plugin.logo" class="w-[24px] h-[24px] mr-[15px]">
      <div>
        <p class="title">{{ plugin.name }}</p>
        <p class="subtitle">{{ plugin.description }}</p>
      </div>
    </div>
    <div ref="cardRef">
      <bk-form
        class="auth-source-form"
        ref="formRef"
        form-type="vertical"
        :model="formData"
        :rules="rules">
        <div class="content-item">
          <p class="item-title">基础信息</p>
          <bk-form-item class="w-[600px]" label="名称" property="name" required>
            <bk-input v-model="formData.name" :placeholder="validate.name.message" @focus="handleChange" />
          </bk-form-item>
        </div>
        <div class="content-item">
          <p class="item-title">基础配置</p>
          <SchemaForm
            :plugins-config="pluginsConfig"
            :form-data="formData"
            @changePluginConfig="changePluginConfig" />
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
              :class="['matching-item', {
                'hover-item': (hoverItem === index) && formData.data_source_match_rules.length > 1
              }]"
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
          <div :class="['add-data-source', {
                 'forbid-data-source': dataSourceList.every(item => item.disabled === true)
               }]"
               @click="handleAdd">
            <i class="user-icon icon-add-2"></i>
            <span>新增数据源匹配</span>
          </div>
        </div>
      </bk-form>
    </div>
    <div class="footer-wrapper" :class="{ 'fixed': isScroll }">
      <div class="footer-div">
        <bk-button @click="emit('prev')">
          上一步
        </bk-button>
        <bk-button theme="primary" :loading="btnLoading" @click="handleSubmit">
          提交
        </bk-button>
        <bk-button @click="handleCancel">
          取消
        </bk-button>
      </div>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { debounce } from 'bkui-vue/lib/shared';
import { addListener, removeListener } from 'resize-detector';
import { defineExpose, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';

import SchemaForm from '@/components/schema-form/SchemaForm.vue';
import { useCustomPlugin, useValidate } from '@/hooks';
import { getDataSourceList, getFields, getIdpsPluginsConfig } from '@/http';

const validate = useValidate();

const emit = defineEmits(['prev']);

const props = defineProps({
  plugin: {
    type: Object,
    default: () => ({}),
  },
  boxRef: {
    type: Object,
    default: () => ({}),
  },
});

const isLoading = ref(false);
const btnLoading = ref(false);
const formRef = ref();
const formData = ref({
  name: '',
  plugin_id: props.plugin.id,
  plugin_config: {},
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
  name: [validate.required, validate.name],
};

const rulesData = {
  data_source_id: [validate.required],
  target_field: [validate.required],
  source_field: [validate.required, validate.sourceField],
};

const dataSourceList = ref([]);
const builtinFields = ref([]);
const customFields = ref([]);
const pluginsConfig = ref({});

const cardRef = ref();
const isScroll = ref(false);
// 按钮超出屏幕吸底
const handleResize = () => {
  isScroll.value = 32 >= (props.boxRef.clientHeight - cardRef.value.clientHeight - 122);
};

onMounted(async () => {
  try {
    isLoading.value = true;
    dataSourceList.value = [];
    builtinFields.value = [];
    customFields.value = [];
    const [res, fieldRes, configRes] = await Promise.all([
      getDataSourceList(''),
      getFields(),
      getIdpsPluginsConfig(props.plugin.id),
    ]);
    pluginsConfig.value = configRes.data.json_schema;
    dataSourceList.value = res.data?.map(item => ({ key: item.id, name: item.name, disabled: false })) || [];
    builtinFields.value = fieldRes.data?.builtin_fields || [];
    customFields.value = fieldRes.data?.custom_fields || [];
    formData.value.data_source_match_rules[0].targetFields.push(
      ...fieldRes.data?.builtin_fields?.map(item => ({
        key: item.id, name: item.name, disabled: false, type: '内置',
      })) || [],
      ...fieldRes.data?.custom_fields?.map(item => ({
        key: item.id, name: item.name, disabled: false, type: '自定义',
      })) || [],
    );
  } catch (error) {
    console.error(error);
  } finally {
    const listenResize = debounce(300, () => handleResize());
    addListener(props.boxRef as HTMLElement, listenResize);
    nextTick(() => handleResize());
    isLoading.value = false;
  }
});

onBeforeUnmount(() => {
  removeListener(props.boxRef as HTMLElement, handleResize);
});

const changePluginConfig = (value: any) => {
  formData.value.plugin_config = value;
};

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
  'add',
);

defineExpose({
  cardRef,
});
</script>

<style lang="less">
.info-wrapper {
  .details-url {
    .title {
      font-size: 14px;
      color: #63656E;
      text-align: left;
    }

    .content {
      display: flex;
      padding: 8px 12px;
      margin-top: 12px;
      background: #F5F7FA;
      align-items: center;
      justify-content: space-between;

      p {
        display: -webkit-box;
        width: 290px;
        overflow: hidden;
        text-align: left;
        text-overflow: ellipsis;
        word-break: break-all;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 3;
      }

      .icon-copy {
        font-size: 14px;
        color: #3A84FF;
        cursor: pointer;
      }
    }
  }

  .bk-modal-close {
    display: none;
  }
}
</style>
<style lang="less" scoped>
@import url('./WeCom.less');
</style>

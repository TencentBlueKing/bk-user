<template>
  <div class="details-wrapper user-scroll-y" v-bkloading="{ loading: isLoading, zIndex: 10 }">
    <bk-form
      class="auth-source-form"
      ref="formRef"
      form-type="vertical"
      :model="formData"
      :rules="rules">
      <Row :title="$t('基本信息')">
        <bk-form-item :label="$t('名称')" property="name" required>
          <bk-input v-model="formData.name" :placeholder="validate.loginName.message" @change="handleChange" />
        </bk-form-item>
        <bk-form-item :label="$t('是否启用')" required>
          <bk-switcher
            :value="formData.status === 'enabled'"
            size="large"
            theme="primary"
            @change="changeStatus"
          />
        </bk-form-item>
      </Row>
      <Row :title="$t('基础配置')" v-if="formData.plugin_config">
        <SchemaForm
          ref="schemaFormRef"
          :form-data="formData"
          :plugins-config="jsonSchema"
          @change-plugin-config="changePluginConfig" />
      </Row>
      <Row :title="$t('登录模式')">
        <bk-form-item>
          <bk-radio-group v-model="LoginMethod">
            <bk-radio-button label="a">{{ $t('仅用于登录') }}</bk-radio-button>
            <bk-radio-button label="b" :disabled="true">{{ $t('可用于登录注册') }}</bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
      </Row>
      <EffectiveScopeEditor
        v-model="scopeValue"
        @change="handleScopeChange"
      />
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
                  v-for="option in fieldOptions"
                  :key="option.name"
                  :id="option.name"
                  :name="option.name"
                  :disabled="item.field_compare_rules.some(c => c.target_field === option.name)">
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
              @click="handleDeleteItem(index, item.field_compare_rules, i)">
              <i :class="['user-icon icon-minus-fill', { 'forbid': item.field_compare_rules.length === 1 }]" />
            </bk-button>
          </div>
        </div>
      </Row>
    </bk-form>
    <div class="footer">
      <bk-button theme="primary" :loading="btnLoading" @click="handleSubmit" :disabled="isDisabled">
        {{ $t('提交') }}
      </bk-button>
      <bk-button @click="emit('cancel')">
        {{ $t('取消') }}
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { InfoBox, Message } from 'bkui-vue';
import { computed, nextTick, onMounted, ref, toRaw, watch } from 'vue';

import EffectiveScopeEditor from './EffectiveScopeEditor.vue';
import { buildDataSourceMatchRules } from './utils';

import Row from '@/components/layouts/ItemRow.vue';
import SchemaForm from '@/components/schema-form/SchemaForm.vue';
import { useCustomPlugin, useValidate } from '@/hooks';
import { getDataSourceList, getFields, getIdpsPluginsConfig, postIdps, putIdps } from '@/http';
import { t } from '@/language/index';

const props = defineProps({
  data: {
    type: Object,
    default: null,
  },
  pluginId: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['cancel', 'success']);

const validate = useValidate();

const formRef = ref();
const schemaFormRef = ref();
const isLoading = ref(false);
const btnLoading = ref(false);
const scopeValue = ref<number[]>([]);
const formData = ref({
  name: '',
  status: 'enabled',
  plugin_id: '',
  plugin_config: {},
  data_source_match_rules: [
    {
      data_source_id: undefined,
      field_compare_rules: [
        {
          target_field: '',
          source_field: '',
        },
      ],
    },
  ],
});

let originalData = {};
let originalScope: number[] = [];
const isDisabled = ref(true);

const LoginMethod = ref('a');

const rules = {
  name: [validate.required, validate.loginName],
};

const rulesData = {
  data_source_id: [validate.required],
  target_field: [validate.required],
  source_field: [validate.required, validate.sourceField],
};

const dataSourceList = ref([]);
const builtinFields = ref([]);
const customFields = ref([]);

// 目标字段下拉选项（全局一份，disabled 由各规则的 field_compare_rules 实时计算）
const fieldOptions = computed(() => [
  ...(builtinFields.value as Array<{ id: number; name: string }>).map(item => ({ key: item.id, name: item.name, type: t('内置') })),
  ...(customFields.value as Array<{ id: number; name: string }>).map(item => ({ key: item.id, name: item.name, type: t('自定义') })),
]);

onMounted(async () => {
  try {
    isLoading.value = true;
    const [sourceRes, fieldRes] = await Promise.all([
      getDataSourceList({ type: 'real' }),
      getFields(),
    ]);
    getJsonSchema(); // 获取自定义配置
    if (props.data?.id) {
      // 从查看态传入的详情数据直接合并回填，避免重复请求
      formData.value = { ...formData.value, ...props.data };
      scopeValue.value = props.data.data_source_match_rules?.map(item => item.data_source_id) || [];
    } else {
      // 新增态：回填插件标识和认证源名称
      formData.value.plugin_id = props.pluginId;
      formData.value.name = props.data?.name || '';
    }
    // 获取数据源字段
    const sourceIds = new Set(formData.value.data_source_match_rules.map(item => item.data_source_id));

    const availableSources = sourceRes.data || [];
    dataSourceList.value = availableSources.map(item => ({
      key: item.id,
      name: item.name || String(item.id),
      disabled: sourceIds.has(item.id),
    }));

    builtinFields.value = fieldRes.data?.builtin_fields || [];
    customFields.value = fieldRes.data?.custom_fields || [];

    originalData = JSON.parse(JSON.stringify(toRaw(formData.value)));
    originalScope = [...scopeValue.value];
    // watch(scopeValue) 回调异步执行会把 isDisabled 覆盖为 false，需等其执行完再重置
    nextTick(() => {
      isDisabled.value = !!props.data?.id;
    });
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
});

const jsonSchema = ref({});
const getJsonSchema = () => {
  getIdpsPluginsConfig(props.pluginId).then((res) => {
    jsonSchema.value = res.data?.json_schema;
  });
};
watch(formData, () => {
  isDisabled.value = props.data?.id
    ? JSON.stringify(originalData) === JSON.stringify(toRaw(formData.value))
      && JSON.stringify(scopeValue.value) === JSON.stringify(originalScope)
    : false;
}, { deep: true });
watch(scopeValue, () => {
  isDisabled.value = false;
}, { deep: true });
// 切换启用状态
const changeStatus = (value: boolean) => {
  if (!value) {
    const plugName = props.data?.name;
    InfoBox({
      title: t('确认要关闭x登录吗？', { name: plugName }),
      subTitle: t('关闭后用户将无法通过x登录', { name: plugName }),
      onConfirm() {
        formData.value.status = 'disabled';
      },
      onCancel() {
        formData.value.status = 'enabled';
      },
      quickClose: false,
    });
  } else {
    formData.value.status = 'enabled';
  }
  window.changeInput = true;
};

//  提交企自定义认证源配置信息
const handleSubmit = async () => {
  try {
    let valid = await schemaFormRef.value.element.validate().catch(() => false);
    if (!valid) return;
    valid = await formRef.value?.validate?.().catch(() => false);
    if (!valid) return;
    btnLoading.value = true;
    const data = formData.value;
    data.data_source_match_rules = buildDataSourceMatchRules(
      data.data_source_match_rules[0]?.field_compare_rules || [],
      scopeValue.value,
    );
    if (!formData.value.id) {
      const res = await postIdps(data);
      emit('success', res.data?.callback_uri);
    } else {
      await putIdps(data);
      Message({ theme: 'success', message: t('认证源更新成功') });
      emit('success', '');
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
);

const changePluginConfig = (value: any) => {
  formData.value.plugin_config = value;
};

const handleScopeChange = () => {
  window.changeInput = true;
};
</script>

<style lang="less" scoped>
@import url('./WeCom.less');
</style>

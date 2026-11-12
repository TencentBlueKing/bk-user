<template>
  <div class="details-wrapper user-scroll-y" v-bkloading="{ loading: isLoading, zIndex: 10 }">
    <bk-form
      class="auth-source-form flex flex-col gap-[16px]"
      ref="formRef"
      form-type="vertical"
      :model="formData"
      :rules="rules">
      <Row :title="$t('基本信息')" class="!pb-[8px]">
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
      <Row v-if="formData.plugin_config" :title="$t('基础配置')" class="!pb-[8px]">
        <bk-form-item :label="$t('企业 ID')" property="plugin_config.corp_id" required>
          <bk-input v-model="formData.plugin_config.corp_id" @change="handleChange" />
        </bk-form-item>
        <bk-form-item label="Agent ID" property="plugin_config.agent_id" required>
          <bk-input v-model="formData.plugin_config.agent_id" @change="handleChange" />
        </bk-form-item>
        <bk-form-item label="Secret" property="plugin_config.secret" required>
          <passwordInput
            v-model="formData.plugin_config.secret"
            @change="handleChange"
            @input="inputPassword" />
        </bk-form-item>
      </Row>
      <Row :title="$t('登录模式')" class="!pb-[8px]">
        <bk-form-item>
          <bk-radio-group v-model="LoginMethod">
            <bk-radio-button label="a">{{ $t('仅用于登录') }}</bk-radio-button>
            <bk-radio-button label="b" :disabled="true">{{ $t('可用于登录注册') }}</bk-radio-button>
          </bk-radio-group>
        </bk-form-item>
      </Row>
      <EffectiveScopeEditor
        v-model="scopedIds"
        @change="handleScopeChange"
      >
        <!-- 卡片随生效范围增删，全部删掉时不展示登录认证匹配区块 -->
        <template v-if="formData.data_source_match_rules.length" #default>
          <bk-form-item class="!mt-[16px] !mb-[12px]" :label="$t('登录认证匹配')" required />
          <DataSourceMatchCard
            v-for="(rule, index) in formData.data_source_match_rules"
            :key="rule.data_source_id"
            :data-source-id="rule.data_source_id"
            :data-source-name="getDataSourceName(rule.data_source_id)"
            :rule-index="index"
            :field-compare-rules="rule.field_compare_rules"
            :field-options="fieldOptions"
            show-header
            @remove="handleRemoveCard"
            @add="(i) => handleAddItem(rule.field_compare_rules, i)"
            @delete="(i) => handleDeleteItem(index, rule.field_compare_rules, i)"
            @change="handleChange"
          />
        </template>
      </EffectiveScopeEditor>
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
import { computed, nextTick, onMounted, ref } from 'vue';

import DataSourceMatchCard from './DataSourceMatchCard.vue';
import EffectiveScopeEditor from './EffectiveScopeEditor.vue';

import Row from '@/components/layouts/ItemRow.vue';
import passwordInput from '@/components/passwordInput.vue';
import { useCustomPlugin, useDataSourceMatch, useValidate } from '@/hooks';
import { getDataSourceList, getFields, postIdps, putIdps } from '@/http';
import { t } from '@/language/index';

const props = defineProps({
  data: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['cancel', 'success']);

const validate = useValidate();

const formRef = ref();
const isLoading = ref(false);
const btnLoading = ref(false);
const scopedIds = ref<number[]>([]);
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

const LoginMethod = ref('a');

const rules = {
  name: [validate.required, validate.loginName],
  'plugin_config.corp_id': [validate.required],
  'plugin_config.agent_id': [validate.required],
  'plugin_config.secret': [validate.required],
};

const {
  dataSourceList,
  builtinFields,
  customFields,
  fieldOptions,
  isDisabled,
  markOriginalSnapshot,
  handleRemoveCard,
  getDataSourceName,
} = useDataSourceMatch(formData, scopedIds, computed(() => !!props.data?.id));

const { handleChange, handleAddItem, handleDeleteItem } = useCustomPlugin(formData, dataSourceList);

// 切换启用状态
const changeStatus = (value: boolean) => {
  if (!value) {
    InfoBox({
      title: t('确认要关闭企业微信登录吗？'),
      subTitle: t('关闭后用户将无法通过企业微信登录'),
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

//  提交企业微信认证源配置信息
const handleSubmit = async () => {
  try {
    const valid = await formRef.value?.validate?.().catch(() => false);
    if (!valid) return;
    btnLoading.value = true;
    const data = formData.value;
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

const inputPassword = (val: string) => {
  formData.value.plugin_config.secret = val;
};

const handleScopeChange = () => {
  window.changeInput = true;
};

onMounted(async () => {
  try {
    isLoading.value = true;
    const [sourceRes, fieldRes] = await Promise.all([
      getDataSourceList({ type: 'real' }),
      getFields(),
    ]);
    if (props.data?.id) {
      // 从查看态传入的详情数据直接合并回填，避免重复请求
      formData.value = { ...formData.value, ...props.data };
      scopedIds.value = props.data.data_source_match_rules?.map(item => item.data_source_id) || [];
    } else {
      // 新增态：回填认证源名称（父组件传入的默认对象）
      formData.value.name = props.data?.name || '';
    }
    // 获取数据源字段
    const sourceIds = new Set(formData.value.data_source_match_rules.map(item => item.data_source_id));

    dataSourceList.value = sourceRes.data?.map(item => ({
      key: item.id,
      name: item.name,
      disabled: sourceIds.has(item.id),
    })) || [];

    builtinFields.value = fieldRes.data?.builtin_fields || [];
    customFields.value = fieldRes.data?.custom_fields || [];

    markOriginalSnapshot();
    nextTick(() => {
      // 回填会触发 watch(scopedIds) 把 isDisabled 覆盖为 false，这里重置为无改动状态
      isDisabled.value = !!props.data?.id;
    });
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style lang="less" scoped>
@import url('./WeCom.less');
</style>

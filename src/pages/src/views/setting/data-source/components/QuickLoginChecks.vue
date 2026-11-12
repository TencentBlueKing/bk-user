<template>
  <div class="login-options">
    <bk-checkbox
      v-bk-tooltips="{ content: localTooltip, disabled: !localTooltip, placement: 'top' }"
      class="login-option"
      :model-value="modelValue.local"
      :disabled="!isLocal || !localEnablePassword"
      @change="(value: boolean) => emit('update:modelValue', { ...modelValue, local: value })"
    >
      {{ $t('使用账密登录') }}
    </bk-checkbox>
    <bk-checkbox
      v-bk-tooltips="{ content: wecomTooltip, disabled: !wecomTooltip, placement: 'top' }"
      class="login-option"
      :model-value="modelValue.wecom"
      :disabled="!wecomExists"
      @change="(value: boolean) => emit('update:modelValue', { ...modelValue, wecom: value })"
    >
      {{ $t('使用企业微信登录') }}
    </bk-checkbox>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { t } from '@/language/index';

interface IChecked {
  local: boolean;
  wecom: boolean;
}

interface IProps {
  /** 仅本地数据源可勾选账密登录 */
  isLocal: boolean;
  /** 本地数据源是否开启密码功能，未开启时账密登录勾选禁用 */
  localEnablePassword: boolean;
  /** 企微认证源是否已创建，未创建时勾选禁用 */
  wecomExists: boolean;
  /** 登录方式勾选态，账密与企业微信各一位 */
  modelValue: IChecked;
}

const props = defineProps<IProps>();
const emit = defineEmits<{
  'update:modelValue': [value: IChecked];
}>();

/** 账密登录勾选禁用提示，未命中限制条件时为空（tooltip 不弹出） */
const localTooltip = computed(() => {
  if (!props.isLocal) return t('仅本地数据源支持账密登录');
  if (!props.localEnablePassword) return t('本地数据源未开启密码功能');
  return '';
});

/** 企微认证源尚未创建时勾选禁用 */
const wecomTooltip = computed(() => (props.wecomExists ? '' : t('尚未创建该认证源，请前往登录设置创建')));
</script>

<style lang="less" scoped>
.login-options {
  display: flex;
  gap: 24px;
}
</style>

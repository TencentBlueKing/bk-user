<template>
  <bk-input
    class="input-password"
    :type="isPassword ? 'password' : 'text'"
    v-model="modelValue"
    @keydown="handleFastClear"
  >
    <template #suffix>
      <div class="pr-[10px] flex items-center">
        <bk-button
          v-show="!isPassword"
          :disabled="isPasswordDisabled"
          v-bk-tooltips="{ content: $t('不允许查看上次保存的密码'), disabled: !isPasswordDisabled }"
          text
          class="inline-flex text-[14px] ml-[8px] mr-[8px] text-[#979BA5]"
          @click="isPassword = true">
          <eye />
        </bk-button>
        <i
          class="user-icon icon-copy text-[#3A84FF] text-[14px] "
          v-bk-tooltips="{ content: $t('复制密码') }"
          @click="copy(modelValue)" />
      </div>
    </template>
  </bk-input>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips  } from 'bkui-vue';
import { Eye } from 'bkui-vue/lib/icon';
import { ref } from 'vue';

import { copy } from '@/utils';

const modelValue = defineModel<string>({ default: '' });

const props = defineProps({
  isPasswordDisabled: {
    type: Boolean,
    default: false,
  },
  isFastClearEnable: {
    type: Boolean,
    default: false,
  },
});

const isPassword  = ref(false);

const handleFastClear = (_value: any, event: KeyboardEvent) => {
  const CLEAR_CODE = ['Delete', 'Backspace'];
  if (props.isFastClearEnable && CLEAR_CODE.includes(event?.code)) {
    modelValue.value = '';
  }
};

</script>

<style lang="less" scoped>
.bk-input {
  position: relative;
}

:deep(.bk-input--suffix-icon) {
  color:#979BA5;

  &:hover {
    color:#979BA5;
  }
}
</style>


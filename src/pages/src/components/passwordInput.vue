<template>
  <bk-input
    class="input-password"
    :type="isPassword ? 'password' : 'text'"
    v-model="inputValue"
    @change="$emit('change', inputValue)"
    @focus="$emit('focus', inputValue)"
    @input="$emit('input', inputValue); $emit('update: modelValue', inputValue)"
  >
    <template #suffix>
      <span class="copy-icon">
        <i
          class="user-icon icon-copy text-[#3A84FF] text-[14px] "
          v-bk-tooltips="{ content: $t('复制密码') }"
          @click="copy(inputValue)" />
      </span>
      <span
        v-show="!isPassword"
        class="inline-flex text-[14px] ml-[8px] mr-[8px] text-[#979BA5]"
        @click="isPassword = true">
        <eye />
      </span>
    </template>
  </bk-input>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips  } from 'bkui-vue';
import { Eye } from 'bkui-vue/lib/icon';
import { defineEmits, defineProps, ref, watch } from 'vue';

import { copy } from '@/utils';

const props = defineProps({
  modelValue: {
    type: String,
  } });
defineEmits(['change', 'focus', 'input', 'update: modelValue']);

const inputValue = ref('');

watch(() => props.modelValue, (val) => {
  inputValue.value = val;
});

const isPassword  = ref(false);

</script>

<style lang="less" scoped>
.bk-input {
  position: relative;

  .copy-icon {
    position: absolute;
    top: 50%;
    right: 30px;
    transform: translate(0,  -50%)
  }
}

:deep(.bk-input--suffix-icon) {
  color:#979BA5;

  &:hover {
    color:#979BA5;
  }
}
</style>


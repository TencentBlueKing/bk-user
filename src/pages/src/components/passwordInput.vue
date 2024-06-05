<template>
  <bk-input
    class="input-password"
    :type="isPassword ? 'password' : 'text'"
    v-model="props.value"
    @change="$emit('change', props.value)"
    @focus="$emit('focus', props.value)"
    @input="$emit('input', props.value)"
  >
    <template #suffix>
      <span class="copy-icon">
        <i class="user-icon icon-copy text-[#3A84FF] text-[14px] " @click="copy(props.value)" />
      </span>
      <span
        v-show="!isPassword"
        class="inline-flex text-[14px] ml-[8px] mr-[8px] text-[#c4c6cc] hover:text-[#313238]"
        @click="isPassword = true">
        <eye />
      </span>
    </template>
  </bk-input>
</template>

<script setup lang="ts">
import { Eye } from 'bkui-vue/lib/icon';
import { defineEmits, defineProps, ref } from 'vue';

import { copy } from '@/utils';

const props = defineProps({
  value: {
    type: String,
    default: '',
  } });
const isPassword  = ref(false);
const emit = defineEmits(['change', 'focus', 'input']);
</script>

<style lang="less" scoped>
:deep(.copy-icon) {
  position: absolute;
  top: 50%;
  right: 126px;
  transform: translate(0,  -50%)
}
</style>


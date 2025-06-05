<template>
  <bk-popover
    trigger="click"
    theme="light"
    placement="top">
    <div
      :class="innerClassName || ''"
      class="cursor-pointer h-[24px] w-[52px] rounded-[2px] hover:bg-[#E1ECFF] flex justify-center items-center">
      <eye :width="16" :height="16" fill="#3A84FF" />
      <span class="select-none ml-[4px] text-[#3A84FF]">预览</span>
    </div>
    <template #content>
      <ul class="text-[#4D4F56]">
        <li>结果预览</li>
        <li class="name-tag">zhangsan (张三)</li>
        <li class="name-tag">lisi (李四)</li>
        <li class="name-tag">wangwu (王五)</li>
      </ul>
    </template>
  </bk-popover>
</template>

<script lang="ts" setup>
import { Eye } from 'bkui-vue/lib/icon';

defineProps<{
  innerClassName: string
}>();

</script>

<style lang="less" scoped>
.name-tag {
  background-color: #F0F1F5;
  height: 24px;
  line-height: 24px;
  padding: 0 8px 0 8px;
  margin-top: 8px;
  cursor: pointer;
  user-select: none;
  border-radius: 2px;
}
</style>

<template>
  <bk-popover
    ref="popoverRef"
    trigger="click"
    theme="light"
    placement="top">
    <div
      @click="handleClickPreview"
      :class="innerClassName || ''"
      class="cursor-pointer h-[24px] w-[52px] rounded-[2px] hover:bg-[#E1ECFF] flex justify-center items-center">
      <eye :width="16" :height="16" fill="#3A84FF" />
      <span class="select-none ml-[4px] text-[#3A84FF]">{{ $t('预览') }}</span>
    </div>
    <template #content>
      <bk-loading :loading="fieldData.isPreviewLoading">
        <ul class="text-[#4D4F56] min-h-[50px]" :class="previewList.length === 0 && 'min-w-[120px]'">
          <li>{{ $t('结果预览') }}</li>
          <li
            class="name-tag"
            v-for="(item, index) in previewList"
            :key="index">
            {{ item?.display_name || '' }}
          </li>
        </ul>
      </bk-loading>
    </template>
  </bk-popover>
</template>

<script lang="ts" setup>
import { Eye } from 'bkui-vue/lib/icon';
import { ref } from 'vue';

import { useFieldData } from '@/store';

defineProps<{
  innerClassName: string
  previewList: { display_name: string }[]
}>();
const emit = defineEmits(['preview']);
const fieldData = useFieldData();
const popoverRef = ref();
const handleClickPreview = () => {
  if (!popoverRef.value.localIsShow) emit('preview');
};

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

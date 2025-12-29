<template>
  <div
    v-if="!isEdit"
    class="flex items-center text-[14px] text-[#313238]"
    :class="isShowAtFirstLine ? '!items-start' : ''"
  >
    <slot name="text"></slot>
    <div @click="handleClickEdit">
      <slot name="edit-icon">
        <i class="user-icon icon-edit"></i>
      </slot>
    </div>
  </div>
  <div
    v-else
    class="flex text-[14px] z-[1000] text-[#313238]"
  >
    <slot name="edit"></slot>
    <div
      class="flex items-center leading-auto"
      :class="isShowAtFirstLine ? '!items-start mt-[6px]' : ''"
    >
      <Button
        text
        theme="primary"
        class="mx-[12px]"
        @click="handleConfirm"
      >
        {{ $t('确定') }}
      </Button>
      <Button
        text
        theme="primary"
        @click="handleCancel"
      >
        {{ $t('取消') }}
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button } from 'bkui-vue';
import { ref } from 'vue';

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
  isShowAtFirstLine: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['edit', 'confirm', 'cancel']);

const isEdit = ref(false);

const handleClickEdit = () => {
  if (props.disabled) return;
  emit('edit');
  isEdit.value = true;
};

const handleConfirm = () => {
  emit('confirm');
  isEdit.value = false;
};

const handleCancel = () => {
  emit('cancel');
  isEdit.value = false;
};
</script>

<style lang="less" scoped>
.icon-edit {
  margin-left: 14px;
  font-size: 16px;
  color: #979BA5;
  cursor: pointer;

  &:hover {
    color: #3A84FF;
  }
}
</style>

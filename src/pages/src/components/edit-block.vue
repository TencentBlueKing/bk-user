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
    <div class="edit-block-validate-wrapper" :class="{ 'is-error': showError }">
      <slot name="edit"></slot>
      <span v-if="showError" class="error-text">
        {{ errorMessage || $t('必填项') }}
      </span>
    </div>
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
import { computed, ref } from 'vue';

interface IProps {
  disabled?: boolean;
  isShowAtFirstLine?: boolean;
  /** 是否必填校验 */
  required?: boolean;
  /** 自定义错误提示文本 */
  errorMessage?: string;
  /** 自定义空值判断函数 */
  isEmpty?: (value: any) => boolean;
}

// 使用 defineModel 双向绑定校验值
const modelValue = defineModel<any>('modelValue');

const props = withDefaults(defineProps<IProps>(), {
  disabled: false,
  isShowAtFirstLine: false,
  required: false,
});

const emit = defineEmits(['edit', 'confirm', 'cancel']);

const isEdit = ref(false);
const validationError = ref(false);

// 默认的空值判断逻辑
const defaultIsEmpty = (value: any): boolean => {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  return false;
};

// 执行校验
const validate = (): boolean => {
  if (!props.required) return true;

  const checkEmpty = props.isEmpty || defaultIsEmpty;
  const isEmpty = checkEmpty(modelValue.value);
  validationError.value = isEmpty;
  return !isEmpty;
};

// 是否显示错误提示
const showError = computed(() => {
  if (!props.required) return false;
  const checkEmpty = props.isEmpty || defaultIsEmpty;
  return validationError.value && checkEmpty(modelValue.value);
});

const handleClickEdit = () => {
  if (props.disabled) return;
  validationError.value = false; // 进入编辑态时重置错误状态
  emit('edit');
  isEdit.value = true;
};

const handleConfirm = () => {
  // 执行校验
  const isValid = validate();
  if (!isValid) {
    return; // 校验失败，保持编辑态
  }

  // 校验通过，触发 confirm 事件并关闭编辑态
  validationError.value = false;
  isEdit.value = false;
  emit('confirm');
};

const handleCancel = () => {
  validationError.value = false; // 取消时重置错误状态
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

.edit-block-validate-wrapper {
  position: relative;
  display: inline-block;

  &.is-error {
    // 为子元素的输入框添加红色边框
    :deep(.bk-input),
    :deep(.bk-select),
    :deep(.bk-textarea),
    :deep(input),
    :deep(textarea) {
      border-color: #ea3636 !important;
    }

    :deep(.bk-select .bk-input) {
      border-color: #ea3636 !important;
    }
  }

  .error-text {
    position: absolute;
    top: 100%;
    left: 0;
    display: inline-block;
    padding-top: 4px;
    font-size: 12px;
    line-height: 1;
    color: #ea3636;
    white-space: nowrap;
  }
}
</style>

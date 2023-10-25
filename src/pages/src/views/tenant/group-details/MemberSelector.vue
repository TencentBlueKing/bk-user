<template>
  <div class="member-selector-wrapper" :class="{ 'is-focus': isFocus }">
    <bk-select
      class="member-selector"
      :clearable="false"
      :collapse-tags="false"
      placeholder="请输入"
      filterable
      multiple
      multiple-mode="tag"
      :remote-method="remoteFilter"
      enable-scroll-load
      :scroll-loading="scrollLoading"
      @blur="handleCancel"
      @change="handleChange"
      @focus="handleFocus"
      @scroll-end="handleScrollEnd"
    >
      <bk-option
        v-for="item of state.list"
        :key="item.id"
        :label="item.username"
        :value="item.id"
        :disabled="item.disabled"
      >
        <img v-if="item.logo" class="logo-style" :src="item.logo" />
        <i v-else class="user-icon icon-yonghu"></i>
        <span>{{ item.username }}</span>
      </bk-option>
      <template #extension>
        <bk-button text @click="handleClick">确定</bk-button>
        <bk-button text @click="handleCancel">取消</bk-button>
      </template>
    </bk-select>
  </div>
</template>

<script setup lang="ts">
import { defineEmits, defineProps, ref } from 'vue';

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  state: {
    type: Object,
    default: () => {},
  },
  params: {
    type: Object,
    default: () => {},
  },
});

const emit = defineEmits(['update:modelValue', 'selectList', 'scrollChange', 'searchUserList']);
const isFocus = ref(false);
const scrollLoading = ref(false);
const isSearch = ref(false);

// 远程搜索人员
const remoteFilter = async (value: string) => {
  value ? isSearch.value = true : isSearch.value = false;
  await emit('searchUserList', value);
};
const handleChange = (values: string[]) => {
  emit('update:modelValue', values);
};
const handleFocus = () => {
  isFocus.value = true;
};
const handleClick = () => {
  const list = [];
  props.state.list.forEach((item) => {
    if (props.modelValue.includes(item.id)) {
      list.push(item);
    }
  });
  emit('selectList', list);
};
const handleCancel = () => {
  emit('selectList', []);
  emit('searchUserList', '');
};
const handleScrollEnd = () => {
  if (!scrollLoading.value && props.state.count > (props.params.page * 10)) {
    scrollLoading.value = true;
    setTimeout(() => {
      emit('scrollChange');
      scrollLoading.value = false;
    }, 1000);
  }
};
</script>

<style lang="less">
.bk-select {
  .bk-select-trigger {
    .bk-select-tag:not(.collapse-tag) {
      min-height: 42px;
      padding: 0 10px;
      border: 1px solid transparent;

      &:hover {
        border-color: #3a84ff;
      }
    }

    .angle-up {
      display: none !important;
    }
  }
}

.is-selected {
  background-color: #e1ecff !important;
}

.bk-select-dropdown {
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 4px;
    background-color: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background-color: #dcdee5;
    border-radius: 4px;
  }

  .logo-style {
    width: 22px;
    height: 22px;
    margin-right: 5px;
    border: 1px solid #C4C6CC;
    border-radius: 50%;
  }
}

.bk-select-extension {
  justify-content: space-around;

  .bk-button {
    width: 50%;
    height: 100%;
    border-radius: 0;

    &:first-child {
      border-right: 1px solid #dcdee5;
    }
  }
}

.icon-yonghu {
  margin-right: 5px;
  font-size: 22px;
}
</style>

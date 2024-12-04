<template>
  <div class="member-selector-wrapper" :class="{ 'is-focus': isFocus }">
    <bk-select
      class="member-selector"
      :clearable="clearable"
      :collapse-tags="false"
      :placeholder="$t('请输入')"
      v-model="curMember"
      filterable
      :multiple="multiple"
      :show-on-init="showOnInit"
      :multiple-mode="multiple ? 'tag' : 'default'"
      :remote-method="remoteFilter"
      enable-scroll-load
      :scroll-loading="scrollLoading"
      @change="handleChange"
      @focus="handleFocus"
      @scroll-end="handleScrollEnd"
    >
      <bk-option
        v-for="(item, index) in state.results"
        :key="index"
        :label="item.username"
        :value="item.id"
      >
        <i class="user-icon icon-yonghu"></i>
        <span>{{ item.username }}</span>
      </bk-option>
    </bk-select>
  </div>
</template>

<script setup lang="ts">
import { defineEmits, defineModel, defineProps, ref } from 'vue';

const props = defineProps({
  state: {
    type: Object,
    default: () => {},
  },
  params: {
    type: Object,
    default: () => {},
  },
  clearable: {
    type: Boolean,
    default: false,
  },
  showOnInit: {
    type: Boolean,
    default: true,
  },
  multiple: {
    type: Boolean,
    default: true,
  },
});
const emit = defineEmits(['changeSelectList', 'scrollChange', 'searchUserList']);
const isFocus = ref(false);
const scrollLoading = ref(false);
const isSearch = ref(false);
const curMember = defineModel<string | string[]>();

// 远程搜索人员
const remoteFilter = async (value: string) => {
  value ? isSearch.value = true : isSearch.value = false;
  await emit('searchUserList', value);
};

const handleChange = (values: string[]) => {
  emit('changeSelectList', values);
};

const handleFocus = () => {
  isFocus.value = true;
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
      padding: 0 10px;

      &:hover {
        border-color: #3a84ff;
      }
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

<template>
  <div class="no-data-wrapper">
    <bk-exception v-if="isDataEmpty" type="empty" scene="part" description="暂无数据" />
    <bk-exception v-if="isSearchEmpty" type="search-empty" scene="part">
      搜索结果为空
      <p>
        可以尝试&nbsp;调整关键词&nbsp;或&nbsp;
        <bk-button
          text
          theme="primary"
          @click="$emit('handleEmpty')">清空筛选条件
        </bk-button>
      </p>
    </bk-exception>
    <bk-exception v-if="isDataError" type="500" scene="part">
      数据获取异常
      <bk-button
        text
        theme="primary"
        class="empty-search-text"
        @click="$emit('handleUpdate')">刷新</bk-button>
    </bk-exception>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

defineProps({
  isDataEmpty: {
    type: Boolean,
    default: false,
  },
  isSearchEmpty: {
    type: Boolean,
    default: false,
  },
  isDataError: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['handleEmpty', 'handleUpdate']);
</script>

<style lang="less" scoped>
.no-data-wrapper {
  width: 100%;
  height: 100%;

  .empty-search-text {
    display: block;
    width: 100%;
    font-size: 12px;
    line-height: 20px;
    text-align: center;
  }

  :deep(.bk-exception-text.part-text) {
    line-height: 25px;

    p {
      display: flex;
      font-size: 12px;
      color: #979BA5;
    }
  }

  :deep(.bk-link-text) {
    font-size: 12px;
  }
}
</style>

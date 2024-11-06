<template>
  <div class="grid place-items-center">
    <!-- 筛选表单 -->
    <div class="filter-operation-history-container" v-if="!isFold">
      <bk-form class="w-full" form-type="vertical">
        <bk-form-item class="inline-block ml-[24px]" :label="$t('操作人')">
          <bk-input class="items-input" clearable />
        </bk-form-item>
        <bk-form-item class="inline-block ml-[20px]" :label="$t('操作类型')">
          <bk-select class="items-select">
          </bk-select>
        </bk-form-item>
        <bk-form-item class="inline-block ml-[20px]" :label="$t('操作对象')">
          <bk-select class="items-select">
          </bk-select>
        </bk-form-item>
        <bk-form-item class="inline-block ml-[20px]" :label="$t('操作实例')">
          <bk-input class="items-input" clearable />
        </bk-form-item>
        <bk-form-item class="inline-block ml-[24px]" :label="$t('操作时间')">
          <bk-date-picker class="items-picker" />
        </bk-form-item>
        <bk-form-item class="inline-block ml-[20px]" :label="$t('操作结果')">
          <bk-select class="items-select">
          </bk-select>
        </bk-form-item>
        <bk-form-item class="ml-[24px]">
          <bk-button
            class="w-[88px] h-[32px]"
            theme="primary"
            @click="() => {}"
          >
            {{ $t('查询') }}
          </bk-button>
          <bk-button
            class="w-[88px] h-[32px] ml-[8px]"
            @click="() => {}"
          >
            {{ $t('重置') }}
          </bk-button>
        </bk-form-item>

      </bk-form>
    </div>
    <!-- 折叠按钮 -->
    <div class="flex justify-center w-full">
      <div @mouseover="handleHoverFoldBtn" @mouseleave="handleLeaveFoldBtn" v-if="!isFold">
        <bk-button
          v-if="isHover" theme="primary"
          @click="toggleFold"
          class="w-[120px] h-[24px] text-bold">︿</bk-button>
        <bk-button
          v-else
          @click="toggleFold"
          class="w-[120px] h-[24px] !bg-[#DCDEE5] !text-[#ffffff] text-bold">︿</bk-button>
      </div>
      <div v-else>
        <bk-button
          theme="primary"
          @click="toggleFold"
          class="w-[120px] h-[24px] text-bold">﹀</bk-button>
      </div>
    </div>
    <!-- 展示列表 -->
    <div class="data-operation-history-container">
      <bk-table
        :pagination="pagination"
        settings
        @page-limit-change="pageLimitChange"
        @page-value-change="pageCurrentChange"
      >
        <bk-table-column :label="$t('操作人')" prop="name" width="100"></bk-table-column>
        <bk-table-column :label="$t('操作时间')" sort prop="name" width="100"></bk-table-column>
        <bk-table-column :label="$t('操作对象')" prop="name" width="100"></bk-table-column>
        <bk-table-column :label="$t('操作实例')" prop="name" width="100"></bk-table-column>
        <bk-table-column :label="$t('操作类型')" prop="name" width="100"></bk-table-column>
        <bk-table-column :label="$t('执行结果')" prop="name" width="100"></bk-table-column>
      </bk-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';

const isHover = ref(false);
const isFold = ref(false);

const pagination = reactive({
  current: 1,
  count: 0,
  limit: 10,
});
const handleHoverFoldBtn = () => {
  isHover.value = true;
};
const handleLeaveFoldBtn = () => {
  isHover.value = false;
};
const toggleFold = () => {
  isFold.value = !isFold.value;
  isHover.value = false;
};
const pageLimitChange = () => {

};

const pageCurrentChange = () => {

};
</script>

<style lang="less" scoped>
@container-width: 1312px;

.filter-operation-history-container {
  width: @container-width;
  height: 248px;
  padding: 24px 0px;
  background: #FFFFFF;
  box-shadow: 0 2px 4px 0 #1919290d;
  border-radius: 2px;

  .items-input, .items-select, .items-picker {
    width: 298px;
  }
}

.data-operation-history-container {
  width: @container-width;
}
</style>

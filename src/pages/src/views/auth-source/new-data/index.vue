<template>
  <div>
    <MainBreadcrumbsDetails @toBack="toBack">
      <template #content>
        <bk-steps
          ext-cls="steps-wrapper"
          :cur-step="curStep"
          :steps="stepsConfig"
          class="mb20"
        />
      </template>
    </MainBreadcrumbsDetails>
    <div ref="boxRef" class="user-scroll-y">
      <Config v-if="curStep === 1" @next="handleNext" />
      <div v-else>
        <WeCom
          v-if="currentPlugin.id === 'wecom'"
          :plugin="currentPlugin"
          :box-ref="boxRef"
          @prev="handlePrev" />
        <CustomPlugin
          v-else
          :plugin="currentPlugin"
          :box-ref="boxRef"
          @prev="handlePrev" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineExpose, inject, reactive, ref } from 'vue';

import Config from './config.vue';
import CustomPlugin from './CustomPlugin.vue';
import WeCom from './WeCom.vue';

import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import router from '@/router/index';

const editLeaveBefore = inject('editLeaveBefore');
const curStep = ref(1);
const stepsConfig = reactive([
  { title: '认证源选择', icon: 1 },
  { title: '登录配置', icon: 2 },
]);

const toBack = async () => {
  if (curStep.value === 2) {
    getStatus();
  } else {
    router.push({ name: 'authSourceList' });
  }
};

const currentPlugin = ref({});

const handleNext = (item) => {
  curStep.value = 2;
  currentPlugin.value = item;
};

const handlePrev = () => {
  getStatus();
};

const getStatus = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    curStep.value = 1;
  } else {
    curStep.value = 1;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};

const boxRef = ref();
defineExpose({ boxRef });
</script>

<style lang="less" scoped>
.main-breadcrumbs-details {
  .icon-arrow-left {
    margin-right: 10px;
    font-size: 18px;
    color: #3a84ff;
    cursor: pointer;
  }

  .tittle{
    margin-right: 8px;
    font-size: 16px;
    color: #313238;
  }

  .steps-wrapper {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 360px;
    transform: translate(-50%, -50%);
  }
}

.user-scroll-y {
  position: relative;
  height: calc(100vh - 104px);
  padding-bottom: 48px;
}
</style>

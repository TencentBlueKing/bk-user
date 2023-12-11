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
    <div class="user-scroll-y">
      <Config v-if="curStep === 1" @next="handleNext" />
      <div v-else>
        <WeCom
          v-if="currentPlugin.id === 'wecom'"
          :plugin="currentPlugin"
          @prev="handlePrev" />
        <CustomPlugin
          v-else
          :plugin="currentPlugin"
          @prev="handlePrev" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { inject, reactive, ref } from 'vue';

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
    width: 360px;
    margin: 0 auto;
  }
}

.user-scroll-y {
  height: calc(100vh - 104px);
}
</style>

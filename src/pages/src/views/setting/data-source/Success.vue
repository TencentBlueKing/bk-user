<template>
  <div class="success-wrapper">
    <div class="content">
      <i class="user-icon icon-duihao-2" />
      <p class="title">{{ title }}</p>
      <div>
        <bk-tag class="align-middle">
          <strong class="text-[18px]">{{ remainTime }}</strong> s
        </bk-tag>{{ $t('后将自动跳转回查看组织架构') }}
      </div>
      <div class="mt-[24px]">
        <bk-button
          class="mr-[8px]"
          theme="primary"
          @click="handleSync"
        >
          {{ $t('立即同步') }}
        </bk-button>
        <bk-button
          class="mr-[8px]"
          @click="loginConfig"
        >
          {{ $t('登录配置') }}
        </bk-button>
        <bk-button @click="viewOrganization">
          {{ $t('查看组织架构') }}
        </bk-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

import router from '@/router';

defineProps({
  title: {
    type: String,
    default: '',
  },
});

const remainTime = ref(3);
const timer = ref(0);

onMounted(() => {
  // 倒计时
  timer.value = setInterval(() => {
    remainTime.value = remainTime.value - 1;
    if (remainTime.value === 0) {
      clearInterval(timer.value);
      router.push({ name: 'organization' });
    }
  }, 1000);
});

const handleSync = () => {};

const loginConfig = () => {};

const viewOrganization = () => {
  router.push({ name: 'organization' });
};
</script>

<style>
.success-wrapper {
  position: relative;
  width: 100%;
  height: calc(100vh - 136px);
  min-height: 400px;
  text-align: center;
  background: #fff;

  .content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);

    .icon-duihao-2 {
      font-size: 56px;
      color: #2DCB56;
    }

    .title {
      margin: 21px 0 6px;
      font-size: 16px;
      color: #000;
    }
  }
}
</style>

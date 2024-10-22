<template>
  <div class="success-wrapper">
    <div class="content">
      <i class="user-icon icon-duihao-2" />
      <p class="title">{{ title }}</p>
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
import { defineProps } from 'vue';

import { useDataSource } from '@/hooks';
import router from '@/router';
import { useSyncStatus } from '@/store';

defineProps({
  title: {
    type: String,
    default: '',
  },
});

const { handleOperationsSync } = useDataSource();
const syncStatusStore = useSyncStatus();
// 同步数据后跳转到数据源配置页面
const handleSync = () => {
  handleOperationsSync();
  syncStatusStore.setRefresh(false);
  router.push({ name: 'dataSource' });
};

// 跳转到登录配置页面
const loginConfig = () => {
  router.push({ name: 'login' });
};

// 跳转到组织架构页面
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

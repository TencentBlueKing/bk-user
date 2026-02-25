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
import { Message } from 'bkui-vue';

import useDataSourceSetting from '@/hooks/useDataSourceSetting';
import { postOperationsSync } from '@/http/dataSourceFiles';
import router from '@/router';
import { useDataSourceStore, useSyncStatus } from '@/store';

interface IProps {
  title: string;
}

withDefaults(defineProps<IProps>(), {
  title: '',
});

const syncStatusStore = useSyncStatus();
const dataSourceStore = useDataSourceStore();
const { startDataSourceSync } = useDataSourceSetting();

// 同步数据后跳转到数据源配置页面
const handleSync = async () => {
  const res = await postOperationsSync(dataSourceStore.newDataSourceId);
  Message({ theme: res.data.status, message: res.data.summary });
  // more-data-source-todo
  // 新建完数据源后，若跳转到数据源列表，初始化会获取一次数据源状态
  // 若为未同步完成，则会触发轮询，因此这里真的还需要手动轮询吗？
  // 这里的pluginId是可以通过dataSourceStore.newDataSourceId获取吗？这是新建数据，看下是不是要用props处理
  const dataSource = dataSourceStore.dataSource.find(item => item.id === dataSourceStore.newDataSourceId);
  if (dataSource) {
    startDataSourceSync(dataSourceStore.newDataSourceId, dataSource.plugin_id);
  }
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

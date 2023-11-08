<template>
  <bk-loading :loading="isLoading">
    <MainBreadcrumbsDetails :subtitle="subtitle">
      <template #tag>
        <div class="data-source-type" v-for="item in typeList" :key="item">
          <img v-if="item.id === pluginId && item.logo" :src="item.logo">
          <span v-if="item.id === pluginId">{{ item.name }}</span>
        </div>
      </template>
      <template #right>
        <div>
          <bk-button
            v-if="pluginId !== 'local'"
            class="w-[88px] mr-[8px]"
            outline
            theme="primary"
            @click="handleSync">
            一键同步
          </bk-button>
          <bk-button v-if="statusText" class="w-[64px]" hover-theme="primary" @click="handleClick">
            {{ statusText === 'disabled' ? '启用' : '停用' }}
          </bk-button>
        </div>
      </template>
    </MainBreadcrumbsDetails>
    <bk-tab
      v-model:active="activeKey"
      type="unborder-card"
      ext-cls="tab-details"
      @change="changeTab"
    >
      <bk-tab-panel name="user" label="用户信息">
        <UserInfo v-if="activeKey === 'user'" :data-source-id="currentId" :plugin-id="pluginId" />
      </bk-tab-panel>
      <bk-tab-panel :visible="pluginId === 'local'" name="account" label="账密信息">
        <PswInfo v-if="activeKey === 'account'" />
      </bk-tab-panel>
      <bk-tab-panel :visible="pluginId !== 'local'" name="config" label="配置信息">
        <ConfigInfo v-if="activeKey === 'config'" />
      </bk-tab-panel>
    </bk-tab>
  </bk-loading>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import ConfigInfo from './ConfigInfo.vue';
import PswInfo from './PswInfo.vue';
import UserInfo from './UserInfo.vue';

import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import { changeSwitchStatus, getDataSourceList, getDataSourcePlugins, postOperationsSync } from '@/http/dataSourceFiles';
import router from '@/router/index';

const route = useRoute();

const currentId = computed(() => Number(route.params.id));

const activeKey = ref('user');
const isLoading = ref(false);

const subtitle = ref('');
const statusText = ref('');
const typeList = ref([]);
const pluginId = ref('');

onMounted(async () => {
  isLoading.value = true;
  const res = await getDataSourceList('');
  res.data.forEach((item) => {
    if (item.id === currentId.value) {
      statusText.value = item.status;
      subtitle.value = item.name;
      pluginId.value = item.plugin_id;
    }
  });
  const pluginsRes = await getDataSourcePlugins();
  typeList.value = pluginsRes.data;
  isLoading.value = false;
});

const handleClick = async () => {
  const res = await changeSwitchStatus(route.params.id);
  statusText.value = res.data?.status;
  const message = res.data?.status === 'disabled' ? '停用成功' : '启用成功';
  Message({ theme: 'success', message });
};

const changeTab = (value) => {
  activeKey.value = value;
};

const handleSync = async () => {
  const res = await postOperationsSync(currentId.value);
  router.push({ name: 'syncRecords' });
  const status = res.data?.status === 'failed' ? 'error' : 'success';
  Message({ theme: status, message: res.data.summary });
};
</script>

<style lang="less" scoped>
.main-breadcrumbs-details {
  box-shadow: none;
}

.data-source-type {
  display: flex;
  height: 24px;
  line-height: 24px;
  background: #f0f1f5;
  border-radius: 2px;
  align-items: center;

  img {
    width: 14px;
    height: 14px;
    margin: 0 8px 0 10px;
  }

  span {
    padding-right: 10px;
  }
}
</style>

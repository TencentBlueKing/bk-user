<template>
  <bk-loading :loading="isLoading">
    <MainBreadcrumbsDetails :subtitle="subtitle" @toBack="toBack">
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
            class="min-w-[88px] mr-[8px]"
            outline
            theme="primary"
            @click="handleSync">
            {{ $t('一键同步') }}
          </bk-button>
          <bk-button v-if="statusText" class="min-w-[64px]" hover-theme="primary" @click="handleClick">
            {{ statusText === 'disabled' ? t('启用') : t('停用') }}
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
      <bk-tab-panel name="user" :label="$t('用户信息')">
        <UserInfo
          v-if="activeKey === 'user'"
          :data-source-id="currentId"
          :plugin-id="pluginId"
          :is-password-login="isPasswordLogin" />
      </bk-tab-panel>
      <bk-tab-panel :visible="pluginId === 'local'" name="account" :label="$t('账密信息')">
        <PswInfo v-if="activeKey === 'account'" />
      </bk-tab-panel>
      <bk-tab-panel :visible="pluginId !== 'local'" name="config" :label="$t('配置信息')">
        <ConfigInfo v-if="activeKey === 'config'" />
      </bk-tab-panel>
    </bk-tab>
  </bk-loading>
</template>

<script setup lang="ts">
import { InfoBox, Message } from 'bkui-vue';
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import ConfigInfo from './ConfigInfo.vue';
import PswInfo from './PswInfo.vue';
import UserInfo from './UserInfo.vue';

import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import {
  changeSwitchStatus,
  getDataSourceDetails,
  getDataSourceList,
  getDataSourcePlugins,
  postOperationsSync,
} from '@/http/dataSourceFiles';
import { t } from '@/language/index';
import router from '@/router/index';

const route = useRoute();

const currentId = computed(() => Number(route.params.id));

const activeKey = ref('user');
const isLoading = ref(false);

const subtitle = ref('');
const statusText = ref('');
const typeList = ref([]);
const pluginId = ref('');
// 是否开启账密登录
const isPasswordLogin = ref(false);

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
  const loginRes = await getDataSourceDetails(currentId?.value);
  isPasswordLogin.value = loginRes.data?.plugin_config?.enable_account_password_login;
  typeList.value = pluginsRes.data;
  isLoading.value = false;
});
// 切换启停状态
const toggleStatus = async () => {
  const res = await changeSwitchStatus(route.params.id);
  statusText.value = res.data?.status;
  const message = res.data?.status === 'disabled' ? t('停用成功') : t('启用成功');
  Message({ theme: 'success', message });
};

const handleClick = async () => {
  if (statusText.value === 'enabled') {
    InfoBox({
      title: t('确认停用该数据源吗？'),
      subTitle: t('停用后，该数据源下所有用户将无法登录'),
      onConfirm: toggleStatus,
    });
  } else {
    toggleStatus();
  }
};

const changeTab = (value) => {
  activeKey.value = value;
};

const handleSync = async () => {
  const res = await postOperationsSync(currentId.value);
  router.push({ name: 'syncRecords', params: { type: 'sync' } });
  const status = res.data?.status === 'failed' ? 'error' : 'success';
  Message({ theme: status, message: res.data.summary });
};

const toBack = () => {
  router.push({ name: 'dataSource' });
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

::v-deep .tab-details {
  .bk-tab-content {
    height: calc(100vh - 140px);
    padding: 24px;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 4px;
      background-color: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background-color: #dcdee5;
      border-radius: 4px;
    }
  }
}
</style>

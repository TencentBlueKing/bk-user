<template>
  <bk-loading :loading="isLoading">
    <MainBreadcrumbsDetails :subtitle="subtitle">
      <template #tag>
        <bk-tag>
          <template #icon>
            <div class="datasource-type-icon" v-for="item in typeList" :key="item">
              <img v-if="item.id === pluginId && item.logo" :src="item.logo">
              <i v-else :class="dataSourceType[pluginId].icon" />
              <span>{{ dataSourceType[pluginId].text }}</span>
            </div>
          </template>
        </bk-tag>
      </template>
      <template #right>
        <bk-button class="w-[64px]" hover-theme="primary" @click="handleClick">
          {{ statusText === 'disabled' ? '启用' : '停用' }}
        </bk-button>
      </template>
    </MainBreadcrumbsDetails>
    <bk-tab
      v-model:active="activeKey"
      type="unborder-card"
      ext-cls="tab-details"
    >
      <bk-tab-panel
        v-for="item in panels"
        :key="item.name"
        :name="item.name"
        :label="item.label"
      >
        <UserInfo v-if="activeKey === 'user'" />
        <PswInfo v-else />
      </bk-tab-panel>
    </bk-tab>
  </bk-loading>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

import PswInfo from './PswInfo.vue';
import UserInfo from './UserInfo.vue';

import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import { changeSwitchStatus, getDataSourceList, getDataSourcePlugins } from '@/http/dataSourceFiles';
import { dataSourceType } from '@/utils';

const route = useRoute();

const currentId = computed(() => Number(route.params.id));

const activeKey = ref('user');
const panels = reactive([
  { name: 'user', label: '用户信息' },
  { name: 'account', label: '账密信息' },
]);

const isLoading = ref(false);

const subtitle = ref('');
const statusText = ref('');
const typeList = ref([]);
const pluginId = ref('');

onMounted(async () => {
  isLoading.value = true;
  statusText.value = route.params.status;
  const res = await getDataSourceList('');
  res.data.forEach((item) => {
    if (item.id === currentId.value) {
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
</script>

<style lang="less" scoped>
.main-breadcrumbs-details {
  box-shadow: none;
}
</style>

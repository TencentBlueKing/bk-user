<template>
  <bk-loading :loading="isLoading">
    <MainBreadcrumbsDetails :subtitle="subtitle">
      <template #tag>
        <bk-tag v-if="typeText">
          <template #icon>
            <i :class="typeIcon" />
          </template>
          {{ typeText }}
        </bk-tag>
      </template>
      <template #right>
        <bk-button v-if="statusText" class="w-[64px]" @click="handleClick">
          {{ statusText }}
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
import { changeSwitchStatus, getDataSourceList } from '@/http/dataSourceFiles';
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
const typeText = ref('');
const typeIcon = ref('');
const statusText = ref('');
const switchStatus = ref('');

onMounted(async () => {
  isLoading.value = true;
  const res = await getDataSourceList('');
  await getSwitchStatus();
  res.data.forEach((item) => {
    if (item.id === currentId.value) {
      const { text, icon } = dataSourceType[item.plugin_id];
      subtitle.value = item.name;
      typeText.value = text;
      typeIcon.value = icon;
    }
  });
  isLoading.value = false;
});

const getSwitchStatus = async () => {
  const res = await changeSwitchStatus(route.params.id);
  switchStatus.value = res.data?.status;
  statusText.value = res.data?.status === 'disabled' ? '启用' : '停用';
};

const handleClick = async () => {
  await getSwitchStatus();
  const message = switchStatus.value === 'disabled' ? '停用成功' : '启用成功';
  Message({ theme: 'success', message });
};
</script>

<style lang="less">
.main-breadcrumbs-details {
  box-shadow: none;
}
</style>

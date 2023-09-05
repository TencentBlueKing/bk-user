<template>
  <div>
    <MainBreadcrumbsDetails :subtitle="subtitle">
      <template #tag>
        <bk-tag>
          <template #icon>
            <i :class="typeText.icon" />
          </template>
          {{ typeText.text }}
        </bk-tag>
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
        <UserInfo
          v-if="activeKey === 'user'"
          :users="state.users"
          :is-loading="state.isLoading"
          :data-source-id="currentId"
          :is-data-empty="state.isDataEmpty"
          :is-empty-search="state.isEmptySearch"
          :is-data-error="state.isDataError"
          :pagination="state.pagination"
          @updateUsers="updateUsers"
          @updatePageLimit="updatePageLimit"
          @updatePageCurrent="updatePageCurrent" />
        <PswInfo v-else />
      </bk-tab-panel>
    </bk-tab>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

import PswInfo from './PswInfo.vue';
import UserInfo from './UserInfo.vue';

import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import { getDataSourceUsers } from '@/http/dataSourceFiles';
import { dataSourceType } from '@/utils';

const route = useRoute();

// 当前面包屑展示文案
const subtitle = computed(() => route.params.name);
const typeText = computed(() => {
  const { text, icon } = dataSourceType[route.params.type];
  return { text, icon };
});
const currentId = computed(() => Number(route.params.id));

const activeKey = ref('user');
const panels = reactive([
  { name: 'user', label: '用户信息' },
  { name: 'account', label: '账密信息' },
]);

const state = reactive({
  isLoading: false,
  users: [],
  departments: [],
  // 搜索结果为空
  isEmptySearch: false,
  // 表格请求出错
  isDataError: false,
  // 表格请求结果为空
  isDataEmpty: false,
  pagination: {
    current: 1,
    count: 0,
    limit: 10,
  },
});

const params = reactive({
  id: currentId.value,
  username: '',
  page: 1,
  pageSize: 10,
});

const getUsers = async () => {
  try {
    state.isLoading = true;
    state.isDataEmpty = false;
    state.isEmptySearch = false;
    state.isDataError = false;
    const res = await getDataSourceUsers(params);
    if (res.data.count === 0) {
      params.username === '' ? state.isDataEmpty = true : state.isEmptySearch = true;
    }
    state.pagination.count = res.data.count;
    state.users = res.data.results;
    state.isLoading = false;
  } catch (error) {
    state.isDataError = true;
  } finally {
    state.isLoading = false;
  }
};
getUsers();

const updateUsers = (value: string) => {
  params.username = value;
  getUsers();
};

const updatePageLimit = (limit) => {
  state.pagination.limit = limit;
  params.pageSize = limit;
  getUsers();
};
const updatePageCurrent = (current) => {
  state.pagination.current = current;
  params.page = current;
  getUsers();
};
</script>

<style lang="less">
.main-breadcrumbs-details {
  box-shadow: none;
}
</style>

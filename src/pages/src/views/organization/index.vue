<template>
  <bk-loading class="organization-wrapper" :loading="state.isLoading">
    <div class="tree-wrapper user-scroll-y">
      <div class="tree-main">
        <bk-tree
          ref="treeRef"
          :data="state.treeData"
          node-key="id"
          label="name"
          children="children"
          :node-content-action="['selected', 'expand', 'click', 'collapse']"
          :selected="selectedId"
          @node-click="changeNode"
          @node-expand="changeNode"
        >
          <template #nodeAction="item">
            <span v-if="!item.__attr__.isRoot" style="color: #979ba5;">
              <DownShape class="h-[34px] mt-[4px]" v-if="item.has_children && item.__attr__.isOpen" />
              <RightShape class="h-[34px] mt-[4px]" v-if="item.has_children && !item.__attr__.isOpen" />
            </span>
          </template>
          <template #nodeType="item">
            <img class="img-logo" v-if="item.__attr__.isRoot && item.logo" :src="item.logo" />
            <span
              class="span-logo"
              v-else-if="item.__attr__.isRoot && !item.logo"
            >
              {{ item.name.charAt(0).toUpperCase() }}
            </span>
            <i class="bk-sq-icon icon-file-close" v-else />
          </template>
          <template #node="item">
            <span v-overflow-title>{{ item.name }}</span>
          </template>
          <template #nodeAppend="item">
            <span class="user-number"></span>
            <bk-dropdown
              trigger="click"
              placement="bottom-start"
              ref="dropdownMenu"
              @click.stop
            >
              <i class="user-icon icon-more"></i>
              <template #content>
                <bk-dropdown-menu>
                  <bk-dropdown-item
                    v-for="(child, index) in submenu"
                    :key="index"
                    @click="handleClick(child.type, item)">
                    {{ child.name }}
                  </bk-dropdown-item>
                </bk-dropdown-menu>
              </template>
            </bk-dropdown>
          </template>
        </bk-tree>
      </div>
    </div>
    <div class="organization-main">
      <header>
        <img class="img-logo" v-if="state.currentTenant.logo" :src="state.currentTenant.logo" />
        <span v-else class="span-logo">{{ convertLogo(state.currentTenant.name) }}</span>
        <span class="name">{{ state.currentTenant.name }}</span>
      </header>
      <bk-tab
        v-model:active="state.active"
        type="unborder-card"
        ext-cls="tab-details"
        @change="tabChange"
      >
        <bk-tab-panel
          v-for="(item, index) in panels"
          :key="item.name"
          :name="item.name"
          :label="item.label"
          :visible="item.isVisible"
        >
          <bk-loading :loading="state.tabLoading">
            <UserInfo
              v-if="index === 0"
              :user-data="state.currentUsers"
              :is-data-empty="state.isDataEmpty"
              :is-empty-search="state.isEmptySearch"
              :is-data-error="state.isDataError"
              :pagination="state.pagination"
              :keyword="params.keyword"
              :is-tenant="isTenant"
              @searchUsers="searchUsers"
              @changeUsers="changeUsers"
              @updatePageLimit="updatePageLimit"
              @updatePageCurrent="updatePageCurrent" />
            <DetailsInfo
              v-if="index === 1"
              :user-data="state.currentTenant"
              @updateTenantsList="initData" />
          </bk-loading>
        </bk-tab-panel>
      </bk-tab>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { overflowTitle } from 'bkui-vue';
import { DownShape, RightShape } from 'bkui-vue/lib/icon';
import { computed, inject, reactive, ref } from 'vue';

import DetailsInfo from './details/DetailsInfo.vue';
import UserInfo from './details/UserInfo.vue';

import {
  getTenantDepartments,
  getTenantDepartmentsList,
  getTenantOrganizationDetails,
  getTenantOrganizationList,
  getTenantUsersList,
} from '@/http/organizationFiles';
import { copy } from '@/utils';

const vOverflowTitle = overflowTitle;
const editLeaveBefore = inject('editLeaveBefore');

const treeRef = ref();
const state = reactive({
  isLoading: false,
  tabLoading: false,
  treeData: [],
  currentTenant: {},
  currentUsers: [],
  currentItem: {},
  active: 'user_info',
  isDataEmpty: false,
  isEmptySearch: false,
  isDataError: false,
  pagination: {
    current: 1,
    count: 0,
    limit: 10,
  },
});
const panels = reactive([
  { name: 'user_info', label: '人员信息', isVisible: true },
  { name: 'details_info', label: '详细信息', isVisible: true },
]);

const submenu = [
  {
    name: '复制组织ID',
    type: 'id',
  },
  {
    name: '复制组织名称',
    type: 'name',
  },
];

const params = reactive({
  id: '',
  keyword: '',
  page: 1,
  pageSize: 10,
  recursive: false,
});

const convertLogo = name => name?.charAt(0).toUpperCase();

const isTenant = computed(() => (!!state.currentItem.isRoot));

const initData = async () => {
  try {
    state.isLoading = true;
    const res = await getTenantOrganizationList();
    state.treeData = res.data;
    state.treeData.forEach((item, index) => {
      if (index === 0) {
        getTenantDetails(item.id);
        getTenantUsers(item.id);
        state.currentItem = item;
      }
      item.isRoot = true;
      item.children = item.departments;
      item.children.forEach((child) => {
        if (child.has_children) {
          child.children = [];
        }
      });
    });
  } catch (e) {
    console.log(e);
  } finally {
    state.isLoading = false;
  }
};
initData();

const changeNode = async (node) => {
  if (state.currentItem.id === node.id) return;
  state.currentItem = {
    id: node.id,
    name: node.name,
    managers: [],
  };
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
  state.tabLoading = true;
  params.keyword = '';
  if (node.isRoot) {
    panels[1].isVisible = true;
    state.active = 'user_info';
    // 切换租户
    await getTenantDetails(node.id);
    await getTenantUsers(node.id);
  } else {
    panels[1].isVisible = false;
    // 切换组织
    await getDepartmentsDetails(node);
    await getTenantDepartmentsUser(node.id);
  }
};

const selectedId = computed(() => `${state.currentItem.id}`);

const handleClick = (type, item) => {
  copy(item[type]);
};

const tabChange = (val) => {
  state.active = val;
};

const getTenantUsers = async (id) => {
  try {
    state.tabLoading = true;
    params.id = id;
    const data = { ...params };
    delete data.recursive;
    state.isDataEmpty = false;
    state.isEmptySearch = false;
    state.isDataError = false;
    const res = await getTenantUsersList(data);
    if (res.data.count === 0) {
      params.keyword === '' ? state.isDataEmpty = true : state.isEmptySearch = true;
    }
    state.pagination.count = res.data.count;
    state.currentUsers = res.data.results;
    state.tabLoading = false;
  } catch (e) {
    state.isDataError = true;
    state.tabLoading = false;
  } finally {
    state.tabLoading = false;
  }
};

const getTenantDetails = async (id: string) => {
  const res = await getTenantOrganizationDetails(id);
  state.pagination.count = res.data.managers.length;
  state.currentTenant = res.data;
  state.currentTenant.isRoot = true;
};

const getTenantDepartmentsUser = async (id) => {
  try {
    state.tabLoading = true;
    params.id = id;
    state.isDataEmpty = false;
    state.isEmptySearch = false;
    state.isDataError = false;
    const res = await getTenantDepartmentsList(params);
    if (res.data.count === 0) {
      params.keyword === '' ? state.isDataEmpty = true : state.isEmptySearch = true;
    }
    state.pagination.count = res.data.count;
    state.currentUsers = res.data.results;
    state.tabLoading = false;
  } catch (e) {
    state.isDataError = true;
  } finally {
    state.tabLoading = false;
  }
};

const getDepartmentsDetails = async (node) => {
  const res = await getTenantDepartments(node.id);
  state.currentTenant = res.data;
  node.children = res.data;
};
// 搜索人员信息
const searchUsers = (value: string) => {
  params.keyword = value;
  state.currentItem.isRoot ? getTenantUsers(state.currentItem.id) : getTenantDepartmentsUser(state.currentItem.id);
};
// 仅显示本级用户
const changeUsers = async (value: boolean) => {
  params.recursive = value;
  await getTenantDepartmentsUser(state.currentItem.id);
};
const updatePageLimit = async (limit) => {
  state.pagination.limit = limit;
  params.pageSize = limit;
  await getTenantDepartmentsUser(state.currentItem.id);
};
const updatePageCurrent = async (current) => {
  state.pagination.current = current;
  params.page = current;
  await getTenantDepartmentsUser(state.currentItem.id);
};
</script>

<style lang="less" scoped>
@import url("./tree.less");

.organization-wrapper {
  display: flex;
  width: 100%;
  height: calc(100vh - 52px);

  .organization-main {
    height: calc(100% - 52px);

    header {
      display: flex;
      height: 52px;
      padding: 0 24px;
      line-height: 52px;
      background-color: #fff;
      align-items: center;

      .name {
        font-size: 16px;
        color: #313238;
      }
    }
  }
}

:deep(.tab-details) {
  height: calc(100vh - 104px);

  .bk-tab-header {
    font-size: 14px;
    line-height: 36px !important;
    background: #fff;
    border-bottom: none;
    box-shadow: 0 3px 4px 0 rgb(0 0 0 / 4%);

    .bk-tab-header-item {
      padding: 0 5px !important;
      margin: 0 20px;
    }
  }

  .bk-tab-content {
    padding: 0;
  }
}
</style>

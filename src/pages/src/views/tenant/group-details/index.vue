<template>
  <div class="group-details-wrapper user-scroll-y">
    <div class="main-content">
      <div class="content-search">
        <div class="content-search-left">
          <bk-button class="mr-[24px]" theme="primary" @click="handleClick('add')">
            <i class="user-icon icon-add-2 mr8" />
            新建租户
          </bk-button>
          <!-- <bk-switcher
            v-model="demo"
            theme="primary"
            size="large"
          />
          <span class="switcher-text">租户名是否跨租户可见</span> -->
        </div>
        <bk-input
          class="content-search-input"
          v-model="searchName"
          placeholder="搜索租户名"
          type="search"
          clearable
          @enter="handleEnter"
          @clear="fetchTenantsList"
        />
      </div>
      <bk-loading :loading="state.tableLoading">
        <bk-table
          class="content-table"
          :data="state.list"
          :max-height="tableMaxHeight"
          show-overflow-tooltip>
          <template #empty>
            <Empty
              :is-data-empty="state.isTableDataEmpty"
              :is-search-empty="state.isEmptySearch"
              :is-data-error="state.isTableDataError"
              @handleEmpty="fetchTenantsList"
              @handleUpdate="fetchTenantsList"
            />
          </template>
          <bk-table-column
            prop="name"
            label="租户名"
            :sort="{ value: 'asc' }">
            <template #default="{ row, index }">
              <div class="item-name">
                <img v-if="row.logo" class="img-logo" :src="row.logo" />
                <span v-else class="span-logo" :style="`background-color: ${LOGO_COLOR[index]}`">
                  {{ logoConvert(row.name) }}
                </span>
                <bk-button
                  text
                  theme="primary"
                  @click="handleClick('view', row)"
                >
                  {{ row.name }}
                </bk-button>
                <img v-if="row.new" class="icon-new" src="@/images/new.svg" alt="">
              </div>
            </template>
          </bk-table-column>
          <bk-table-column prop="id" label="租户ID"></bk-table-column>
          <bk-table-column prop="managers" label="租户管理员">
            <template #default="{ row }">
              <bk-tag v-for="(item, index) in row.managers" :key="index">{{ item.username }}</bk-tag>
            </template>
          </bk-table-column>
          <bk-table-column prop="data_sources" label="已绑定数据源">
            <template #default="{ row }">
              <span>{{ formatConvert(row.data_sources) }}</span>
            </template>
          </bk-table-column>
          <bk-table-column prop="created_at" label="创建时间" :sort="true" />
          <bk-table-column label="操作">
            <template #default="{ row }">
              <bk-button
                text
                theme="primary"
                style="margin-right: 8px;"
                @click="handleClick('edit', row)"
              >
                编辑
              </bk-button>
            </template>
          </bk-table-column>
        </bk-table>
      </bk-loading>
    </div>
    <bk-sideslider
      :ext-cls="['details-wrapper', { 'details-edit-wrapper': !isView }]"
      :width="isView ? 640 : 960"
      :is-show="detailsConfig.isShow"
      :title="detailsConfig.title"
      :before-close="handleBeforeClose"
      quick-close
    >
      <template #header>
        <span>{{ detailsConfig.title }}</span>
        <div v-if="isView">
          <bk-button
            outline
            theme="primary"
            @click="handleClick('edit', state.tenantsData)"
          >编辑</bk-button
          >
        </div>
      </template>
      <template #default>
        <ViewDetails v-if="isView" :tenants-data="state.tenantsData" />
        <OperationDetails
          v-else
          :type="detailsConfig.type"
          :tenants-data="state.tenantsData"
          @handleCancelEdit="handleCancelEdit"
          @updateTenantsList="updateTenantsList"
        />
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, inject, reactive, ref, watch } from 'vue';

import OperationDetails from './OperationDetails.vue';
import ViewDetails from './ViewDetails.vue';

import Empty from '@/components/Empty.vue';
import { useTableMaxHeight } from '@/hooks/useTableMaxHeight';
import { getDefaultConfig } from '@/http/dataSourceFiles';
import {
  getTenantDetails,
  getTenants,
  searchTenants,
} from '@/http/tenantsFiles';
import { useMainViewStore } from '@/store/mainView';
import { formatConvert, LOGO_COLOR, logoConvert } from '@/utils';

const store = useMainViewStore();
store.customBreadcrumbs = false;

const tableMaxHeight = useTableMaxHeight(202);
const editLeaveBefore = inject('editLeaveBefore');
const searchName = ref('');
const state = reactive({
  list: [],
  tableLoading: true,
  // 搜索结果为空
  isEmptySearch: false,
  // 表格请求出错
  isTableDataError: false,
  // 表格请求结果为空
  isTableDataEmpty: false,
  // 租户详情数据
  tenantsData: {
    name: '',
    id: '',
    feature_flags: {
      user_number_visible: true,
    },
    logo: '',
    managers: [
      {
        username: '',
        full_name: '',
        email: '',
        phone: '',
        phone_country_code: '86',
        error: false,
      },
    ],
    password_initial_config: {},
  },
});
const detailsConfig = reactive({
  isShow: false,
  title: '',
  type: '',
});
const enumData = {
  view: {
    title: '租户详情',
    type: 'view',
  },
  add: {
    title: '新建租户',
    type: 'add',
  },
  edit: {
    title: '编辑租户',
    type: 'edit',
  },
};

watch(
  () => detailsConfig.isShow,
  () => {
    if (!detailsConfig.isShow) {
      state.tenantsData = {
        name: '',
        id: '',
        feature_flags: {
          user_number_visible: true,
        },
        logo: '',
        managers: [
          {
            username: '',
            full_name: '',
            email: '',
            phone: '',
            phone_country_code: '86',
            error: false,
          },
        ],
        password_initial_config: {},
      };
    }
  },
);

const isView = computed(() => detailsConfig.type === 'view');
const currentTenantId = ref('');

const handleClick = async (type: string, item?: any) => {
  if (type !== 'add') {
    const res = await getTenantDetails(item.id);
    state.tenantsData = res.data;
    currentTenantId.value = item.id;
  } else {
    const res = await getDefaultConfig('local');
    state.tenantsData.password_initial_config = res.data.config.password_initial;
  }
  detailsConfig.title = enumData[type].title;
  detailsConfig.type = enumData[type].type;
  detailsConfig.isShow = true;
};

const handleCancelEdit = async () => {
  window.changeInput = false;
  if (detailsConfig.type === 'add') {
    detailsConfig.isShow = false;
  } else {
    const res = await getTenantDetails(currentTenantId.value);
    state.tenantsData = res.data;
    detailsConfig.type = 'view';
    detailsConfig.title = '租户详情';
    window.changeInput = false;
  }
};
// 获取租户列表
const fetchTenantsList = () => {
  searchName.value = '';
  state.tableLoading = true;
  state.isTableDataEmpty = false;
  state.isEmptySearch = false;
  state.isTableDataError = false;
  getTenants()
    .then((res: any) => {
      if (res.data.length === 0) {
        state.isTableDataEmpty = true;
      }

      const newDate = new Date().getTime(); // 当前时间
      res.data.forEach((item) => {
        const createdDate = new Date(item.created_at).getTime();
        // 相差天数
        item.new = Math.floor((newDate - createdDate) / (24 * 3600 * 1000)) <= 1;
      });

      state.list = res.data.sort((a, b) => a.name.localeCompare(b.name, 'zh-Hans-CN'));
      state.tableLoading = false;
    })
    .catch(() => {
      state.isTableDataError = true;
      state.tableLoading = false;
    });
};
// 初始化加载
fetchTenantsList();
// 搜索租户列表
const handleEnter = () => {
  state.tableLoading = true;
  searchTenants(searchName.value)
    .then((res: any) => {
      if (res.data.length === 0) {
        state.isEmptySearch = true;
      }
      state.list = res.data;
      state.tableLoading = false;
    })
    .catch(() => {
      state.isTableDataError = true;
      state.tableLoading = false;
    });
};
// 更新租户列表
const updateTenantsList = (text) => {
  detailsConfig.isShow = false;
  window.changeInput = false;
  fetchTenantsList();
  Message({
    theme: 'success',
    message: text,
  });
};

const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    detailsConfig.isShow = false;
  } else {
    detailsConfig.isShow = false;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};
</script>

<style lang="less" scoped>
.group-details-wrapper {
  width: 100%;
  height: calc(100vh - 104px);
  padding: 24px;

  .main-content {
    .content-search {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      .content-search-left {
        display: flex;
        align-items: center;

        .switcher-text {
          margin-left: 12px;
          font-size: 14px;
          color: #313238;
        }
      }

      .content-search-input {
        width: 400px;
      }
    }

    :deep(.bk-table) {
      .item-name {
        display: flex;
        align-items: center;
        height: 42px;
        line-height: 42px;

        .icon-new {
          width: 26px;
          margin-left: 8px;
        }
      }
    }
  }
}

.details-wrapper {
  :deep(.bk-sideslider-title) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px 0 50px !important;

    .bk-button {
      padding: 5px 17px !important;
    }
  }
}

.details-edit-wrapper {
  :deep(.bk-modal-content) {
    height: calc(100vh - 106px);
    background: #f5f7fa;

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
